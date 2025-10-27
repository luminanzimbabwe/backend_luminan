# myapp/utils.py
import requests
from django.conf import settings
import jwt
import datetime
from bson import ObjectId
from bson.errors import InvalidId
from db import gas_orders, drivers_collection


# -----------------------
# Order-related helpers
# -----------------------
def get_updated_order(order_id):
    try:
        oid_order = ObjectId(order_id)
    except InvalidId:
        return None
    return gas_orders.find_one({"_id": oid_order})

def get_driver_details(driver_id):
    try:
        oid_driver = ObjectId(driver_id)
    except InvalidId:
        return None
    driver_doc = drivers_collection.find_one({"_id": oid_driver})
    if not driver_doc:
        return None
    return {
        "driver_id": str(driver_doc.get("_id")),
        "driver_name": driver_doc.get("username"),
        "phone": driver_doc.get("phone"),
        "vehicle_number": driver_doc.get("vehicle_number"),
        "vehicle_color": driver_doc.get("vehicle_color"),
        "photo_url": driver_doc.get("photo_url"),
        "currentLocation": driver_doc.get("currentLocation", {"lat": 0, "lng": 0}),
    }

def fetch_order_tracking_data(order_id):
    try:
        try:
            ObjectId(order_id)
        except InvalidId:
            return {"error": "Invalid order ID format"}, 400

        order_data = get_updated_order(order_id)
        if not order_data:
            return {"error": "Order not found"}, 404

        driver_id = order_data.get("assigned_driver_id")
        driver_details = get_driver_details(driver_id) if driver_id else None

        tracking_statuses = ["confirmed", "accepted", "picked_up", "in_transit"]
        eta = "15-20 mins" if order_data.get("order_status") in tracking_statuses else "Calculating..."

        response_data = {
            "order_id": order_data.get("order_id"),
            "status": order_data.get("order_status"),
            "delivery_address": order_data.get("delivery_address"),
            "eta": eta,
            "driver": driver_details,
        }

        return response_data, 200

    except Exception as e:
        print(f"Error fetching tracking data: {e}")
        return {"error": "Failed to retrieve order tracking details", "details": str(e)}, 500

# -----------------------
# SMS helper
# -----------------------
TEXTBEE_API_URL = "https://api.textbee.dev/sms/send"

def send_sms(to_number, message):
    headers = {
        "Authorization": f"Bearer {settings.TEXTBEE_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {"to": to_number, "message": message}
    try:
        response = requests.post(TEXTBEE_API_URL, json=payload, headers=headers)
        response.raise_for_status()
        return {"success": True, "data": response.json()}
    except requests.exceptions.RequestException as err:
        return {"success": False, "error": str(err)}

# -----------------------
# JWT helper
# -----------------------
def create_jwt_tokens(admin_data):
    payload = {
        "admin_id": str(admin_data["_id"]),
        "email": admin_data["email"],
        "role": "superadmin",
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=2),
        "iat": datetime.datetime.utcnow(),
    }
    access_token = jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")

    refresh_payload = {
        "admin_id": str(admin_data["_id"]),
        "type": "refresh",
        "exp": datetime.datetime.utcnow() + datetime.timedelta(days=7),
        "iat": datetime.datetime.utcnow(),
    }
    refresh_token = jwt.encode(refresh_payload, settings.SECRET_KEY, algorithm="HS256")
    return access_token, refresh_token



# utils.py

DEFAULT_PRICE_PER_KG = 2.0  # fallback price

def safe_float(value, default=0.0):
    try:
        return float(value)
    except (TypeError, ValueError):
        return default

def safe_int(value, default=0):
    try:
        return int(value)
    except (TypeError, ValueError):
        return default

def serialize_objectid(doc):
    """
    Recursively convert ObjectId in dict to string for JSON response
    """
    if isinstance(doc, dict):
        return {k: serialize_objectid(v) for k, v in doc.items()}
    elif isinstance(doc, list):
        return [serialize_objectid(i) for i in doc]
    elif hasattr(doc, '__class__') and doc.__class__.__name__ == 'ObjectId':
        return str(doc)
    else:
        return doc
