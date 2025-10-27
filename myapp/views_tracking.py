import json
from datetime import datetime, timedelta
from bson import ObjectId
from django.http import JsonResponse
from geopy.distance import geodesic
from rest_framework.decorators import api_view


# --- Utility ---
def calculate_eta(driver_loc, delivery_loc, avg_speed_kmh=30):
    """Return ETA datetime based on distance and average speed."""
    try:
        dist_km = geodesic(driver_loc, delivery_loc).km
    except Exception:
        dist_km = 0
    eta_min = dist_km / avg_speed_kmh * 60
    return datetime.utcnow() + timedelta(minutes=eta_min)

# --- Driver sends GPS updates ---
@api_view(["POST"])
def update_driver_location(request, driver_id):
    data = json.loads(request.body)
    lat, lng = data.get("lat"), data.get("lng")
    if lat is None or lng is None:
        return JsonResponse({"success": False, "message": "Missing location"}, status=400)

    now = datetime.utcnow()
    drivers_collection.update_one(
        {"_id": ObjectId(driver_id)},
        {"$set": {"current_location": {"lat": lat, "lng": lng, "timestamp": now}}}
    )

    # also push to active order
    active = gas_orders.find_one({"driver_id": driver_id, "status": {"$in": ["On the way", "Picked up"]}})
    if active:
        delivery = active.get("delivery_location", None)
        if delivery:
            eta = calculate_eta((lat, lng),
                                (delivery["lat"], delivery["lng"])) if "lat" in delivery else None
        else:
            eta = None
        gas_orders.update_one(
            {"_id": active["_id"]},
            {"$set": {
                "current_location": {"lat": lat, "lng": lng, "timestamp": now},
                "estimated_arrival": eta
            }}
        )
    return JsonResponse({"success": True})
    

# --- User polls for tracking info ---
@api_view(["GET"])
def track_order(request, order_id):
    order = gas_orders.find_one({"_id": ObjectId(order_id)})
    if not order:
        return JsonResponse({"success": False, "message": "Order not found"}, status=404)

    driver = drivers_collection.find_one({"_id": ObjectId(order["driver_id"])}, {"password": 0}) if order.get("driver_id") else None

    return JsonResponse({
        "success": True,
        "tracking": {
            "order_id": str(order["_id"]),
            "status": order.get("status"),
            "driver": {
                "name": driver.get("name") if driver else None,
                "phone": driver.get("phone") if driver else None,
                "location": order.get("current_location"),
            },
            "delivery_location": order.get("delivery_location"),
            "eta": order.get("estimated_arrival"),
            "last_updated": order.get("updated_at"),
        }
    })
