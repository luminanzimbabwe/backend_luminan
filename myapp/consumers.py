import json
from channels.generic.websocket import AsyncWebsocketConsumer
from bson import ObjectId
from datetime import datetime
from db import gas_orders, drivers_collection


# --- DRIVER ↔ ORDER WEBSOCKET ---
from channels.generic.websocket import AsyncWebsocketConsumer
from bson import ObjectId
from datetime import datetime, timezone
import json

class OrderTrackingConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.order_id = self.scope["url_route"]["kwargs"]["order_id"]
        self.group_name = f"order_{self.order_id}"

        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

        # --- Fetch order & driver info ---
        order = gas_orders.find_one({"_id": ObjectId(self.order_id)})
        driver = None
        driver_id = None

        if order:
            driver_id = order.get("driver_id") or order.get("assigned_driver_id")

        if driver_id:
            driver = drivers_collection.find_one({"_id": ObjectId(driver_id)})

        # --- Prepare initial payload ---
        payload = {
            "event": "location_update",
            "status": order.get("status", "") if order else "",
            "eta": order.get("eta", "Calculating...") if order else "Calculating...",
        }

        if driver and driver.get("current_location"):
            current_loc = driver["current_location"]
            payload.update({
                "lat": current_loc.get("lat", 0.0),
                "lng": current_loc.get("lng", 0.0),
                "driver_id": str(driver["_id"]),
                "driver_name": driver.get("username", driver.get("name", "")),
                "driver_vehicle": driver.get("vehicle_number", driver.get("vehicle", "")),
                "timestamp": str(current_loc.get("timestamp", datetime.now(timezone.utc))),
            })
        else:
            payload.update({
                "lat": 0.0,
                "lng": 0.0,
                "driver_id": driver_id or "",
                "driver_name": "",
                "driver_vehicle": "",
                "timestamp": str(datetime.now(timezone.utc))
            })

        await self.send(json.dumps(payload))

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data):
        """Driver sends GPS updates here."""
        try:
            data = json.loads(text_data)
            lat, lng, driver_id = data.get("lat"), data.get("lng"), data.get("driver_id")

            if lat is None or lng is None or not driver_id:
                await self.send(json.dumps({
                    "event": "error",
                    "message": "Missing lat/lng/driver_id"
                }))
                return

            now = datetime.now(timezone.utc)

            # --- Update driver location in DB ---
            drivers_collection.update_one(
                {"_id": ObjectId(driver_id)},
                {"$set": {"current_location": {"lat": float(lat), "lng": float(lng), "timestamp": now}}}
            )

            # --- Fetch latest driver & order info ---
            driver = drivers_collection.find_one({"_id": ObjectId(driver_id)})
            order = gas_orders.find_one({"_id": ObjectId(self.order_id)})

            # --- Update order’s current location ---
            gas_orders.update_one(
                {"_id": ObjectId(self.order_id)},
                {"$set": {"current_location": {"lat": float(lat), "lng": float(lng), "timestamp": now}}}
            )

            # --- Broadcast to order group (user tracking) ---
            await self.channel_layer.group_send(
                self.group_name,
                {
                    "type": "location_update",
                    "lat": float(lat),
                    "lng": float(lng),
                    "driver_id": driver_id,
                    "driver_name": driver.get("username", driver.get("name", "")) if driver else "",
                    "driver_vehicle": driver.get("vehicle_number", driver.get("vehicle", "")) if driver else "",
                    "status": order.get("status", "") if order else "",
                    "eta": order.get("eta", "Calculating...") if order else "Calculating...",
                    "timestamp": str(now),
                }
            )

            # --- Broadcast to all admins (admin live map) ---
            await self.channel_layer.group_send(
                "admin_driver_tracking",
                {
                    "type": "driver_location_update",
                    "driver_id": driver_id,
                    "lat": float(lat),
                    "lng": float(lng),
                    "timestamp": str(now),
                }
            )

        except Exception as e:
            print(f"❌ WebSocket error: {e}")
            await self.send(json.dumps({
                "event": "error",
                "message": str(e)
            }))

    async def location_update(self, event):
        """Send live updates to users tracking a specific order."""
        await self.send(json.dumps({
            "event": "location_update",
            "lat": event.get("lat"),
            "lng": event.get("lng"),
            "driver_id": event.get("driver_id", ""),
            "driver_name": event.get("driver_name", ""),
            "driver_vehicle": event.get("driver_vehicle", ""),
            "status": event.get("status", ""),
            "eta": event.get("eta", "Calculating..."),
            "timestamp": event.get("timestamp"),
        }))


# --- ADMIN LIVE DRIVER TRACKING REFINED ---
class AdminDriverTrackingConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.group_name = "admin_driver_tracking"
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

        # Initial connection confirmation
        await self.send(json.dumps({
            "event": "connected",
            "message": "Admin connected to driver tracking."
        }))

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def driver_location_update(self, event):
        """
        Refined: Send driver info in frontend-expected format.
        """
        driver_payload = {
            "id": event.get("driver_id", ""),
            "lat": event.get("lat", 34.0522),   # fallback to default
            "lon": event.get("lng", -118.2437), # fallback to default
            "speed": event.get("speed", 0),
            "lastUpdate": event.get("timestamp", ""),
            "status": event.get("status", "En Route"),
            "assignedRoute": event.get("assignedRoute", "Unassigned")
        }

        await self.send(json.dumps({
            "event": "driver_update",
            "driver": driver_payload
        }))
