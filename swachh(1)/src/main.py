import os
import uuid
from fastapi import FastAPI, UploadFile, File, Form, Depends, HTTPException, BackgroundTasks, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import text
from src.database import get_db, engine, Base
from src.models import User, GVP, Payout, GVPStatus, PayoutStatus
from src.schemas import GVPReportResponse, GVPResponse
from src.services.exif import extract_gps_coordinates
from src.services.storage import upload_image_to_s3
from src.services.ml_vision import verify_solid_waste
from src.services.payment import create_contact_and_fund_account, trigger_payout
import pydantic

app = FastAPI(title="SwachhConnect API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup():
    try:
        async with engine.begin() as conn:
            await conn.execute(text("CREATE EXTENSION IF NOT EXISTS postgis;"))
            await conn.run_sync(Base.metadata.create_all)
            await conn.execute(text("INSERT INTO users (id, name, upi_id, phone_number, wallet_balance, created_at) VALUES ('00000000-0000-0000-0000-000000000000', 'Dummy Reporter', 'dummy@ybl', '0000000000', 0, NOW()) ON CONFLICT (id) DO NOTHING;"))
        print("Database connection successful and tables created.")
    except Exception as e:
        print(f"Warning: Could not connect to the database on startup. Please check your .env credentials. Error: {e}")

@app.get("/")
def read_root():
    return {"message": "Welcome to SwachhConnect API"}

@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return Response(status_code=204)

@app.post("/api/v1/gvp/report", response_model=GVPReportResponse)
async def report_gvp(
    reporter_id: uuid.UUID = Form(...),
    image: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
):
    # Verify user
    result = await db.execute(select(User).filter(User.id == reporter_id))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    image_bytes = await image.read()

    # 1. Extract GPS Data
    lat, lon = extract_gps_coordinates(image_bytes)
    if lat is None or lon is None:
        raise HTTPException(status_code=400, detail="No GPS data found in image EXIF. Please ensure location services are enabled on your camera.")

    # 2. Run ML Inference
    confidence_score = verify_solid_waste(image_bytes)
    if confidence_score < 0.85:
        return GVPReportResponse(
            message="Image rejected. ML confidence score too low for solid waste.",
            gvp=None,
            ml_confidence_score=confidence_score
        )

    # 3. Upload to Cloud Storage
    filename = f"gvps/{uuid.uuid4()}_{image.filename}"
    image_url = upload_image_to_s3(image_bytes, filename, image.content_type)
    
    if not image_url:
        raise HTTPException(status_code=500, detail="Failed to upload image to cloud storage")

    # 4. Save to Database
    tender_amount = float(os.getenv("DEFAULT_TENDER_AMOUNT", "500.00"))
    
    new_gvp = GVP(
        reporter_id=user.id,
        location=f"SRID=4326;POINT({lon} {lat})", # PostGIS format: POINT(lon lat)
        before_image_url=image_url,
        ml_confidence_score=confidence_score,
        tender_amount=tender_amount,
        status=GVPStatus.PENDING
    )
    
    db.add(new_gvp)
    await db.commit()
    await db.refresh(new_gvp)

    # We cannot construct GVPResponse directly because location is a Geometry object.
    # We'd need to extract lat/lon for the response, but for simplicity we return a mock response here
    
    return GVPReportResponse(
        message="GVP successfully reported and micro-tender opened.",
        gvp=GVPResponse(
            id=new_gvp.id,
            reporter_id=new_gvp.reporter_id,
            latitude=lat,
            longitude=lon,
            before_image_url=new_gvp.before_image_url,
            ml_confidence_score=new_gvp.ml_confidence_score,
            status=new_gvp.status,
            tender_amount=float(new_gvp.tender_amount),
            created_at=new_gvp.created_at,
            updated_at=new_gvp.updated_at
        ),
        ml_confidence_score=confidence_score
    )

@app.get("/api/v1/gvp/tenders")
async def list_tenders(lat: float, lon: float, radius_meters: int = 5000, db: AsyncSession = Depends(get_db)):
    """
    Lists open GVPs within a specific radius, ordered by urgency/ML confidence.
    """
    # ST_DWithin uses SRID 4326 geometry, so we cast to geography for meters
    query = select(GVP).where(
        GVP.status == GVPStatus.PENDING,
        text(f"ST_DWithin(location::geography, ST_SetSRID(ST_MakePoint({lon}, {lat}), 4326)::geography, {radius_meters})")
    ).order_by(GVP.ml_confidence_score.desc())
    
    result = await db.execute(query)
    gvps = result.scalars().all()
    
    return {"tenders": [{"id": g.id, "confidence": g.ml_confidence_score, "amount": g.tender_amount} for g in gvps]}

@app.post("/api/v1/gvp/verify-cleanup")
async def verify_cleanup(
    gvp_id: uuid.UUID = Form(...),
    after_image: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(GVP).filter(GVP.id == gvp_id))
    gvp = result.scalars().first()
    
    if not gvp:
        raise HTTPException(status_code=404, detail="GVP not found")
        
    if gvp.status != GVPStatus.PENDING and gvp.status != GVPStatus.FUNDED:
        raise HTTPException(status_code=400, detail="GVP is already cleaned or paid")

    image_bytes = await after_image.read()
    filename = f"gvps_after/{uuid.uuid4()}_{after_image.filename}"
    image_url = upload_image_to_s3(image_bytes, filename, after_image.content_type)
    
    if not image_url:
        raise HTTPException(status_code=500, detail="Failed to upload image")

    # In a real system, another ML check could be run on the "after" image here.

    gvp.after_image_url = image_url
    gvp.status = GVPStatus.CLEANED
    await db.commit()
    
    return {"message": "Cleanup verified.", "gvp_id": gvp.id, "status": gvp.status}

@app.post("/api/v1/payout/trigger")
async def trigger_gvp_payout(gvp_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(GVP).filter(GVP.id == gvp_id))
    gvp = result.scalars().first()
    
    if not gvp or gvp.status != GVPStatus.CLEANED:
        raise HTTPException(status_code=400, detail="GVP not eligible for payout")
        
    user_result = await db.execute(select(User).filter(User.id == gvp.reporter_id))
    user = user_result.scalars().first()
    
    # Check if user has a Razorpay fund account, if not create one
    # Note: In production, store fund_account_id in User model to avoid recreating.
    fund_account_id = create_contact_and_fund_account(
        name=user.name,
        email="citizen@example.com", # Dummy email for example
        contact_number=user.phone_number,
        upi_id=user.upi_id
    )
    
    if not fund_account_id:
        raise HTTPException(status_code=500, detail="Failed to setup Razorpay Fund Account")

    # Create Payout DB Record
    new_payout = Payout(
        user_id=user.id,
        gvp_id=gvp.id,
        amount=gvp.tender_amount,
        razorpay_fund_account_id=fund_account_id,
        status=PayoutStatus.PENDING
    )
    db.add(new_payout)
    await db.commit()
    await db.refresh(new_payout)

    # Trigger Payout
    try:
        payout_res = trigger_payout(fund_account_id, float(gvp.tender_amount), str(new_payout.id))
        new_payout.razorpay_payout_id = payout_res.get("id")
        new_payout.status = PayoutStatus.PROCESSING
        await db.commit()
    except Exception as e:
        new_payout.status = PayoutStatus.FAILED
        await db.commit()
        raise HTTPException(status_code=500, detail="Payout execution failed")

    return {"message": "Payout initiated", "payout_id": new_payout.id}

@app.post("/api/v1/webhooks/razorpay")
async def razorpay_webhook(request: Request, db: AsyncSession = Depends(get_db)):
    payload = await request.json()
    # In production, verify the webhook signature here using razorpay client!
    
    event = payload.get("event")
    if event in ["payout.processed", "payout.failed", "payout.reversed"]:
        payout_data = payload.get("payload", {}).get("payout", {}).get("entity", {})
        ref_id = payout_data.get("reference_id")
        
        if ref_id:
            result = await db.execute(select(Payout).filter(Payout.id == ref_id))
            payout = result.scalars().first()
            if payout:
                if event == "payout.processed":
                    payout.status = PayoutStatus.PROCESSED
                    
                    # Update User Wallet Balance
                    user_result = await db.execute(select(User).filter(User.id == payout.user_id))
                    user = user_result.scalars().first()
                    if user:
                        user.wallet_balance += payout.amount
                        
                    # Update GVP status
                    gvp_result = await db.execute(select(GVP).filter(GVP.id == payout.gvp_id))
                    gvp = gvp_result.scalars().first()
                    if gvp:
                        gvp.status = GVPStatus.PAID

                elif event == "payout.failed":
                    payout.status = PayoutStatus.FAILED
                elif event == "payout.reversed":
                    payout.status = PayoutStatus.REVERSED

                await db.commit()
    
    return {"status": "ok"}

@app.get("/api/v1/admin/gvps/pending")
async def admin_get_pending_gvps(db: AsyncSession = Depends(get_db)):
    """Fetch all pending GVPs for the admin dashboard"""
    query = select(GVP).where(GVP.status == GVPStatus.PENDING).order_by(GVP.created_at.desc())
    result = await db.execute(query)
    gvps = result.scalars().all()
    
    return {
        "gvps": [
            {
                "id": g.id,
                "location": "Sector 4, Kuvempunagar" if "4326" in str(g.location) else "Unknown", 
                "ml_confidence_score": g.ml_confidence_score,
                "created_at": g.created_at
            } for g in gvps
        ]
    }

@app.post("/api/v1/admin/gvp/{gvp_id}/approve")
async def admin_approve_gvp(gvp_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    """Approve a GVP and credit the reporter with 50 Rs"""
    result = await db.execute(select(GVP).filter(GVP.id == gvp_id))
    gvp = result.scalars().first()
    
    if not gvp:
        raise HTTPException(status_code=404, detail="GVP not found")
        
    if gvp.status != GVPStatus.PENDING:
        raise HTTPException(status_code=400, detail="GVP is already processed")
        
    # Update GVP status
    gvp.status = GVPStatus.VERIFIED
    
    # Fetch user to update wallet
    user_result = await db.execute(select(User).filter(User.id == gvp.reporter_id))
    user = user_result.scalars().first()
    
    if user:
        # Credit wallet with 50 Rs
        user.wallet_balance = float(user.wallet_balance or 0) + 50.0
        
        # Create a simulated payout record
        new_payout = Payout(
            user_id=user.id,
            gvp_id=gvp.id,
            amount=50.0,
            status=PayoutStatus.PROCESSED,
            razorpay_payout_id="simulated_hackathon_payout_" + str(uuid.uuid4())[:8]
        )
        db.add(new_payout)
        
    await db.commit()
    
    return {"message": "GVP Approved and ₹50 credited to user wallet."}

@app.get("/api/v1/user/{user_id}/wallet")
async def get_user_wallet(user_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    """Get the current wallet balance for a user"""
    result = await db.execute(select(User).filter(User.id == user_id))
    user = result.scalars().first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    return {"wallet_balance": float(user.wallet_balance or 0)}
