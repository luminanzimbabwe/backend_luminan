import asyncio
import json
import random
import websockets
from datetime import datetime, timezone

WS_URL = "ws://127.0.0.1:8000/ws/admin/drivers/"
DRIVER_ID = "68fb5f049ed7068eca712dbd"
DRIVER_NAME = "private"

lat = -17.8292
lon = 31.0522

async def simulate_driver():
    async with websockets.connect(WS_URL) as ws:
        print("✅ Connected to admin tracking WebSocket")
        while True:
            # Random movement
            global lat, lon
            lat += random.uniform(-0.0005, 0.0005)
            lon += random.uniform(-0.0005, 0.0005)
            speed = random.randint(10, 60)

            message = {
                "event": "driver_update",      # must match frontend
                "driver_id": DRIVER_ID,
                "lat": lat,
                "lng": lon,
                "speed": speed,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }

            await ws.send(json.dumps(message))
            print(f"📡 Sent update: {lat:.5f}, {lon:.5f} ({speed} km/h)")
            await asyncio.sleep(3)

if __name__ == "__main__":
    try:
        asyncio.run(simulate_driver())
    except KeyboardInterrupt:
        print("\n🛑 Simulation stopped.")
