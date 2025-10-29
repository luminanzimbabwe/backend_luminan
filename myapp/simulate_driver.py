# simulate_driver.py
import asyncio
import json
import websockets
import random
from datetime import datetime

# --- CONFIGURATION ---
ORDER_ID = "68fb43ea6d8b40cce800f624"  # your test order ID
DRIVER_ID = "6900bbc93c9f92a9882679b0"  # your driver ID
WEBSOCKET_URL = f"ws://127.0.0.1:8000/ws/track/{ORDER_ID}/"

# Bounding box for simulation (e.g., Harare area)
MIN_LAT, MAX_LAT = -17.8305, -17.8250
MIN_LNG, MAX_LNG = 31.0500, 31.0550
STEP = 0.0003  # movement per update (~30m per tick)

def random_start():
    """Generate a random starting coordinate within bounding box."""
    lat = random.uniform(MIN_LAT, MAX_LAT)
    lng = random.uniform(MIN_LNG, MAX_LNG)
    return lat, lng

async def send_location():
    """Continuously send simulated driver GPS updates."""
    lat, lng = random_start()
    print(f"Connecting to {WEBSOCKET_URL} as driver {DRIVER_ID}...")
    
    try:
        async with websockets.connect(WEBSOCKET_URL) as ws:
            print("✅ Connected to backend WebSocket.")

            while True:
                # Simulate random movement in a more natural direction
                lat += random.uniform(-STEP, STEP)
                lng += random.uniform(-STEP, STEP)
                now = datetime.utcnow().isoformat()

                message = json.dumps({
                    "driver_id": DRIVER_ID,
                    "lat": lat,
                    "lng": lng,
                    "timestamp": now
                })

                try:
                    await ws.send(message)
                    print(f"📍 Sent location: {lat:.6f}, {lng:.6f} at {now}")

                    # Optionally read backend response (non-blocking)
                    try:
                        response = await asyncio.wait_for(ws.recv(), timeout=1)
                        print("🛰️  Server response:", response)
                    except asyncio.TimeoutError:
                        pass

                except Exception as e:
                    print("❌ Error sending data:", e)
                    break

                await asyncio.sleep(2)  # send every 2 seconds

    except websockets.exceptions.InvalidStatus as e:
        print(f"🚫 Server rejected connection: {e}")
    except Exception as e:
        print(f"💥 Connection failed: {e}")

if __name__ == "__main__":
    asyncio.run(send_location())
