from pymongo import MongoClient
from decouple import config
from urllib.parse import quote_plus

# --- Global Variables Initialized (Added 'notifications = None') ---
db = None
global_config = None
users_collection = None
drivers_collection = None
companies_collection = None
products_collection = None
gas_orders = None
pending_users_collection = None
pending_drivers_collection = None
notifications = None 
admins_collection = None
admin_sessions = None
admin_activity_logs = None
payouts_collection = None
inventory_collection = None
gas_stations_collection = None
suppliers_collection = None
stock_alerts_collection = None
ratings_collection = None
withdrawal_requests_collection = None

# === MongoDB Configuration ===
MONGO_USER = config("MONGO_USER")
MONGO_PASS = config("MONGO_PASS")
MONGO_DB = config("MONGO_DB")

password_encoded = quote_plus(MONGO_PASS)
MONGO_URI = (
    f"mongodb+srv://{MONGO_USER}:{password_encoded}"
    f"@cluster0.ulpdfeb.mongodb.net/{MONGO_DB}"
    f"?retryWrites=true&w=majority&ssl=true"
)

# === Connect to MongoDB ===
try:
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=20000)
    version = client.server_info()["version"]
    print(f"✅ MongoDB connected (version {version})")
    db = client[MONGO_DB]
except Exception as e:
    print("❌ MongoDB connection failed:", e)
    db = None

# === Collections ===
if db is not None:
    # Core collections
    users_collection = db["users"]
    drivers_collection = db["drivers"]
    companies_collection = db["companies"]
    products_collection = db["products"]
    gas_orders = db["gas_orders"]
    pending_users_collection = db['pending_users'] 
        # Pending drivers collection for driver verification flow
        pending_drivers_collection = db['pending_drivers']
    pending_drivers_collection = db['pending_drivers']
    withdrawal_requests_collection = db['withdrawal_requests']

    # System & notifications
    notifications = db["notifications"] 
    admins_collection = db["admins"]
    admin_sessions = db["admin_sessions"]
    admin_activity_logs = db["admin_activity_logs"]

    # Finance
    payouts_collection = db["payouts"]

    # Inventory
    inventory_collection = db["inventory"]
    gas_stations_collection = db["gas_stations"]
    suppliers_collection = db["suppliers"]
    stock_alerts_collection = db["stock_alerts"]
    ratings_collection = db["ratings"]
    global_config = db["global_config"]


    # === Indexes ===
    try:
        # Admin sessions
        admin_sessions.create_index("token", unique=True)
        admin_sessions.create_index("admin_email")
        admin_sessions.create_index("created_at")

        # Activity logs
        admin_activity_logs.create_index("admin_email")
        admin_activity_logs.create_index("timestamp")

        # Core collections
        admins_collection.create_index("email", unique=True)
        admins_collection.create_index("username", unique=True)
        users_collection.create_index("email", unique=True)
        drivers_collection.create_index("email", unique=True)
        gas_orders.create_index("status")
        gas_orders.create_index("driver_id")
        gas_orders.create_index("created_at")
        notifications.create_index([("user_id", 1), ("read", 1), ("created_at", -1)])

        print("✅ MongoDB indexes ensured.")
    except Exception as idx_err:
        print("⚠️ Index creation failed:", idx_err)

    print("c")
else:
    print("⚠️ Skipping collection setup — MongoDB not connected.")
