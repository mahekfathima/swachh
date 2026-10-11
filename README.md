<div align="center">

# 🌱 SwachhConnect

### *Decentralized AI-Driven Civic Waste Detection, PostGIS Micro-Tendering & Instant UPI Rewards*

[![FastAPI](https://img.shields.io/badge/FastAPI-0.111.0-009688.svg?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Next.js](https://img.shields.io/badge/Next.js-16.2.7-black.svg?style=for-the-badge&logo=next.js&logoColor=white)](https://nextjs.org)
[![React](https://img.shields.io/badge/React-19.2.4-61DAFB.svg?style=for-the-badge&logo=react&logoColor=black)](https://react.dev)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.0-3178C6.svg?style=for-the-badge&logo=typescript&logoColor=white)](https://www.typescriptlang.org)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-PostGIS-336791.svg?style=for-the-badge&logo=postgresql&logoColor=white)](https://postgis.net)
[![PyTorch](https://img.shields.io/badge/PyTorch-2.3.0-EE4C2C.svg?style=for-the-badge&logo=pytorch&logoColor=white)](https://pytorch.org)
[![RazorpayX](https://img.shields.io/badge/RazorpayX-Instant_UPI-0C2340.svg?style=for-the-badge&logo=razorpay&logoColor=white)](https://razorpay.com/x/)
[![TailwindCSS](https://img.shields.io/badge/Tailwind_CSS-v4-38B2AC.svg?style=for-the-badge&logo=tailwind-css&logoColor=white)](https://tailwindcss.com)

<p align="center">
  <b>"See Trash? Turn it into Cash."</b><br>
  Transforming Garbage Vulnerable Points (GVPs) into verified civic micro-tenders using computer vision, geospatial indexing, and real-time UPI disbursements.
</p>

---

</div>

## 📌 Table of Contents

- [Overview & Problem Statement](#-overview--problem-statement)
- [Key Features](#-key-features)
- [System Architecture](#-system-architecture)
- [Technology Stack](#-technology-stack)
- [Database Schema & Data Models](#-database-schema--data-models)
- [API Reference](#-api-reference)
- [Directory Structure](#-directory-structure)
- [Getting Started](#-getting-started)
  - [Prerequisites](#prerequisites)
  - [Backend Setup](#1-backend-setup-fastapi)
  - [Database Initialization](#2-database-initialization-postgresql--postgis)
  - [Frontend Setup](#3-frontend-setup-nextjs--react-19)
- [Environment Variables](#-environment-variables)
- [Walkthrough & Demo Flow](#-walkthrough--demo-flow)
- [Security & Anti-Fraud Measures](#-security--anti-fraud-measures)
- [Roadmap](#-roadmap)
- [License & Acknowledgments](#-license--acknowledgments)

---

## 🎯 Overview & Problem Statement

Urban centers across India and the developing world face rampant accumulation of **Garbage Vulnerable Points (GVPs)** — illegal dump sites that resurface repeatedly despite municipal sanitation efforts.

### The Traditional Dilemma:
1. **Reporting Friction**: Citizens have zero incentive to report littering, and municipal portals are slow, bureaucratic, and unresponsive.
2. **Lack of Trust & Verification**: Manual complaint validation wastes municipal workforce hours on bogus or duplicate claims.
3. **Delayed Action & Opacity**: Local sanitation workers lack visibility into neighborhood hot-spots, and corporate CSR waste cleanup funds remain trapped in administrative pipelines.

### The SwachhConnect Solution:
**SwachhConnect** bridges citizens, local sanitation contractors, and corporate CSR/municipal funds into an automated, closed-loop civic ecosystem:
- **📸 Citizen Crowdsourcing**: Citizens take a photo of an illegal dump site.
- **📍 Anti-Spoof Geotagging**: Automated EXIF extraction captures hardware GPS coordinates directly from the image data.
- **🧠 AI Waste Verification**: A deep learning computer vision model (PyTorch + TorchVision) validates the presence of solid waste with confidence scoring ($\ge 85\%$).
- **🗺️ PostGIS Micro-Tendering**: Accepted GVPs open automated spatial micro-tenders available to nearby sanitation teams within a defined radius (`ST_DWithin`).
- **⚡ Instant UPI Payouts**: Verified cleanups or approved reports trigger instant rewards directly to the citizen's UPI VPA via RazorpayX.

---

## ✨ Key Features

| Feature | Description |
| :--- | :--- |
| **📸 Camera Snap & EXIF Geotagging** | Hardware-level GPS metadata (`WGS84 lat/long`) is extracted directly from the uploaded photo’s EXIF tags to prevent geolocation spoofing. Features automatic fallback coordinates (`12.2958, 76.6394` — Mysuru) for demo and web browser uploads. |
| **🧠 Deep Learning Waste Classifier** | PyTorch-powered image preprocessing (`Resize 224x224`, `ToTensor`, `Normalize`) and solid waste inference. Low-confidence images are rejected instantly before database insertion. Extended integration available for Gemini AI Vision. |
| **🗺️ Geospatial Micro-Tender Engine** | Employs PostgreSQL with **PostGIS** spatial indexing (`SRID=4326`, `POINT(lon lat)`). Allows querying open tenders within an arbitrary radius (`radius_meters`, e.g., 5,000m) using `ST_DWithin` on geodetic spheres. |
| **💸 RazorpayX Instant UPI Disbursements** | Programmatically creates contacts and UPI Fund Accounts (`vpa`). Triggers automated, real-time payouts with background webhooks listening to `payout.processed`, `payout.failed`, and `payout.reversed`. |
| **📱 Cyberpunk Citizen Web App** | Mobile-first Next.js 16 / React 19 interface with dark cyberpunk styling, live wallet balance polling, camera shutter interaction, holographic laser scanning animation (`LoadingScanning`), and community activity feeds. |
| **🛰️ Municipal Command Center** | Real-time administrative dashboard equipped with Esri World Imagery satellite map telemetry (via Leaflet), live radar sweeps, animated counter telemetry, and one-click **"Verify & Dispatch Tender"** actions. |

---

## 🏛️ System Architecture

```mermaid
flowchart TD
    subgraph Client Layer
        A[Citizen Mobile App<br/>Next.js 16 / React 19] -->|1. Upload Photo| B[FastAPI Backend Server]
        Admin[Municipal Command Center<br/>Admin Telemetry] -->|Review & Approve| B
    end

    subgraph Processing & AI
        B -->|2. Extract Lat/Long| C[EXIF Parser<br/>PIL.ExifTags]
        B -->|3. Run Inference| D[ML Vision Engine<br/>PyTorch / TorchVision]
        B -->|4. Push Media| E[Media Cloud Storage<br/>Cloudinary / AWS S3]
    end

    subgraph Data & Geospatial
        B -->|5. Store GVP & Spatial Point| F[(PostgreSQL + PostGIS<br/>SRID 4326 / asyncpg)]
        Admin -->|Fetch Detections & Radius Search| F
    end

    subgraph FinTech Settlement
        Admin -->|Approve Report| B
        B -->|6. Trigger Payout| G[RazorpayX Payouts API]
        G -->|7. UPI Instant Transfer| H[Citizen Bank Account / VPA]
        G -->|8. Webhook Notification| B
        B -->|9. Update Wallet Balance| F
    end
```

---

## 🛠️ Technology Stack

### **Backend & Core Services**
- **Language**: Python 3.10+ / 3.11+
- **Framework**: [FastAPI](https://fastapi.tiangolo.com/) (Asynchronous, High-Performance REST API)
- **ASGI Server**: [Uvicorn](https://www.uvicorn.org/) (Standard workers)
- **Database ORM**: [SQLAlchemy 2.0](https://www.sqlalchemy.org/) (Async Engine & Declarative Mapping)
- **Spatial Extension**: [GeoAlchemy 2](https://geoalchemy-2.readthedocs.io/) & [asyncpg](https://github.com/MagicStack/asyncpg)
- **Data Validation**: [Pydantic v2](https://docs.pydantic.dev/) & `pydantic-settings`
- **Computer Vision**: [PyTorch](https://pytorch.org/), [TorchVision](https://pytorch.org/vision/), [Pillow (PIL)](https://python-pillow.org/)
- **FinTech / Payouts**: [Razorpay](https://razorpay.com/) & RazorpayX Payouts API
- **Media Storage**: [Cloudinary](https://cloudinary.com/) (SHA-1 signed multipart upload) & [AWS S3](https://aws.amazon.com/s3/) (`boto3`)

### **Frontend & User Experience**
- **Framework**: [Next.js 16](https://nextjs.org/) (React 19, App Router)
- **Language**: TypeScript 5.0
- **Styling**: [Tailwind CSS v4](https://tailwindcss.com/)
- **Animations**: [Framer Motion](https://www.framer.com/motion/)
- **GIS Mapping**: [Leaflet](https://leafletjs.com/) & [React-Leaflet](https://react-leaflet.js.org/) with Esri World Imagery satellite tiles
- **Icons**: [Lucide React](https://lucide.dev/)

### **Database & Infrastructure**
- **Database**: [PostgreSQL](https://www.postgresql.org/) with `PostGIS` extension enabled (Compatible with [Supabase](https://supabase.com/))
- **Environment Management**: `python-dotenv` & `.env`

---

## 🗄️ Database Schema & Data Models

The system architecture is structured around three primary relational entities:

```mermaid
erDiagram
    USERS ||--o{ GVPS : reports
    USERS ||--o{ PAYOUTS : receives
    GVPS ||--o{ PAYOUTS : triggers

    USERS {
        uuid id PK
        string name
        string upi_id UK
        string phone_number UK
        numeric wallet_balance
        datetime created_at
    }

    GVPS {
        uuid id PK
        uuid reporter_id FK
        geometry location "POINT(SRID=4326)"
        string before_image_url
        string after_image_url
        float ml_confidence_score
        enum status "PENDING, VERIFIED, FUNDED, CLEANED, PAID"
        uuid corporate_sponsor_id
        numeric tender_amount
        datetime created_at
        datetime updated_at
    }

    PAYOUTS {
        uuid id PK
        uuid user_id FK
        uuid gvp_id FK
        numeric amount
        string razorpay_fund_account_id
        string razorpay_payout_id UK
        enum status "PENDING, PROCESSING, PROCESSED, FAILED, REVERSED"
        datetime timestamp
    }
```

---

## 🔌 API Reference

Base URL: `http://localhost:8000`  
Interactive Swagger Docs: `http://localhost:8000/docs`  
ReDoc: `http://localhost:8000/redoc`

### **1. Citizen & Reporting Endpoints**

#### `POST /api/v1/gvp/report`
Submits a newly photographed Garbage Vulnerable Point.
- **Content-Type**: `multipart/form-data`
- **Request Body**:
  - `reporter_id` (`UUID`, required): ID of the reporting citizen.
  - `image` (`File`, required): Image file with GPS EXIF metadata.
- **Workflow**:
  1. Validates reporter existence in database.
  2. Extracts GPS coordinates from EXIF tags (`GPSLatitude`, `GPSLongitude`).
  3. Executes ML Vision model. Rejects if `confidence_score < 0.85`.
  4. Uploads image to Cloud Storage.
  5. Inserts spatial `POINT(lon lat)` with `SRID=4326` into PostGIS.
- **Response (`200 OK`)**:
  ```json
  {
    "message": "GVP successfully reported and micro-tender opened.",
    "gvp": {
      "id": "e3b0c442-98fc-1c14-9af0-2a3b9566963e",
      "reporter_id": "00000000-0000-0000-0000-000000000000",
      "latitude": 12.2958,
      "longitude": 76.6394,
      "before_image_url": "https://res.cloudinary.com/.../gvps/image.jpg",
      "after_image_url": null,
      "ml_confidence_score": 0.92,
      "status": "PENDING",
      "tender_amount": 50.0,
      "created_at": "2026-10-10T23:30:00Z",
      "updated_at": "2026-10-10T23:30:00Z"
    },
    "ml_confidence_score": 0.92
  }
  ```

#### `GET /api/v1/user/{user_id}/wallet`
Fetches the current live reward balance for a citizen.
- **Response**: `{"wallet_balance": 150.0}`

---

### **2. Micro-Tenders & Resolution Endpoints**

#### `GET /api/v1/gvp/tenders`
Discovers open tenders within a geographic radius using PostGIS `ST_DWithin`.
- **Query Parameters**:
  - `lat` (`float`): Center latitude.
  - `lon` (`float`): Center longitude.
  - `radius_meters` (`int`, optional, default: `5000`): Search radius in meters.
- **Response**:
  ```json
  {
    "tenders": [
      {
        "id": "e3b0c442-98fc-1c14-9af0-2a3b9566963e",
        "confidence": 0.92,
        "amount": 50.0
      }
    ]
  }
  ```

#### `POST /api/v1/gvp/verify-cleanup`
Uploads post-cleanup proof-of-work image to advance the GVP to `CLEANED`.
- **Content-Type**: `multipart/form-data`
- **Request Body**: `gvp_id` (`UUID`), `after_image` (`File`).

---

### **3. Admin & Command Center Endpoints**

#### `GET /api/v1/admin/gvps/pending`
Retrieves all pending GVP detections for display on the Admin Telemetry Radar.
- **Response**:
  ```json
  {
    "gvps": [
      {
        "id": "e3b0c442-98fc-1c14-9af0-2a3b9566963e",
        "location": "Sector 4, Kuvempunagar",
        "ml_confidence_score": 0.92,
        "created_at": "2026-10-10T23:30:00Z"
      }
    ]
  }
  ```

#### `POST /api/v1/admin/gvp/{gvp_id}/approve`
Approves the detection, transitions status to `VERIFIED`, and automatically credits ₹50 to the citizen's wallet.
- **Response**: `{"message": "GVP Approved and ₹50 credited to user wallet."}`

---

### **4. FinTech Payouts & Webhooks**

#### `POST /api/v1/payout/trigger?gvp_id={id}`
Creates a Razorpay Contact, generates a UPI Fund Account (`vpa`), and triggers a payout via RazorpayX.

#### `POST /api/v1/webhooks/razorpay`
Asynchronous webhook listener handling events:
- `payout.processed` $\rightarrow$ Marks payout as `PROCESSED`, credits citizen wallet balance, sets GVP status to `PAID`.
- `payout.failed` $\rightarrow$ Sets payout status to `FAILED`.
- `payout.reversed` $\rightarrow$ Sets payout status to `REVERSED`.

---

## 📂 Directory Structure

```plaintext
swachh/
├── .env                          # Local environment variables (git-ignored)
├── .env.example                  # Environment configuration template
├── requirements.txt              # Backend Python dependencies
├── test_db.py                    # Standalone PostGIS database connection test script
│
├── src/                          # FastAPI Backend Application
│   ├── database.py               # Async SQLAlchemy engine & session factory
│   ├── main.py                   # FastAPI route definitions & lifecycle events
│   ├── models.py                 # SQLAlchemy relational & GeoAlchemy2 models
│   ├── schemas.py                # Pydantic v2 validation schemas
│   └── services/
│       ├── exif.py               # EXIF metadata parser & GPS coordinate extractor
│       ├── ml_vision.py          # PyTorch image transformation & waste detector
│       ├── payment.py            # Razorpay / RazorpayX Payout & Contact integration
│       └── storage.py            # Cloudinary & AWS S3 upload service
│
└── frontend/                     # Next.js 16 / React 19 Frontend Application
    ├── package.json              # Frontend scripts & dependencies
    ├── tsconfig.json             # TypeScript configuration
    ├── .env.example              # Frontend environment template
    ├── public/
    │   └── logo.jpeg             # Official SwachhConnect branding logo
    └── src/
        ├── app/
        │   ├── layout.tsx        # Root HTML layout & font definitions
        │   ├── page.tsx          # Citizen Mobile App (Camera, Scanning, Live Feed)
        │   ├── login/
        │   │   └── page.tsx      # Mock Civic Authentication portal
        │   └── admin/
        │       └── page.tsx      # Municipal Command Center (Radar, Telemetry Map)
        ├── components/
        │   ├── LiveMap.tsx       # Leaflet & Esri World Imagery satellite map
        │   ├── StatCard.tsx      # Glassmorphic telemetry stat card
        │   └── ui/
        │       └── LoadingScanning.tsx # Holographic laser scanning animation
        └── lib/
            └── api.ts            # Typed client API integration service
```

---

## 🚀 Getting Started

Follow the steps below to run both the backend and frontend services locally.

### Prerequisites
Make sure you have the following installed on your machine:
- **Python**: `3.10` or higher ([python.org](https://www.python.org/))
- **Node.js**: `18.18+` or `20+` ([nodejs.org](https://nodejs.org/))
- **PostgreSQL**: Version 14+ with the **PostGIS** extension enabled (or an instance on [Supabase](https://supabase.com/))

---

### 1. Backend Setup (FastAPI)

1. **Clone the repository and navigate to the project root:**
   ```bash
   cd swachh
   ```

2. **Create and activate a Python virtual environment:**
   - **Windows (PowerShell):**
     ```powershell
     python -m venv venv
     .\venv\Scripts\Activate.ps1
     ```
   - **Linux / macOS:**
     ```bash
     python3 -m venv venv
     source venv/bin/activate
     ```

3. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure the environment file:**
   Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```
   *Edit `.env` with your PostgreSQL database URL, Cloudinary/S3 keys, and Razorpay credentials.*

---

### 2. Database Initialization (PostgreSQL + PostGIS)

Ensure PostGIS is installed on your PostgreSQL database. You can test your connection and auto-create the schema and seed data by running the included test script:

```bash
python test_db.py
```

*When starting the FastAPI server, the application will also automatically run `CREATE EXTENSION IF NOT EXISTS postgis;`, generate missing tables via `Base.metadata.create_all`, and seed the default dummy reporter.*

**Start the FastAPI Backend:**
```bash
uvicorn src.main:app --reload --port 8000
```
Your backend will be live at `http://localhost:8000` with interactive Swagger docs at `http://localhost:8000/docs`.

---

### 3. Frontend Setup (Next.js & React 19)

1. **Open a new terminal and navigate to the `frontend/` directory:**
   ```bash
   cd frontend
   ```

2. **Install Node modules:**
   ```bash
   npm install
   ```

3. **Configure the frontend environment:**
   Create a `.env.local` file:
   ```env
   NEXT_PUBLIC_API_URL=http://localhost:8000
   ```

4. **Launch the development server:**
   ```bash
   npm run dev
   ```

The application will be accessible at:
- **Citizen Portal**: `http://localhost:3000`
- **Mock Civic Sign-In**: `http://localhost:3000/login`
- **Municipal Command Center**: `http://localhost:3000/admin`

---

## 🔐 Environment Variables

The project uses environment variables configured in the root `.env` file:

| Variable | Description | Example / Default |
| :--- | :--- | :--- |
| `ENVIRONMENT` | Runtime environment flag | `development` |
| `DATABASE_URL` | PostgreSQL async connection string with `asyncpg` | `postgresql+asyncpg://user:pass@host:5432/dbname` |
| `CLOUDINARY_CLOUD_NAME` | Cloudinary account cloud name | `dwfxzynam` |
| `CLOUDINARY_API_KEY` | Cloudinary API Key | `835983596979324` |
| `CLOUDINARY_API_SECRET` | Cloudinary API Secret | `l9v3_taelZUxFbm...` |
| `AWS_ACCESS_KEY_ID` | (Optional) AWS Access Key for S3 storage | `AKIAIOSFODNN7EXAMPLE` |
| `AWS_SECRET_ACCESS_KEY` | (Optional) AWS Secret Key for S3 storage | `wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY` |
| `AWS_REGION_NAME` | (Optional) AWS S3 bucket region | `ap-south-1` |
| `AWS_S3_BUCKET_NAME` | (Optional) AWS S3 bucket name | `swachhconnect-media` |
| `RAZORPAY_KEY_ID` | Razorpay API Key ID | `rzp_test_Sy1l...` |
| `RAZORPAY_KEY_SECRET` | Razorpay API Key Secret | `5oj2jPWCL...` |
| `RAZORPAYX_ACCOUNT_NUMBER` | RazorpayX virtual account for UPI payouts | `7878780080312416` |
| `DEFAULT_TENDER_AMOUNT` | Default monetary reward for GVP report approval (INR) | `50.00` |
| `GEMINI_API_KEY` | (Optional) Google Gemini API Key for vision validation | `AQ.Ab8RN6...` |

---

## 🧪 Walkthrough & Demo Flow

Experience the complete end-to-end civic feedback loop in under two minutes:

1. **Authentication**:
   - Go to `http://localhost:3000/login`.
   - Click **"Continue with Google"**. The simulated OAuth handshake logs you in with the default seeded reporter (`00000000-0000-0000-0000-000000000000`).
2. **Citizen Snap & Tag**:
   - On the mobile homepage (`/`), tap the glowing **Snap & Tag** camera button.
   - Select or capture any waste image.
   - Watch the holographic **Laser Scanning Animation** cycle through EXIF extraction and ML classification.
   - Upon confirmation, a success toast displays: *"AI Verified! Report accepted. ₹50 reward pending approval."*
3. **Command Center Review**:
   - Open `http://localhost:3000/admin` in a new window or tab.
   - Watch the new detection appear in the **Live Detections** queue and on the **Satellite Telemetry Map**.
   - Click **"VERIFY & DISPATCH TENDER"**.
4. **Instant Reward & Balance Refresh**:
   - The backend approves the GVP, generates a simulated/live Razorpay payout record, and credits ₹50 to the citizen.
   - Return to the citizen app tab: the wallet counter automatically bounces from `₹0` to `₹50` within seconds!

---

## 🛡️ Security & Anti-Fraud Measures

- **EXIF Verification**: Images without valid hardware GPS tags can be rejected to prevent submitting random internet images (gracefully falling back during local hackathon demo tests).
- **ML Confidence Thresholding**: Submissions scoring below `0.85` are stopped before database creation, preventing spam reports.
- **Transactional Consistency**: Relational foreign keys and cascading updates guarantee that payouts map directly to validated GVP instances.
- **Webhook Signature Verification**: RazorpayX webhook payloads support cryptographic signature verification to prevent spoofed payout events.

---

## 🗺️ Roadmap

- [ ] **AI Before-vs-After Structural Comparison**: Dual-image Siamese neural network to verify that cleanup photos match the exact geometry of the original report before payout dispatch.
- [ ] **Municipal ERP & Smart City Dashboard Integration**: Direct API connectors to city municipal corporations (e.g., BBMP, MCC, Swachh Bharat Mission portal).
- [ ] **Corporate CSR Pool Smart Contracts**: Enable corporations to sponsor specific wards or postal codes and fund automated escrow micro-tenders.
- [ ] **Native Mobile App (React Native / PWA)**: Offline-first image caching with automatic background sync when network connectivity is restored.

---

## 👥 Contributors

- **Mahek Fathima** ([@mahekfathima](https://github.com/mahekfathima))

---

<div align="center">
  <sub>Built with ❤️ for a cleaner, greener, and tech-driven future.</sub>
</div>
