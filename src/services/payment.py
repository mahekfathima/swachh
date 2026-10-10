import os
import razorpay
from typing import Optional, Dict, Any

def get_razorpay_client():
    key_id = os.getenv("RAZORPAY_KEY_ID")
    key_secret = os.getenv("RAZORPAY_KEY_SECRET")
    
    if not key_id or not key_secret:
        raise ValueError("Razorpay credentials are not configured.")
        
    return razorpay.Client(auth=(key_id, key_secret))

def create_contact_and_fund_account(name: str, email: str, contact_number: str, upi_id: str) -> Optional[str]:
    """
    Creates a Razorpay Contact and then a Fund Account (UPI) for the contact.
    Returns the fund_account_id if successful.
    """
    client = get_razorpay_client()
    try:
        # 1. Create Contact
        contact_data = {
            "name": name,
            "email": email,
            "contact": contact_number,
            "type": "citizen",
            "reference_id": f"ref_{contact_number}"
        }
        contact = client.contact.create(data=contact_data)
        contact_id = contact.get("id")

        if not contact_id:
            return None

        # 2. Create Fund Account (UPI)
        fund_account_data = {
            "contact_id": contact_id,
            "account_type": "vpa",
            "vpa": {
                "address": upi_id
            }
        }
        fund_account = client.fund_account.create(data=fund_account_data)
        return fund_account.get("id")
        
    except Exception as e:
        print(f"Razorpay Account Creation Error: {e}")
        return None

def trigger_payout(fund_account_id: str, amount_inr: float, reference_id: str) -> Dict[str, Any]:
    """
    Triggers a RazorpayX Payout.
    Returns the payout response dict.
    """
    client = get_razorpay_client()
    
    # Amount needs to be in paise (multiply INR by 100)
    amount_paise = int(amount_inr * 100)
    
    try:
        payout_data = {
            "account_number": os.getenv("RAZORPAYX_ACCOUNT_NUMBER"), # From which account the payout is made
            "fund_account_id": fund_account_id,
            "amount": amount_paise,
            "currency": "INR",
            "mode": "UPI",
            "purpose": "payout",
            "queue_if_low_balance": True,
            "reference_id": reference_id,
            "narration": "SwachhConnect Cleanup Reward"
        }
        payout = client.payout.create(data=payout_data)
        return payout
    except Exception as e:
        print(f"Razorpay Payout Error: {e}")
        raise e
