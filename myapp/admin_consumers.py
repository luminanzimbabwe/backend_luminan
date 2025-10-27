import json
from channels.generic.websocket import AsyncWebsocketConsumer
from datetime import datetime
from bson import ObjectId
from .db import drivers_collection

class AdminDriverTrackingConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Create a group for all admins
        self.group_name = "admin_drivers"
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()
        await self.send(json.dumps({"event": "connected", "message": "Admin connected to live tracking"}))

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data):
        """Admins don’t send data; only receive driver updates"""
        await self.send(json.dumps({"event": "info", "message": "Admin listening only"}))

    async def driver_location_update(self, event):
        """Receive location broadcast from drivers"""
        await self.send(json.dumps({
            "event": "driver_update",
            "driver_id": event["driver_id"],
            "lat": event["lat"],
            "lng": event["lng"],
            "timestamp": event["timestamp"],
        }))
