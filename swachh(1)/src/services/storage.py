import os
import requests
from typing import Optional
import time
import hashlib

def upload_image_to_s3(file_bytes: bytes, filename: str, content_type: str = "image/jpeg") -> Optional[str]:
    """
    Uploads an image to Cloudinary (kept the function name 's3' for backward compatibility in main.py)
    and returns the public secure URL.
    """
    cloud_name = os.getenv('CLOUDINARY_CLOUD_NAME')
    api_key = os.getenv('CLOUDINARY_API_KEY')
    api_secret = os.getenv('CLOUDINARY_API_SECRET')
    
    if not all([cloud_name, api_key, api_secret]):
        print("Warning: Cloudinary credentials are not fully set in .env")
        return None

    url = f"https://api.cloudinary.com/v1_1/{cloud_name}/image/upload"
    
    timestamp = str(int(time.time()))
    
    # Cloudinary Signature = sha1(sorted_params_string + api_secret)
    string_to_sign = f"timestamp={timestamp}{api_secret}"
    signature = hashlib.sha1(string_to_sign.encode('utf-8')).hexdigest()

    data = {
        "api_key": api_key,
        "timestamp": timestamp,
        "signature": signature,
    }
    
    files = {
        "file": (filename, file_bytes, content_type)
    }

    try:
        response = requests.post(url, data=data, files=files)
        if response.status_code == 200:
            return response.json().get("secure_url")
        else:
            print(f"Error uploading to Cloudinary: {response.text}")
            return None
    except Exception as e:
        print(f"Exception during Cloudinary upload: {e}")
        return None
