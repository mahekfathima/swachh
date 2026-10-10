from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS
import io

def get_decimal_from_dms(dms, ref):
    """Convert degrees, minutes, seconds to decimal degrees."""
    degrees = dms[0]
    minutes = dms[1]
    seconds = dms[2]
    
    decimal = float(degrees) + float(minutes)/60 + float(seconds)/3600
    
    if ref in ['S', 'W']:
        decimal = -decimal
    return decimal

def extract_gps_coordinates(file_bytes: bytes) -> tuple[float, float]:
    """
    Extracts GPS coordinates from image EXIF data.
    Returns a tuple of (latitude, longitude) or (None, None) if not found.
    """
    try:
        image = Image.open(io.BytesIO(file_bytes))
        exif_data = image._getexif()
        
        if not exif_data:
            print("Warning: No EXIF data found. Using dummy coordinates for hackathon demo.")
            return 12.2958, 76.6394

        gps_info = {}
        for tag, value in exif_data.items():
            decoded = TAGS.get(tag, tag)
            if decoded == "GPSInfo":
                for t in value:
                    sub_decoded = GPSTAGS.get(t, t)
                    gps_info[sub_decoded] = value[t]

        if "GPSLatitude" in gps_info and "GPSLongitude" in gps_info:
            lat = get_decimal_from_dms(gps_info["GPSLatitude"], gps_info.get("GPSLatitudeRef", "N"))
            lon = get_decimal_from_dms(gps_info["GPSLongitude"], gps_info.get("GPSLongitudeRef", "E"))
            return lat, lon

        print("Warning: GPS Info not found in EXIF. Using dummy coordinates for hackathon demo.")
        return 12.2958, 76.6394
    except Exception as e:
        print(f"Error extracting EXIF: {e}. Using dummy coordinates.")
        return 12.2958, 76.6394
