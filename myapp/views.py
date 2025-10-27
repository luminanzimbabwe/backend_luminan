from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.views.decorators.csrf import csrf_exempt
from django.utils.timezone import now
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.contrib.auth.models import AnonymousUser
from django.conf import settings
import traceback
import os
from functools import wraps
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from .serializers import serializers
from .serializers import DriverSerializer
from django.views.decorators.http import require_POST

from datetime import datetime, timedelta
from bson import ObjectId
from decouple import config
import bcrypt
from bcrypt import hashpw, gensalt, checkpw
import uuid, random, secrets, requests, pytz, jwt, traceback

from .utils import send_sms
from db import (
    users_collection,
    drivers_collection,
    companies_collection,
    products_collection,
    gas_orders,
    notifications,
    admins_collection,
    admin_activity_logs,
    admin_sessions,
    inventory_collection,
    gas_stations_collection,
    suppliers_collection,
    stock_alerts_collection,
    ratings_collection,
    payouts_collection,
    pending_users_collection,
    pending_drivers_collection,
    withdrawal_requests_collection,
    global_config


)
from bson.objectid import ObjectId
from datetime import datetime

import random
import string
from datetime import datetime, timedelta
import re
import os
import jwt
import traceback
from datetime import datetime, timedelta
from bson.objectid import ObjectId
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.conf import settings
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from paynow import Paynow

# Initialize Paynow with localhost URLs for testing
paynow = Paynow(
    '22231',  # Your Integration ID
    '191b4024-b653-42d9-9199-3b20fa5c894c',  # Integration Key
    'http://localhost:8000/paynow/update',  # Poll URL for Paynow status updates
    'http://localhost:8000/return?gateway=paynow'  # Return URL after payment
)

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
import openai
from django.conf import settings

# Set API key
openai.api_key = settings.OPENAI_API_KEY

import traceback

@api_view(['POST'])
@permission_classes([AllowAny])
def chat_with_gpt(request):
    print("OPENAI_API_KEY loaded:", settings.OPENAI_API_KEY is not None)

    user_message = request.data.get("message")
    if not user_message:
        return Response({"error": "Message is required"}, status=400)

    try:
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": user_message}],
            temperature=0.7
        )
        reply = response.choices[0].message["content"]
        return Response({"reply": reply})

    except Exception as e:
        print("=== ChatGPT API Exception ===")
        traceback.print_exc()
        return Response({"error": str(e)}, status=500)



# Constants (if not already imported from settings)
MAX_LOGIN_ATTEMPTS = getattr(settings, "MAX_LOGIN_ATTEMPTS", 5)
LOCKOUT_DURATION_MINUTES = getattr(settings, "LOCKOUT_DURATION_MINUTES", 15)
RESET_PASSWORD_URL = getattr(settings, "RESET_PASSWORD_URL", "https://yourdomain.com/reset-password")

# JWT config
SECRET_KEY = getattr(settings, "SECRET_KEY", "gQhJg-wB8q-v0A4LhK5zE_sXz3r-d-l2iGj9mZ8o2Y4_uT7P0fV6cU1yA2eR4t")
JWT_ALGORITHM = "HS256"


OTP_EXPIRY_MINUTES = 5











MAX_FAILED_ATTEMPTS = 5 # Used in verify_otp




LOCAL_TZ = pytz.timezone("Africa/Harare")
now = datetime.now(LOCAL_TZ)

MAX_FAILED_ATTEMPTS = 5
LOCKOUT_TIME_MINUTES = 15 
RESET_TOKEN_EXPIRY_HOURS = 10000000000 
MAX_FORGOT_REQUESTS = 3
FORGOT_REQUEST_WINDOW_MINUTES = 15
RESET_CODE_EXPIRY_MINUTES = 15


MAX_FAILED_ATTEMPTS = 5
LOCKOUT_TIME_MINUTES = 15
JWT_SECRET = config("SECRET_KEY")
JWT_ALGORITHM = "HS256"
JWT_EXP_DELTA_SECONDS = 60 * 60 * 24  # 1 day
JWT_EXP_DELTA_MINUTES = 60 * 60 * 24

# Alias for bcrypt functions
hashpw = bcrypt.hashpw
gensalt = bcrypt.gensalt
checkpw = bcrypt.checkpw

# --- NEW CONSTANTS FOR PASSWORD RESET ---
FORGOT_REQUEST_WINDOW_MINUTES = 10 # Time frame for rate limiting
MAX_FORGOT_REQUESTS = 3            # Max requests allowed within the window
RESET_CODE_EXPIRY_MINUTES = 15     # How long the 6-digit code is valid


checkpw = bcrypt.checkpw 



@api_view(['GET'])
@permission_classes([AllowAny])
def test_view(request):
    return Response({"message": "hello world"})



def get_user_from_token(token):
    return users_collection.find_one({"auth_token": token})




def send_test_sms(request):
    """
    Send a test SMS via TextBee to +263787592481
    """
    BASE_URL = "https://api.textbee.dev/api/v1"
    DEVICE_ID = "YOUR_DEVICE_ID"  
    API_KEY = settings.TEXTBEE_API_KEY

    url = f"{BASE_URL}/gateway/devices/{DEVICE_ID}/send-sms"

    payload = {
        "recipients": ["+263787592481"],  
        "message": "Hello! This is a test message from LuminaN app."
    }

    headers = {
        "x-api-key": API_KEY,
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        return JsonResponse({
            "success": True,
            "message": "SMS sent successfully",
            "response": response.json()
        })
    except requests.exceptions.RequestException as e:
        return JsonResponse({
            "success": False,
            "error": f"HTTP Error: {str(e)}"
        }, status=500)





def generate_otp():
    """Generates a secure 6-digit OTP."""
    # Uses random.choices for cryptographically secure random numbers (good practice)
    return ''.join(random.choices(string.digits, k=6))

from django.conf import settings # <-- Ensure this is imported

def dispatch_verification_code(contact_type, contact_value, code):
    """
    Dispatches the OTP via the chosen method (Email or SMS).
    Returns True on success, False on failure.
    """
    try:
        if contact_type == "email":
            # Assuming 'emails/verify_otp.html' template exists
            html_content = render_to_string('emails/verify_otp.html', {'code': code, 'expiry_minutes': 5})
            
            # Use Django's send_mail for email
            send_mail(
                subject="Account Verification Code",
                message=f"Your verification code is: {code}",
                # Uses the securely configured DEFAULT_FROM_EMAIL setting
                from_email=settings.DEFAULT_FROM_EMAIL, 
                recipient_list=[contact_value],
                html_message=html_content,
                fail_silently=False # 🛑 CRITICAL: Forces Django to raise the SMTP error
            )
            return True
            
        # ... (phone_number logic omitted for brevity)

        return False

    except Exception as e:
        # 🛑 CRITICAL: This logs the full traceback, including the SMTP error.
        print(f"!!! ERROR DISPATCHING CODE via {contact_type}: {traceback.format_exc()}")
        return False



# Place this function near your other dispatch functions (e.g., in views.py)

def dispatch_welcome_email(user_email, username):
    """Dispatches a welcome email with app information after registration."""
    try:
        # NOTE: You need to create this HTML template file: 'emails/welcome_message.html'
        html_content = render_to_string('emails/welcome_message.html', {
            'username': username,
            'app_name': 'Luminan Gas Delivery',
            'features': [
                "Order and schedule gas delivery from your phone.",
                "Track your delivery in real-time.",
                "Secure in-app payment options.",
                "View past order history."
            ]
        })

        send_mail(
            subject="Welcome to Luminan Gas Delivery!",
            message=f"Hi {username}, thank you for registering! Luminan makes getting gas simple. Check your OTP to verify your account.",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user_email],
            html_message=html_content,
            fail_silently=True # Important: Welcome email failure should NOT stop registration.
        )
        print(f"!!! WELCOME EMAIL DISPATCHED to {user_email} !!!")
        return True
    except Exception as e:
        # Log the error, but registration continues due to fail_silently=True
        print(f"!!! ERROR DISPATCHING WELCOME EMAIL to {user_email}: {traceback.format_exc()}")
        return False



def validate_registration_data(data):
    """Performs mandatory input validation."""
    errors = {}
    
    # Check Required Fields
    required_fields = ["username", "email", "phone_number", "password", "preferred_contact"]
    for field in required_fields:
        if not data.get(field) or not str(data[field]).strip():
            errors[field] = f"{field.replace('_', ' ').capitalize()} is required."

    # Check Password Strength
    password = data.get("password", "")
    if len(password) < 8:
        errors["password"] = "Password must be at least 8 characters long."
    # Optional: Add regex check for complexity (e.g., must contain a number/uppercase letter)

    # Check Email Format (Basic)
    if 'email' in data and data['email'] and not re.match(r"[^@]+@[^@]+\.[^@]+", data['email']):
        errors["email"] = "Invalid email format."
        
    # Check Contact Choice Validity
    preferred_contact = data.get("preferred_contact")
    if preferred_contact and preferred_contact not in ["email", "phone_number"]:
        errors["preferred_contact"] = "Must be 'email' or 'phone_number'."
    
    # Ensure the chosen contact method has a value
    if preferred_contact and preferred_contact in ["email", "phone_number"]:
        contact_value = data.get(preferred_contact)
        if not contact_value:
             errors[preferred_contact] = f"Contact value for {preferred_contact} is required."
        
    return errors



@api_view(['POST'])
@permission_classes([AllowAny])
def register_user(request):
    """
    Handles user registration, validation, password hashing, and initiates the OTP verification process.
    """
    # Use request.data.copy() if you need to modify the data before validation/hashing
    data = request.data

    # --- 1. Initial Data Validation ---
    errors = validate_registration_data(data)
    if errors:
        return Response({"error": "Validation failed", "details": errors}, status=400)

    # Normalize username
    username_lower = data["username"].lower()

    # Extract contact details dynamically
    try:
        preferred_contact = data["preferred_contact"]
        # Ensure the contact key exists in the data payload
        contact_value = data[preferred_contact] 
    except KeyError:
        return Response({"error": f"Required data field for '{preferred_contact}' is missing."}, status=400)

    try:
        # --- 2. Check for Existing User ---
        existing_user = pending_users_collection.find_one({
             # Check pending and fully registered collections
             # Assuming a `users_collection` (verified users) and `pending_users_collection` (unverified users)
             # You should check BOTH here if a user might exist unverified or verified.
            "$or": [
                {"username_lower": username_lower},
                {"email": data["email"]},
                {"phone_number": data["phone_number"]}
            ]
        })

        if existing_user:
            # 409 Conflict is the correct status for resource conflict
            return Response({"error": "An account with this data already exists."}, status=409)

        # --- 3. Hash Password ---
        hashed_pw = bcrypt.hashpw(
            data["password"].encode('utf-8'),
            bcrypt.gensalt()
        ).decode('utf-8')

        # --- 4. Generate and Dispatch OTP ---
        otp_code = generate_otp()
        otp_expiry = datetime.utcnow() + timedelta(minutes=5)

        if not dispatch_verification_code(preferred_contact, contact_value, otp_code):
            return Response({"error": "Failed to send verification code. Service unavailable."}, status=503)

        # --- 5. Create Temporary User Document ---
        temp_user_doc = {
            "username": data["username"],
            "username_lower": username_lower,
            "email": data["email"],
            "phone_number": data["phone_number"],
            "password_hash": hashed_pw,
            "role": "user",
            "is_verified": False,
            "otp_code": otp_code,
            "otp_expiry": otp_expiry,
            "verification_method": preferred_contact,
            "created_at": datetime.utcnow(),
            "failed_attempts": 0,
        }

        inserted_result = pending_users_collection.insert_one(temp_user_doc)
        
        # 🟢 CRITICAL FIX CONFIRMED: Convert ObjectId to string for JSON serialization
        temp_user_id_str = str(inserted_result.inserted_id) 

        # --- 6. Return Success Response ---
        return Response({
            "message": "Registration initiated. Verification code sent.",
            "verification_type": preferred_contact,
            "contact_sent_to": contact_value,
            "temp_user_id": temp_user_id_str 
        }, status=202) # 202 Accepted

    except Exception as e:
        # Log the full traceback for server-side debugging
        import traceback
        print(f"!!! CRITICAL REGISTRATION ERROR: {traceback.format_exc()}")
        return Response({
            "error": "Registration failed due to an unexpected server issue. Please try again."
        }, status=500)














# 🧩 Helper class for SimpleJWT compatibility (MongoDB users)
class SimpleUserMock:
    def __init__(self, user_id, username="mockuser", email=None):
        self.id = user_id
        self.pk = user_id
        self.username = username
        self.email = email

    def get_username(self):
        return self.username

    @property
    def is_authenticated(self):
        return True



# Constants
ACCESS_TOKEN_LIFETIME = getattr(settings, 'ACCESS_TOKEN_LIFETIME', timedelta(minutes=5))
REFRESH_TOKEN_LIFETIME = getattr(settings, 'REFRESH_TOKEN_LIFETIME', timedelta(days=7))
MAX_LOGIN_ATTEMPTS = 5
LOCKOUT_DURATION_MINUTES = 5

# Your SimpleUserMock class is already defined

@api_view(['POST'])
@permission_classes([AllowAny])
def verify_otp(request):
    data = request.data
    required_fields = ["temp_user_id", "otp_code"]

    # Basic validation
    for field in required_fields:
        if not data.get(field):
            return Response({"error": f"{field} is required."}, status=400)

    temp_user_id = data["temp_user_id"]
    submitted_otp = data["otp_code"]

    try:
        # Validate ObjectId
        try:
            user_id_obj = ObjectId(temp_user_id)
        except Exception:
            return Response({"error": "Invalid verification ID format."}, status=400)

        # Find pending user
        temp_user = pending_users_collection.find_one({"_id": user_id_obj})
        if not temp_user:
            return Response({"error": "Verification session expired or invalid ID. Please re-register."}, status=404)

        # Check for lockout
        failed_attempts = temp_user.get("failed_attempts", 0)
        if failed_attempts >= MAX_LOGIN_ATTEMPTS:
            if not temp_user.get("lockout_start"):
                pending_users_collection.update_one(
                    {"_id": user_id_obj},
                    {"$set": {"lockout_start": datetime.utcnow()}}
                )
            return Response({
                "error": f"Too many failed attempts. Please try again after {LOCKOUT_DURATION_MINUTES} minutes."
            }, status=429)

        # OTP expiration check
        otp_expiry = temp_user.get("otp_expiry")
        if not otp_expiry or datetime.utcnow() > otp_expiry:
            pending_users_collection.delete_one({"_id": user_id_obj})
            return Response({"error": "Verification code has expired. Please re-register."}, status=410)

        # Wrong OTP
        if submitted_otp != temp_user.get("otp_code"):
            pending_users_collection.update_one(
                {"_id": user_id_obj},
                {"$inc": {"failed_attempts": 1}}
            )
            return Response({"error": "Invalid verification code."}, status=400)

        # OTP correct — finalize registration
        final_user_doc = {
            k: v for k, v in temp_user.items()
            if k not in ["otp_code", "otp_expiry", "failed_attempts", "verification_method", "_id", "lockout_start"]
        }
        final_user_doc["is_verified"] = True
        final_user_doc["verified_at"] = datetime.utcnow()

        inserted_result = users_collection.insert_one(final_user_doc)
        pending_users_collection.delete_one({"_id": user_id_obj})

        # Optional: send welcome email
        try:
            dispatch_welcome_email(
                user_email=final_user_doc.get("email"),
                username=final_user_doc.get("username")
            )
        except Exception as e:
            print("⚠️ Failed to send welcome email:", e)

        # Generate JWT tokens via SimpleJWT
        user_id_str = str(inserted_result.inserted_id)
        # Use custom JWT helpers instead of RefreshToken.for_user to avoid
        # SimpleJWT attempting to persist tokens against Django's auth.User
        # (our users are stored in MongoDB with string/ObjectId IDs).
        access_token = generate_access_token(user_id_str, final_user_doc.get("role", "user"))
        refresh_token = generate_refresh_token(user_id_str)

        # Success response
        response_data = {
            "success": True,
            "message": "Account verified successfully.",
            # top-level token fields (preferred)
            "access": access_token,
            "refresh": refresh_token,
            # legacy compatibility
            "access_token": access_token,
            "refresh_token": refresh_token,
            "tokens": {
                "access": access_token,
                "refresh": refresh_token
            },
            "user": {
                "_id": user_id_str,
                "username": final_user_doc.get("username"),
                "email": final_user_doc.get("email"),
                "is_verified": True,
            },
        }

        return Response(response_data, status=200)

    except Exception:
        print(f"🔥 CRITICAL SERVER ERROR DURING VERIFY_OTP:\n{traceback.format_exc()}")
        return Response({"error": "An unexpected server error occurred during verification."}, status=500)









#  login users  









def generate_access_token(user_id, role):
    """Generates a secure, short-lived JWT Access Token."""
    payload = {
        'user_id': user_id,
        'role': role,
        'iat': datetime.utcnow(),
        'token_type': 'access',
    }
    # Optionally omit exp to make token non-expiring (dangerous for prod)
    if not getattr(settings, 'TOKEN_NEVER_EXPIRE', False):
        payload['exp'] = datetime.utcnow() + ACCESS_TOKEN_LIFETIME
    return jwt.encode(payload, SECRET_KEY, algorithm='HS256')

def generate_refresh_token(user_id):
    """Generates a secure, long-lived JWT Refresh Token."""
    payload = {
        'user_id': user_id,
        'iat': datetime.utcnow(),
        'token_type': 'refresh',
    }
    if not getattr(settings, 'TOKEN_NEVER_EXPIRE', False):
        payload['exp'] = datetime.utcnow() + REFRESH_TOKEN_LIFETIME
    return jwt.encode(payload, SECRET_KEY, algorithm='HS256')




def check_account_lockout(user):
    """Checks if a user is currently locked out."""
    failed_attempts = user.get('failed_login_attempts', 0)
    lockout_time = user.get('lockout_time')

    if failed_attempts >= MAX_LOGIN_ATTEMPTS and lockout_time:
        # Check if the lockout duration has passed
        if datetime.utcnow() < lockout_time + timedelta(minutes=LOCKOUT_DURATION_MINUTES):
            # Account is still locked
            return True, lockout_time
        else:
            # Lockout period has expired, reset attempts
            return False, None
    
    return False, None


def dispatch_login_notification(user_email, username, identifier, ip_address=None, device_info=None):
    """
    Sends a security email notification after a successful login.
    """
    # Format the login time for the email content
    login_time_formatted = datetime.utcnow().strftime("%B %d, %Y at %I:%M %p UTC")
    
    try:
        html_content = render_to_string('emails/login_notification.html', {
            'username': username,
            'identifier': identifier,
            'login_time': login_time_formatted,
            'ip_address': ip_address or "Not available",
            'device_info': device_info or "Web Browser",
            'reset_password_url': RESET_PASSWORD_URL,
            'current_year': datetime.utcnow().year,
        })

        send_mail(
            subject="Security Alert: New Sign-In to Your Luminan Account",
            message=f"A new sign-in was detected for your Luminan Gas Delivery account at {login_time_formatted}. If this wasn't you, please change your password immediately.",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user_email],
            html_message=html_content,
            fail_silently=True 
        )
        print(f"!!! LOGIN NOTIFICATION DISPATCHED to {user_email} !!!")
        return True
    except Exception as e:
        # Log the error, but don't fail the login process
        print(f"!!! ERROR DISPATCHING LOGIN NOTIFICATION to {user_email}: {traceback.format_exc()}")
        return False






@api_view(['POST'])
@permission_classes([AllowAny])
def login_user(request):
    data = request.data
    identifier = data.get("identifier")
    password = data.get("password")

    if not identifier or not password:
        return Response({"error": "Invalid credentials."}, status=401)

    try:
        identifier_lower = identifier.lower()

        # Find user
        user = users_collection.find_one({
            "$or": [
                {"username_lower": identifier_lower},
                {"email": identifier},
                {"phone_number": identifier}
            ]
        })

        if not user:
            return Response({"error": "Invalid credentials."}, status=401)

        # Check lockout
        is_locked, lockout_time = check_account_lockout(user)
        if is_locked:
            remaining_time = lockout_time + timedelta(minutes=LOCKOUT_DURATION_MINUTES) - datetime.utcnow()
            minutes = int(remaining_time.total_seconds() // 60)
            seconds = int(remaining_time.total_seconds() % 60)
            return Response({
                "error": "Account locked due to too many failed attempts.",
                "retry_after": f"{minutes}m {seconds}s"
            }, status=429)

        # Check verification
        if not user.get('is_verified', False):
            return Response({"error": "Account not verified."}, status=403)

        # Password check
        stored_hash = user.get('password_hash')
        if isinstance(stored_hash, str):
            stored_hash = stored_hash.encode('utf-8')
        if not stored_hash or not checkpw(password.encode('utf-8'), stored_hash):
            # Failed login attempt
            new_attempts = user.get('failed_login_attempts', 0) + 1
            update_fields = {"failed_login_attempts": new_attempts}
            if new_attempts >= MAX_LOGIN_ATTEMPTS:
                update_fields["lockout_time"] = datetime.utcnow()
            users_collection.update_one({"_id": user["_id"]}, {"$set": update_fields})
            return Response({"error": "Invalid credentials."}, status=401)

        # Reset failed attempts
        if user.get('failed_login_attempts', 0) > 0:
            users_collection.update_one(
                {"_id": user["_id"]},
                {"$set": {"failed_login_attempts": 0, "lockout_time": None}}
            )

        # Generate JWT tokens using the project's helpers (MongoDB user IDs)
        access_token = generate_access_token(str(user["_id"]), user.get("role", "user"))
        refresh_token = generate_refresh_token(str(user["_id"]))

        # Dispatch login notification
        ip_address = request.META.get('HTTP_X_FORWARDED_FOR') or request.META.get('REMOTE_ADDR')
        device_info = request.META.get('HTTP_USER_AGENT', 'Unknown Device')
        dispatch_login_notification(
            user_email=user["email"],
            username=user["username"],
            identifier=identifier,
            ip_address=ip_address,
            device_info=device_info
        )

        # Update last login
        users_collection.update_one(
            {"_id": user["_id"]},
            {"$set": {"last_login": datetime.utcnow()}}
        )

        # Response
        user_resp = {
            "id": str(user["_id"]),
            "username": user["username"],
            "email": user.get("email"),
            "role": user.get("role", "user"),
        }

        # Standardized response: top-level tokens + legacy keys + user object
        resp = {
            "access": access_token,
            "refresh": refresh_token,
            "access_token": access_token,
            "refresh_token": refresh_token,
            "user": user_resp,
        }

        return Response(resp, status=200)

    except Exception as e:
        print(f"Login error: {traceback.format_exc()}")
        return Response({"error": "Login failed due to a server error."}, status=500)












@api_view(['POST'])
@permission_classes([AllowAny])
def forgot_password(request):
    try:
        email = request.data.get("email")
        if not email:
            return Response({"error": "Email is required"}, status=400)

        user = users_collection.find_one({"email": email})
        if not user:
            # Crucial: Use generic response for security to prevent email enumeration
            return Response({"message": "If this account exists, a reset code has been sent."}, status=200)

        now = datetime.utcnow()
        
        # --- 🛑 FIX: Use datetime objects from MongoDB if available 🛑 ---
        last_request = user.get("last_forgot_request")
        request_count = user.get("forgot_request_count", 0)

        if last_request and isinstance(last_request, datetime):
            # Check if within the rate limit window
            if now - last_request < timedelta(minutes=FORGOT_REQUEST_WINDOW_MINUTES):
                if request_count >= MAX_FORGOT_REQUESTS:
                    return Response({"error": "Too many password reset requests. Try again later."}, status=429)
            else:
                request_count = 0  # reset counter if outside window

        # Generate reset code
        reset_code_plain = str(random.randint(100000, 999999))
        reset_code_hashed = hashpw(reset_code_plain.encode('utf-8'), gensalt()).decode('utf-8')
        expires_at = now + timedelta(minutes=RESET_CODE_EXPIRY_MINUTES)

        # Save to MongoDB
        users_collection.update_one(
            {"_id": user["_id"]},
            {"$set": {
                "reset_code": reset_code_hashed,
                "reset_code_expiry": expires_at,  # 🛑 Store as datetime object (preferred)
                "last_forgot_request": now,       # 🛑 Store as datetime object (preferred)
                "forgot_request_count": request_count + 1
            }}
        )

        # Send email
        html_content = render_to_string('emails/reset_password.html', {
            'user': user,
            'code': reset_code_plain,
            'expiry_minutes': RESET_CODE_EXPIRY_MINUTES
        })

        send_mail(
            subject="Luminan Password Reset Request",
            message=f"Your password reset code is: {reset_code_plain} (Expires in {RESET_CODE_EXPIRY_MINUTES} minutes).",
            from_email="Luminan Support <support@luminan.com>",
            recipient_list=[email],
            html_message=html_content,
            fail_silently=False
        )

        return Response({"message": "If this account exists, a reset code has been sent."}, status=200)

    except Exception as e:
        print(f"!!! CRITICAL FORGOT PASSWORD ERROR: {traceback.format_exc()}")
        return Response({"error": "Failed to process password reset due to a server issue."}, status=500)






@api_view(['POST'])
@permission_classes([AllowAny])
def reset_password(request):
    try:
        email = request.data.get("email")
        code = request.data.get("code")
        new_password = request.data.get("new_password")
        confirm_password = request.data.get("confirm_password")

        # 1. Input Validation
        if not all([email, code, new_password, confirm_password]):
            return Response({"error": "Email, code, new password, and confirm password are required"}, status=400)
        
        # NOTE: You should add a password strength check here (e.g., length > 8)
        if new_password != confirm_password:
            return Response({"error": "Passwords do not match"}, status=400)

        # 2. Find User and Check Code Existence
        user = users_collection.find_one({"email": email})
        # Use generic error message for security if user or code is missing
        if not user or "reset_code" not in user:
            return Response({"error": "Invalid or expired code."}, status=400)

        # 3. Check Expiry
        expiry_dt = user.get("reset_code_expiry")
        now = datetime.utcnow()
        
        # 🛑 FIX: Check for datetime object and compare
        if not expiry_dt or now > expiry_dt:
            return Response({"error": "Reset code has expired."}, status=400)

        # 4. Check Reset Code (Use checkpw)
        stored_code = user["reset_code"].encode('utf-8')
        if not checkpw(code.encode('utf-8'), stored_code):
            # Use generic error message for security
            return Response({"error": "Invalid or expired code."}, status=400)

        # 5. Hash new password and Update MongoDB
        hashed_pw = hashpw(new_password.encode('utf-8'), gensalt()).decode('utf-8')
        
        users_collection.update_one(
            {"_id": user["_id"]},
            {"$set": {
                "password_hash": hashed_pw, # 🛑 Use 'password_hash' for consistency
                "last_login": now          # Good practice to update last login/password change time
            }, 
            "$unset": {
                "reset_code": "", 
                "reset_code_expiry": "",
                "forgot_request_count": "",
                "last_forgot_request": ""
            }}
        )

        # 6. Send confirmation email
        html_content = render_to_string('emails/password_reset_success.html', {'user': user})
        send_mail(
            subject="Your Luminan Password Has Been Reset",
            message="Your password was reset successfully. If this wasn't you, please contact support immediately.",
            from_email="Luminan Support <support@luminan.com>",
            recipient_list=[user['email']],
            html_message=html_content,
            fail_silently=True # Changed to True: Don't fail the API if email service is down
        )

        return Response({"message": "Password reset successfully. You can now log in."}, status=200)

    except Exception as e:
        print(f"!!! CRITICAL RESET PASSWORD ERROR: {traceback.format_exc()}")
        return Response({"error": "Password reset failed due to a server issue."}, status=500)




@api_view(['POST'])
@permission_classes([AllowAny])
def forgot_password_driver(request):
    try:
        email = request.data.get("email")
        if not email:
            return Response({"error": "Email is required"}, status=400)

        driver = drivers_collection.find_one({"email": email})
        if not driver:
            # Crucial: Use generic response for security to prevent email enumeration
            return Response({"message": "If this account exists, a reset code has been sent."}, status=200)

        now = datetime.utcnow()

        # --- 🛑 FIX: Use datetime objects from MongoDB if available 🛑 ---
        last_request = driver.get("last_forgot_request")
        request_count = driver.get("forgot_request_count", 0)

        if last_request and isinstance(last_request, datetime):
            # Check if within the rate limit window
            if now - last_request < timedelta(minutes=FORGOT_REQUEST_WINDOW_MINUTES):
                if request_count >= MAX_FORGOT_REQUESTS:
                    return Response({"error": "Too many password reset requests. Try again later."}, status=429)
            else:
                request_count = 0  # reset counter if outside window

        # Generate reset code
        reset_code_plain = str(random.randint(100000, 999999))
        reset_code_hashed = hashpw(reset_code_plain.encode('utf-8'), gensalt()).decode('utf-8')
        expires_at = now + timedelta(minutes=RESET_CODE_EXPIRY_MINUTES)

        # Save to MongoDB
        drivers_collection.update_one(
            {"_id": driver["_id"]},
            {"$set": {
                "reset_code": reset_code_hashed,
                "reset_code_expiry": expires_at,  # 🛑 Store as datetime object (preferred)
                "last_forgot_request": now,       # 🛑 Store as datetime object (preferred)
                "forgot_request_count": request_count + 1
            }}
        )

        # Send email
        html_content = render_to_string('emails/reset_password.html', {
            'user': driver,
            'code': reset_code_plain,
            'expiry_minutes': RESET_CODE_EXPIRY_MINUTES
        })

        send_mail(
            subject="Luminan Driver Password Reset Request",
            message=f"Your password reset code is: {reset_code_plain} (Expires in {RESET_CODE_EXPIRY_MINUTES} minutes).",
            from_email="Luminan Support <support@luminan.com>",
            recipient_list=[email],
            html_message=html_content,
            fail_silently=False
        )

        return Response({"message": "If this account exists, a reset code has been sent."}, status=200)

    except Exception as e:
        print(f"!!! CRITICAL FORGOT PASSWORD DRIVER ERROR: {traceback.format_exc()}")
        return Response({"error": "Failed to process password reset due to a server issue."}, status=500)




@api_view(['POST'])
@permission_classes([AllowAny])
def reset_password_driver(request):
    try:
        email = request.data.get("email")
        code = request.data.get("code")
        new_password = request.data.get("new_password")
        confirm_password = request.data.get("confirm_password")

        # 1. Input Validation
        if not all([email, code, new_password, confirm_password]):
            return Response({"error": "Email, code, new password, and confirm password are required"}, status=400)

        # NOTE: You should add a password strength check here (e.g., length > 8)
        if new_password != confirm_password:
            return Response({"error": "Passwords do not match"}, status=400)

        # 2. Find Driver and Check Code Existence
        driver = drivers_collection.find_one({"email": email})
        # Use generic error message for security if driver or code is missing
        if not driver or "reset_code" not in driver:
            return Response({"error": "Invalid or expired code."}, status=400)

        # 3. Check Expiry
        expiry_dt = driver.get("reset_code_expiry")
        now = datetime.utcnow()

        # 🛑 FIX: Check for datetime object and compare
        if not expiry_dt or now > expiry_dt:
            return Response({"error": "Reset code has expired."}, status=400)

        # 4. Check Reset Code (Use checkpw)
        stored_code = driver["reset_code"].encode('utf-8')
        if not checkpw(code.encode('utf-8'), stored_code):
            # Use generic error message for security
            return Response({"error": "Invalid or expired code."}, status=400)

        # 5. Hash new password and Update MongoDB
        hashed_pw = hashpw(new_password.encode('utf-8'), gensalt()).decode('utf-8')

        drivers_collection.update_one(
            {"_id": driver["_id"]},
            {"$set": {
                "password_hash": hashed_pw, # 🛑 Use 'password_hash' for consistency
                "last_login": now          # Good practice to update last login/password change time
            },
            "$unset": {
                "reset_code": "",
                "reset_code_expiry": "",
                "forgot_request_count": "",
                "last_forgot_request": ""
            }}
        )

        # 6. Send confirmation email
        html_content = render_to_string('emails/password_reset_success.html', {'user': driver})
        send_mail(
            subject="Your Luminan Driver Password Has Been Reset",
            message="Your password was reset successfully. If this wasn't you, please contact support immediately.",
            from_email="Luminan Support <support@luminan.com>",
            recipient_list=[driver['email']],
            html_message=html_content,
            fail_silently=True # Changed to True: Don't fail the API if email service is down
        )

        return Response({"message": "Password reset successfully. You can now log in."}, status=200)

    except Exception as e:
        print(f"!!! CRITICAL RESET PASSWORD DRIVER ERROR: {traceback.format_exc()}")
        return Response({"error": "Password reset failed due to a server issue."}, status=500)




# -------------------------
# Logout endpoint (Refined)
# -------------------------

@api_view(['POST'])
# 🛑 FIX: Use IsAuthenticated or similar custom decorator 
# that validates the JWT BEFORE the view is run.
@permission_classes([IsAuthenticated]) 
def logout_user(request):
    # The IsAuthenticated decorator handles the token check. 
    # For JWT, 'logout' means instructing the client to destroy 
    # the token and forget the user's session data.
    
    # We don't need to check the token again, just return success.
    return Response({"message": "Logged out successfully. Please discard your tokens."}, status=200)

# NOTE: If you don't have an IsAuthenticated class, you must 
# remove the @permission_classes line and use the logic from 
# the delete_account view (with the get_user_from_token check).



# -------------------------
# Delete account endpoint (Refined)
# -------------------------
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_account(request):
    user = request.user

    # Verify password is provided and correct
    password = request.data.get('password')
    if not password:
        return Response({"error": "Password is required for account deletion."}, status=400)

    # For SimpleUser model, check password manually since it might not have check_password method
    try:
        # Assuming SimpleUser has a password field that stores hashed password
        from django.contrib.auth.hashers import check_password
        if hasattr(user, 'password') and user.password:
            if not check_password(password, user.password):
                return Response({"error": "Invalid password."}, status=400)
        else:
            # If no password field or empty password, skip verification for now
            # User is already authenticated via JWT token
            pass
    except Exception as e:
        # If password verification fails for any reason, skip it
        # User is already authenticated via JWT token
        pass

    try:
        # Get user ID - assuming user.id is the string/ObjectId
        user_id = user.id

        # Delete user from database
        result = users_collection.delete_one({"_id": ObjectId(user_id)})

        if result.deleted_count == 0:
            return Response({"error": "User account not found."}, status=404)

        # Optional: Send confirmation email or log the action
        # dispatch_account_deletion_confirmation(user.email, user.username)

        return Response({"message": "Account and all associated data deleted successfully."}, status=200)

    except Exception as e:
        # Log the error in production
        # logger.error(f"Account deletion error: {str(e)}")
        return Response({"error": "Account deletion failed due to a server issue."}, status=500)






from bson import ObjectId, errors as bson_errors
import logging

logger = logging.getLogger(__name__)

@api_view(['POST'])
@permission_classes([AllowAny])
def refresh_token(request):
    """
    Accepts a refresh token, validates it, and returns new access and refresh tokens.
    Includes detailed debugging logs.
    """
    try:
        logger.info("Received refresh token request")
        logger.info(f"Request data: {request.data} | type: {type(request.data)}")

        data = request.data
        # Accept multiple possible field names from clients
        refresh_token_str = data.get("refresh") or data.get("refreshToken") or data.get("refresh_token")
        logger.info(f"Received refresh token (raw): {data} | selected: {refresh_token_str} | type: {type(refresh_token_str)}")

        # If not found in parsed request.data, try raw body (JSON or form-encoded)
        if not refresh_token_str:
            try:
                raw = request.body.decode('utf-8') if hasattr(request, 'body') else ''
                if raw:
                    import json
                    try:
                        parsed = json.loads(raw)
                        refresh_token_str = parsed.get('refresh') or parsed.get('refreshToken') or parsed.get('refresh_token')
                        logger.info(f"Parsed raw JSON body for refresh token: {refresh_token_str}")
                    except Exception:
                        # Try form-encoded parse
                        from urllib.parse import parse_qs
                        parsed_qs = parse_qs(raw)
                        for key in ('refresh', 'refreshToken', 'refresh_token'):
                            if key in parsed_qs and parsed_qs[key]:
                                refresh_token_str = parsed_qs[key][0]
                                logger.info(f"Found refresh token in form body key '{key}'")
                                break
            except Exception as e:
                logger.debug(f"Failed to parse raw body for refresh token: {e}")

        # As a last resort, allow sending the refresh token in the Authorization header
        if not refresh_token_str:
            auth_header = request.META.get('HTTP_AUTHORIZATION', '') or request.headers.get('Authorization', '') if hasattr(request, 'headers') else ''
            if auth_header:
                parts = auth_header.split()
                if len(parts) == 2 and parts[0].lower() == 'bearer':
                    candidate = parts[1]
                    try:
                        # decode without exp verification to inspect token_type
                        payload_preview = jwt.decode(candidate, SECRET_KEY, algorithms=["HS256"], options={"verify_exp": False})
                        if payload_preview.get('token_type') == 'refresh':
                            refresh_token_str = candidate
                            logger.info("Using refresh token provided in Authorization header")
                        else:
                            logger.info(f"Authorization header provided but token_type is not 'refresh': {payload_preview.get('token_type')}")
                    except Exception as e:
                        logger.debug(f"Authorization header bearer is not a usable JWT: {e}")

        if not refresh_token_str:
            logger.warning("No refresh token provided in request (checked JSON body, form body, and Authorization header)")
            return Response({"error": "Refresh token is required."}, status=400)

        # Decode the refresh token
        try:
            payload = jwt.decode(refresh_token_str, SECRET_KEY, algorithms=["HS256"])
            logger.info(f"Decoded JWT payload: {payload} | type: {type(payload)}")
        except jwt.ExpiredSignatureError:
            logger.warning("Refresh token has expired")
            return Response({"error": "Refresh token has expired. Please log in again."}, status=401)
        except jwt.InvalidTokenError as e:
            logger.error(f"Invalid token error: {e}")
            return Response({"error": "Invalid token. Please log in again."}, status=401)

        # Check token type
        if payload.get("token_type") != "refresh":
            logger.warning(f"Incorrect token type: {payload.get('token_type')}")
            return Response({"error": "Invalid token type."}, status=400)

        user_id = payload.get("user_id")
        logger.info(f"User ID from token payload: {user_id} | type: {type(user_id)}")

        if not user_id:
            logger.warning("No user_id found in token payload")
            return Response({"error": "Invalid token payload."}, status=400)

        # Convert user_id to ObjectId if needed
        try:
            if not isinstance(user_id, ObjectId):
                user_id = ObjectId(user_id)
            logger.info(f"Converted user_id to ObjectId: {user_id} | type: {type(user_id)}")
        except bson_errors.InvalidId as e:
            logger.error(f"Invalid user_id format: {user_id} | Error: {e}")
            return Response({"error": "Invalid user ID format in token."}, status=400)

        # Fetch user from DB
        try:
            user = users_collection.find_one({"_id": user_id})
            logger.info(f"Fetched user from DB: {user}")
        except Exception as e:
            logger.error(f"Database error fetching user: {e}")
            return Response({"error": "Server error fetching user."}, status=500)

        if not user:
            logger.warning(f"User not found for ID: {user_id}")
            return Response({"error": "User not found."}, status=404)

        # Generate new tokens
        # Use custom JWT helpers instead of RefreshToken.for_user so we don't
        # rely on Django's ORM/user model for token creation (we use MongoDB users).
        new_access_token = generate_access_token(str(user_id), user.get("role", "user"))
        new_refresh_token = generate_refresh_token(str(user_id))

        response_data = {
            "access": new_access_token,
            "refresh": new_refresh_token,
        }
        logger.info(f"Returning new tokens: {response_data}")

        return Response(response_data, status=200)

    except Exception as e:
        logger.exception(f"Unexpected error in refresh_token: {e}")
        return Response({"error": "Unexpected server error."}, status=500)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_current_user(request):
    """
    Fetches the profile of the currently authenticated user.
    Includes detailed debugging logs for user ID/type issues.
    """
    try:
        logger.info("Fetching current user profile")
        logger.info(f"request.user: {request.user} | type: {type(request.user)}")

        # Get user ID
        try:
            user_id = getattr(request.user, "_id", None) or getattr(request.user, "id", None)
            logger.info(f"Raw user_id from request.user: {user_id} | type: {type(user_id)}")
            
            if not isinstance(user_id, ObjectId):
                user_id = ObjectId(user_id)
                logger.info(f"Converted user_id to ObjectId: {user_id} | type: {type(user_id)}")
        except Exception as e:
            logger.error(f"Error converting user_id: {e}")
            return Response({"error": "Invalid user ID."}, status=400)

        # Fetch user from DB
        try:
            user = users_collection.find_one({"_id": user_id})
            logger.info(f"Fetched user from DB: {user}")
        except Exception as e:
            logger.error(f"Database fetch error: {e}")
            return Response({"error": "Server error fetching user profile."}, status=500)

        if not user:
            logger.warning(f"User account not found or deactivated for ID: {user_id}")
            return Response({"error": "User account not found or deactivated."}, status=404)

        # Return user profile
        return Response({
            "id": str(user["_id"]),
            "username": user.get("username", ""),
            "email": user.get("email", ""),
            "phone_number": user.get("phone_number"), 
            "role": user.get("role", "user"),
            "is_verified": user.get("is_verified", False),
            "created_at": user.get("created_at")
        }, status=200)

    except Exception as e:
        logger.exception(f"Unexpected error in get_current_user: {e}")
        return Response({"error": "Unexpected server error."}, status=500)



#--------------------------------------
#-----------------------------------
#----------------------------------------------
#.......LOGIC GAS ORDER..........
#----------------------------------------------------
#-----------------------------------------------------------------
#----------------------------------------------------------------------------------


# views.py (Django + DRF)
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from bson import ObjectId
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

# Assuming these are imported / available:
# products_collection, drivers_collection, gas_orders_collection



from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from bson import ObjectId
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


from datetime import datetime
from bson import ObjectId
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from db import users_collection, products_collection, gas_orders
from paynow import Paynow

# Paynow initialization
paynow = Paynow(
    '22231',
    '191b4024-b653-42d9-9199-3b20fa5c894c',
    'http://localhost:8000/paynow/update',
    'http://localhost:8000/return?gateway=paynow'
)

DEFAULT_PRICE_PER_KG = 2.0  # fallback price per kg

# ----------------- Helpers -----------------
def safe_float(value, default=0.0):
    try:
        return float(value)
    except (ValueError, TypeError):
        return default

def safe_int(value, default=0):
    try:
        return int(value)
    except (ValueError, TypeError):
        return default

def serialize_objectid(obj):
    """Recursively convert ObjectId to string in a dict."""
    if isinstance(obj, dict):
        return {k: serialize_objectid(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [serialize_objectid(i) for i in obj]
    elif isinstance(obj, ObjectId):
        return str(obj)
    return obj

# ----------------- Main Endpoint -----------------
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from bson import ObjectId
from datetime import datetime
from db import users_collection, products_collection, gas_orders, global_config
from .utils import safe_float, safe_int, serialize_objectid, DEFAULT_PRICE_PER_KG
import paynow

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def start_gas_order(request):
    try:
        user_id = str(request.user.id)

        # ---------- Fetch verified user ----------
        user_doc = users_collection.find_one({"_id": ObjectId(user_id), "is_verified": True})
        if not user_doc:
            return Response(
                {"error": "User not verified. Please complete registration before ordering."},
                status=403
            )

        data = request.data or {}

        # ---------- Use order-specific name/phone if provided ----------
        customer_name = data.get("customer_name") or user_doc.get("name") or user_doc.get("username") or "Unknown"
        customer_phone = data.get("phone") or user_doc.get("phone_number") or "N/A"
        user_email = user_doc.get("email", "noemail@example.com")

        # ---------- Required fields ----------
        required_fields = ["product_id", "delivery_address", "payment_method"]
        for field in required_fields:
            if not data.get(field):
                return Response({"error": f"{field} is required."}, status=400)

        # ---------- Validate product ----------
        product_id = str(data.get("product_id"))
        if not ObjectId.is_valid(product_id):
            return Response({"error": "product_id must be valid."}, status=400)

        product = products_collection.find_one({"_id": ObjectId(product_id)})
        if not product:
            return Response({"error": "Product not found."}, status=404)

        # ---------- Weight & Quantity ----------
        is_custom = data.get("is_custom", False)
        if is_custom:
            weight = safe_float(data.get("custom_weight", 1))
            quantity = safe_int(data.get("custom_cylinders", 1), 1)
        else:
            quantity = safe_int(data.get("quantity", 1), 1)
            raw_weight = str(product.get("weight", "1kg"))
            weight_value = ''.join(ch for ch in raw_weight if ch.isdigit() or ch == '.')
            weight = safe_float(weight_value, 1)

        # ---------- Total Price (Refined to use global price) ----------
        config = global_config.find_one({"_id": "global_config"})
        if config and "product_prices" in config:
            unit_price = safe_float(config["product_prices"].get(product.get("name")), DEFAULT_PRICE_PER_KG)
        else:
            unit_price = safe_float(product.get("price_per_kg"), DEFAULT_PRICE_PER_KG)

        delivery_surcharge = safe_float(data.get("delivery_surcharge", product.get("surcharge", 0)))
        total_price = round(quantity * weight * unit_price + delivery_surcharge, 2)

        # ---------- Payment ----------
        payment_method = str(data.get("payment_method", "")).strip().lower()
        if payment_method not in ["cash", "paynow", "ecocash", "onemoney"]:
            return Response({"error": "Invalid payment method."}, status=400)

        payment_status = "pending" if payment_method != "cash" else "unpaid"

        # ---------- Order Document ----------
        now_utc = datetime.utcnow()
        order_doc = {
            "customer_id": ObjectId(user_id),
            "customer_name": customer_name,
            "customer_phone": customer_phone,
            "product_id": ObjectId(product_id),
            "product_name": product.get("name"),
            "quantity": quantity,
            "weight": weight * quantity,
            "unit_price": unit_price,
            "total_price": total_price,
            "delivery_address": data.get("delivery_address"),
            "delivery_type": data.get("delivery_type", "home_delivery"),
            "payment_method": payment_method,
            "payment_status": payment_status,
            "order_status": "pending",
            "notes": str(data.get("notes", "")).strip(),
            "delivery_surcharge": delivery_surcharge,
            "created_at": now_utc,
            "updated_at": now_utc,
        }

        # ---------- Insert Order ----------
        inserted = gas_orders.insert_one(order_doc)
        order_id = str(inserted.inserted_id)
        order_doc["_id"] = order_id

        # ---------- Prepare Response ----------
        response_data = {
            "success": True,
            "message": "Order created successfully.",
            "order_id": order_id,
            "order": serialize_objectid(order_doc),
            "payment_method": payment_method,
            "payment_status": payment_status,
            "total_price": total_price
        }

        # ---------- Paynow Integration ----------
        if payment_method == "paynow":
            if total_price < 1:
                return Response({"error": "Total price must be at least 1 for Paynow payments."}, status=400)
            try:
                payment = paynow.create_payment(f"Gas Order #{order_id}", user_email)
                payment.add(product.get("name", "Gas Refill"), total_price)
                response = paynow.send(payment)
                if response.success:
                    response_data["paynow"] = {
                        "redirect_url": response.redirect_url,
                        "poll_url": response.poll_url
                    }
                    gas_orders.update_one(
                        {"_id": ObjectId(order_id)},
                        {"$set": {"paynow_poll_url": response.poll_url}},
                    )
                else:
                    return Response({"error": "Failed to initiate Paynow payment."}, status=503)
            except Exception as e:
                return Response({"error": f"Paynow initiation failed: {str(e)}"}, status=500)

        # ---------- Ecocash / OneMoney ----------
        elif payment_method in ["ecocash", "onemoney"]:
            merchant_number = "263772886728"
            gas_orders.update_one(
                {"_id": ObjectId(order_id)},
                {"$set": {"merchant_number": merchant_number}}
            )
            response_data["merchant_number"] = merchant_number

        return Response(response_data, status=201)

    except Exception as e:
        print("❌ start_gas_order error:", e)
        return Response({"error": str(e)}, status=500)





# Assuming you have all necessary imports (ObjectId, datetime, paynow)

from datetime import datetime
from bson import ObjectId
from rest_framework.decorators import api_view, permission_classes
from django.views.decorators.csrf import csrf_exempt

from rest_framework.response import Response
from rest_framework import status

# Assuming these are already defined/imported elsewhere:
# from your_project.paynow_setup import paynow
# from your_project.db import gas_orders

@api_view(['GET', 'POST'])
@permission_classes([])  # Allow all (Paynow needs to access it)
@csrf_exempt
def paynow_update_view(request):
    """
    Handles Paynow payment result notifications.
    Supports both GET and POST to accommodate Paynow callback behavior.
    """

    try:
        # ------------------------------------------------------------------
        # 1. Collect incoming data (POST preferred; fallback to GET)
        # ------------------------------------------------------------------
        data = request.data if request.method == 'POST' else request.query_params
        data_dict = {k.lower(): v for k, v in data.items()}  # normalize keys

        print("🔔 Paynow callback received:", data_dict)

        # ------------------------------------------------------------------
        # 2. Validate essential parameters (case-insensitive)
        # ------------------------------------------------------------------
        reference = data_dict.get('reference')
        paynow_ref = data_dict.get('paynowreference') or data_dict.get('pollurl')

        if not reference or not paynow_ref:
            return Response(
                {
                    "error": "Missing essential Paynow parameters.",
                    "received": data_dict,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # ------------------------------------------------------------------
        # 3. Extract Order ID from reference string
        # ------------------------------------------------------------------
        try:
            # e.g. "Gas Order #652f3a8ebd..." → extract last part
            order_id_str = reference.split('#')[-1].strip()
            order_object_id = ObjectId(order_id_str)
        except Exception:
            print(f"⚠️ Invalid order reference format: {reference}")
            return Response(
                {"message": "Invalid order reference format."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # ------------------------------------------------------------------
        # 4. Fetch order from database
        # ------------------------------------------------------------------
        order = gas_orders.find_one({"_id": order_object_id})
        if not order:
            print(f"⚠️ Order not found: {order_id_str}")
            return Response(
                {"message": "Order not found in database."},
                status=status.HTTP_404_NOT_FOUND,
            )

        # ------------------------------------------------------------------
        # 5. Verify transaction with Paynow
        # ------------------------------------------------------------------
        verification_response = paynow.check_transaction_status(paynow_ref)
        print("✅ Paynow verification response:", vars(verification_response))

        if not verification_response.success:
            print(f"❌ Paynow verification failed: {verification_response.error}")
            return Response(
                {"error": "Paynow verification failed during check."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # ------------------------------------------------------------------
        # 6. Determine new payment and order status
        # ------------------------------------------------------------------
        status_text = verification_response.status  # e.g. 'Paid', 'Cancelled'
        if status_text == 'Paid':
            new_payment_status = 'paid'
            new_order_status = 'processing'
        else:
            new_payment_status = status_text.lower()
            new_order_status = order.get("order_status", "pending")

        # ------------------------------------------------------------------
        # 7. Update order in database
        # ------------------------------------------------------------------
        gas_orders.update_one(
            {"_id": order_object_id},
            {
                "$set": {
                    "payment_status": new_payment_status,
                    "order_status": new_order_status,
                    "paynow_status": status_text,
                    "paynow_transaction_id": paynow_ref,
                    "updated_at": datetime.utcnow(),
                }
            },
        )

        # ------------------------------------------------------------------
        # 8. Return 200 OK so Paynow stops retrying
        # ------------------------------------------------------------------
        return Response(
            {
                "message": f"Payment for Order {order_id_str} processed successfully.",
                "payment_status": new_payment_status,
                "order_status": new_order_status,
            },
            status=status.HTTP_200_OK,
        )

    except Exception as e:
        # ------------------------------------------------------------------
        # 9. Global exception handler
        # ------------------------------------------------------------------
        print("❌ Fatal error in paynow_update_view:", str(e))
        return Response(
            {"error": f"Internal server error: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )



@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_order_status(request, order_id):
    """
    Get the payment status of a gas order.
    """
    try:
        if not ObjectId.is_valid(order_id):
            return Response({"error": "Invalid order ID."}, status=400)

        order = gas_orders.find_one({"_id": ObjectId(order_id)})

        if not order:
            return Response({"error": "Order not found."}, status=404)

        # Return minimal info for frontend polling
        data = {
            "order_id": str(order["_id"]),
            "payment_status": order.get("payment_status", "pending"),
            "order_status": order.get("order_status", "pending"),
        }

        return Response(data, status=200)

    except Exception as e:
        return Response({"error": str(e)}, status=500)









@api_view(['POST'])
@permission_classes([IsAuthenticated])
def finalize_gas_order(request):
    """
    Finalize an order. Accepts either:
      - order_id (draft created earlier) + assigned_driver_id + final_price
      - or no order_id and will create an order from provided data.
    Validates product & driver exist, persists the order, returns order_id.
    """
    user = request.user
    data = request.data or {}

    required = ["product_id", "delivery_address", "payment_method", "assigned_driver_id", "final_price"]
    for field in required:
        if not data.get(field):
            return Response({"error": f"{field} is required to finalize the order."}, status=400)

    # Validate numeric fields
    try:
        total_price = float(data["final_price"])
        quantity = int(data.get("quantity", 1))
    except (TypeError, ValueError):
        return Response({"error": "Invalid format for final_price or quantity."}, status=400)

    if total_price <= 0 or quantity <= 0:
        return Response({"error": "Price and quantity must be positive."}, status=400)

    product_id_raw = data.get("product_id")
    driver_id_raw = data.get("assigned_driver_id")

    product_id_str = str(product_id_raw)
    driver_id_str = str(driver_id_raw)

    if not ObjectId.is_valid(product_id_str):
        return Response({"error": "product_id must be a valid id string."}, status=400)
    if not ObjectId.is_valid(driver_id_str):
        return Response({"error": "assigned_driver_id must be a valid id string."}, status=400)

    try:
        # Verify product & driver existence
        product = products_collection.find_one({"_id": ObjectId(product_id_str)})
        if not product:
            return Response({"error": "Selected product not found."}, status=404)

        driver = drivers_collection.find_one({"_id": ObjectId(driver_id_str)})
        if not driver:
            return Response({"error": "Selected driver not found or is unavailable."}, status=404)

        now_utc = datetime.utcnow()

        # If frontend passed a draft order_id, update it; otherwise create a new order
        order_id_from_client = data.get("order_id")
        if order_id_from_client and ObjectId.is_valid(str(order_id_from_client)):
            # Update existing draft (best-effort)
            oid = ObjectId(str(order_id_from_client))
            update_doc = {
                "$set": {
                    "assigned_driver_id": ObjectId(driver_id_str),
                    "quantity": quantity,
                    "unit_price": (total_price / quantity) if quantity > 0 else 0,
                    "total_price": total_price,
                    "payment_method": data["payment_method"],
                    "payment_status": "pending",
                    "order_status": "assigned",
                    "notes": data.get("notes", "").strip(),
                    "updated_at": now_utc,
                }
            }
            gas_orders_collection.update_one({"_id": oid}, update_doc)
            final_order_id = str(oid)
        else:
            # Create a new final order record
            base_weight = product.get("weight", 1)
            unit_price = (total_price / quantity) if quantity > 0 else 0
            order_doc = {
                "customer_id": ObjectId(str(user.id)),
                "customer_name": user.get("name") or user.get("username"),
                "customer_phone": user.get("phone_number"),
                "product_id": ObjectId(product_id_str),
                "vendor_id": product.get("vendor_id"),
                "assigned_driver_id": ObjectId(driver_id_str),
                "quantity": quantity,
                "unit_price": unit_price,
                "total_price": total_price,
                "delivery_address": data["delivery_address"].strip(),
                "delivery_type": data.get("delivery_type", "home_delivery"),
                "payment_method": data["payment_method"],
                "payment_status": "pending",
                "order_status": "assigned",
                "notes": data.get("notes", "").strip(),
                "weight": base_weight * quantity,
                "created_at": now_utc,
                "updated_at": now_utc,
            }
            inserted = gas_orders_collection.insert_one(order_doc)
            final_order_id = str(inserted.inserted_id)

        # (Optional) trigger async notifications / worker to notify driver
        # notify_driver_async(driver_id_str, final_order_id)

        return Response({
            "message": "Order successfully finalized and assigned to driver.",
            "order_id": final_order_id,
            "order_status": "assigned",
            "final_price": total_price
        }, status=201)

    except Exception as e:
        logger.exception("Error finalizing order")
        return Response({"error": "Failed to finalize order due to a server error.", "details": str(e)}, status=500)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_user_orders(request):
    user = request.user

    try:
        limit = min(int(request.query_params.get('limit', 10)), 50)
        skip = max(int(request.query_params.get('skip', 0)), 0)
    except ValueError:
        return Response({"error": "Invalid pagination params."}, status=400)

    try:
        customer_id = ObjectId(str(user.id))
        orders_cursor = gas_orders.find({"customer_id": customer_id}).sort("created_at", -1).skip(skip).limit(limit)
        total_orders = gas_orders.count_documents({"customer_id": customer_id})

        orders = []
        for order in orders_cursor:
            driver = None
            if order.get("assigned_driver_id"):
                driver = drivers_collection.find_one({"_id": ObjectId(order["assigned_driver_id"])})
            orders.append({
                "order_id": str(order.get("_id")),
                "customer_id": str(order.get("customer_id")),
                "product_id": str(order.get("product_id")) if order.get("product_id") else None,
                "quantity": order.get("quantity"),
                "unit_price": order.get("unit_price") or (driver.get("price_per_kg") if driver else 2),
                "total_price": order.get("total_price"),
                "order_status": order.get("order_status"),
                "delivery_address": order.get("delivery_address"),
                "scheduled_time": order.get("scheduled_time"),
                "payment_method": order.get("payment_method"),
                "payment_status": order.get("payment_status"),
                "assigned_driver_id": str(order.get("assigned_driver_id")) if order.get("assigned_driver_id") else None,
                "driver": {
                    "driver_id": str(driver["_id"]),
                    "username": driver.get("username"),
                    "phone": driver.get("phone"),
                    "vehicle_number": driver.get("vehicle_number"),
                    "vehicle_color": driver.get("vehicle_color")
                } if driver else None,
                "notes": order.get("notes"),
                "driver_surcharge": order.get("driver_surcharge", 0),
                "weight": order.get("weight", 1),
                "created_at": safe_datetime(order.get("created_at")),
                "updated_at": safe_datetime(order.get("updated_at"))
            })

        return Response({
            "message": "User orders retrieved successfully.",
            "total_count": total_orders,
            "page_limit": limit,
            "page_skip": skip,
            "has_more": skip + len(orders) < total_orders,
            "orders": orders
        }, status=200)

    except Exception as e:
        print(">>> Exception in list_user_orders:", e)
        return Response({"error": "Failed to fetch orders.", "details": str(e)}, status=500)



@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_order_detail(request, order_id):
    user = request.user
    
    try:
        # 1. Convert order_id to ObjectId
        try:
            oid = ObjectId(order_id)
        except Exception: # Use a generic exception for invalid ObjectId
            return Response({"error": "Invalid order ID format"}, status=400)

        # 2. Fetch order
        order = db.gas_orders.find_one({"_id": oid})
        if not order:
            return Response({"error": "Order not found"}, status=404)

        # 3. CRITICAL: Authorization Check (The order MUST belong to the user)
        # Compare the stored customer_id (ObjectId) to the authenticated user's ID (string from token)
        if str(order["customer_id"]) != str(user.id):
            return Response({"error": "You do not have permission to view this order"}, status=403)

        # 4. Data Enrichment (Fetch product info)
        product = db.products.find_one({"_id": order["product_id"]})
        product_name = product.get("name") if product else "Unknown Product"

        # 5. Prepare and Serialize Response
        order_detail = {
            "order_id": str(order["_id"]),
            "product_name": product_name,
            "product_id": str(order["product_id"]),
            "quantity": order["quantity"],
            "total_price": order["total_price"],
            "unit_price": order["unit_price"],
            "delivery_address": order["delivery_address"],
            "order_status": order["order_status"],
            # 💡 Serialize datetime objects to ISO format
            "created_at": order.get("created_at").isoformat() if isinstance(order.get("created_at"), datetime) else None,
            "updated_at": order.get("updated_at").isoformat() if isinstance(order.get("updated_at"), datetime) else None,
        }

        return Response({"order": order_detail}, status=200)

    except Exception as e:
        # ⚠️ Log full traceback for server-side debugging
        print(f"Error fetching order detail for ID {order_id}: {e}")
        return Response({"error": "Failed to fetch order details due to a server error."}, status=500)






# --- 1. Notification Helper Function (Async is best for production) ---
def send_notification(user_id, type_, message, order_id=None):
    """
    Saves a notification to the database using UTC time.
    In production, this should be executed asynchronously (e.g., Celery).
    """
    try:
        notifications.insert_one({
            "user_id": ObjectId(user_id),
            "type": type_,
            "message": message,
            "order_id": ObjectId(order_id) if order_id else None,
            "read": False,
            "created_at": datetime.utcnow() # 🔴 CRITICAL: Use UTC
        })
        # Note: We don't return anything since this is usually fire-and-forget/async
    except Exception as e:
        # ⚠️ Log this failure, but don't stop the primary transaction (the order update)
        print(f"ASYNC ERROR: Failed to create notification for user {user_id}: {e}")
        pass # Continue processing the main request

# --- 2. Endpoint to Update Order Status (For Driver/Admin use) ---
@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def update_order_status(request, order_id):
    user = request.user
    
    # ⚠️ For a production app, you'd check user roles here: 
    # if user.role not in ["driver", "superadmin"]: return Response(...)
    
    data = request.data
    new_status = data.get("order_status")

    allowed_statuses = ["assigned", "out_for_delivery", "delivered", "cancelled"] 
    
    if not new_status or new_status not in allowed_statuses:
        return Response({"error": f"Invalid order_status. Allowed: {allowed_statuses}"}, status=400)

    try:
        oid = ObjectId(order_id)
    except:
        return Response({"error": "Invalid order ID format"}, status=400)

    try:
        # Fetch order and verify authorization to update
        order = gas_orders.find_one({"_id": oid})
        if not order:
            return Response({"error": "Order not found"}, status=404)

        # 🔴 CRITICAL: Permission check: Only the assigned driver or an admin can update
        assigned_driver_id = order.get("assigned_driver_id")
        if str(user.id) != str(assigned_driver_id) and user.get("role") != "superadmin":
             return Response({"error": "Unauthorized to update this order's status."}, status=403)
             
        # Update order status and timestamp
        now_utc = datetime.utcnow() # 🔴 CRITICAL: Use UTC
        
        gas_orders.update_one(
            {"_id": oid},
            {"$set": {"order_status": new_status, "updated_at": now_utc}} # Store datetime object
        )

        # Send notifications (Customer and Driver/Admin)
        send_notification(
            user_id=order["customer_id"],
            type_="order_status",
            message=f"Your order {order_id} status has been updated to '{new_status}'.",
            order_id=order_id
        )

        if assigned_driver_id:
            send_notification(
                user_id=assigned_driver_id,
                type_="order_status",
                message=f"Order {order_id} you are assigned to is now '{new_status}'.",
                order_id=order_id
            )

        return Response({
            "message": f"Order status updated to {new_status} and notifications sent",
            "order_id": order_id
        }, status=200)

    except Exception as e:
        # ⚠️ Replace with production logging
        return Response({"error": "Failed to update order status", "details": str(e)}, status=500)


# --- 3. Endpoint for Customer to Cancel Order ---
@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def cancel_order(request, order_id):
    user = request.user
    
    try:
        oid = ObjectId(order_id)
    except:
        return Response({"error": "Invalid order ID format"}, status=400)

    try:
        order = gas_orders.find_one({"_id": oid})
        if not order:
            return Response({"error": "Order not found"}, status=404)

        # 🔴 CRITICAL: Authorization Check (User must own the order)
        if str(order["customer_id"]) != str(user.id):
            return Response({"error": "You are not allowed to cancel this order"}, status=403)

        # Check if the status allows cancellation (must be 'assigned' or 'pending')
        cancellable_statuses = ["assigned", "pending"]
        if order["order_status"] not in cancellable_statuses:
            return Response({"error": f"Order cannot be cancelled. Status: {order['order_status']}"}, status=400)

        # Update status to cancelled
        now_utc = datetime.utcnow()
        gas_orders.update_one(
            {"_id": oid},
            {"$set": {"order_status": "cancelled", "updated_at": now_utc}}
        )

        # Send notifications
        assigned_driver_id = order.get("assigned_driver_id")
        if assigned_driver_id:
            send_notification(
                user_id=assigned_driver_id,
                type_="order_cancelled",
                message=f"Order {order_id} has been cancelled by the customer.",
                order_id=order_id
            )

        send_notification(
            user_id=order["customer_id"],
            type_="order_cancelled",
            message=f"Your order {order_id} has been successfully cancelled.",
            order_id=order_id
        )

        return Response({
            "message": "Order cancelled successfully and notifications sent",
            "order_id": order_id
        }, status=200)

    except Exception as e:
        # ⚠️ Replace with production logging
        return Response({"error": "Failed to cancel order", "details": str(e)}, status=500)


# --- 4. Notification Serializer (Needed for consistent output format) ---
# NOTE: This should typically be in a separate 'serializers.py' file.
class NotificationSerializer(serializers.Serializer):
    notification_id = serializers.CharField(source='_id') # Map _id to notification_id
    type = serializers.CharField()
    message = serializers.CharField()
    order_id = serializers.CharField(allow_null=True, required=False)
    read = serializers.BooleanField()
    created_at = serializers.DateTimeField() # DRF handles datetime objects in the serializer

# --- 5. Endpoint to List User Notifications ---
@api_view(['GET'])
@permission_classes([IsAuthenticated]) # 🔴 CRITICAL: Enforce authentication
def get_user_notifications(request):
    user = request.user
    
    try:
        user_id = str(user.id) # Use standard ID access
        unread_only = request.GET.get("unread", "false").lower() == "true"

        query = {"user_id": ObjectId(user_id)}
        if unread_only:
            query["read"] = False

        # Limit and skip for performance, though not requested, is a good idea here too.
        cursor = notifications.find(query).sort("created_at", -1)
        
        # Use the serializer for clean, consistent output formatting
        notif_list = list(cursor)
        
        # Manually convert ObjectId to str for the serializer 'source' mapping
        for n in notif_list:
            n['_id'] = str(n['_id'])
            if n.get('order_id'):
                n['order_id'] = str(n['order_id'])
                
        serializer = NotificationSerializer(notif_list, many=True)
        return Response({"notifications": serializer.data}, status=200)

    except Exception as e:
        # ⚠️ Replace with production logging
        return Response({"error": "Failed to fetch notifications", "details": str(e)}, status=500)


# --- 6. Endpoint to Mark a Single Notification as Read ---
@api_view(['PATCH'])
@permission_classes([IsAuthenticated]) # 🔴 CRITICAL: Enforce authentication
def mark_notification_read(request, notification_id):
    user = request.user
    
    try:
        oid = ObjectId(notification_id)
    except:
        return Response({"error": "Invalid notification ID"}, status=400)

    try:
        # Filter by both ID and user_id to prevent IDOR vulnerability
        update_result = notifications.update_one(
            {"_id": oid, "user_id": ObjectId(str(user.id))}, 
            {"$set": {"read": True}}
        )

        if update_result.matched_count == 0:
            return Response({"error": "Notification not found or access denied"}, status=404)

        return Response({"message": "Notification marked as read"}, status=200)

    except Exception as e:
        # ⚠️ Replace with production logging
        return Response({"error": "Failed to mark notification as read", "details": str(e)}, status=500)


# --- 7. Endpoint to Mark All Notifications Read ---
@api_view(['PATCH'])
@permission_classes([IsAuthenticated]) # 🔴 CRITICAL: Enforce authentication
def mark_all_notifications_read(request):
    user = request.user
    
    try:
        unread_only = request.data.get("unread_only", True)
        
        query = {"user_id": ObjectId(str(user.id))}
        if unread_only:
            query["read"] = False

        result = notifications.update_many(query, {"$set": {"read": True}})
        return Response({"message": f"{result.modified_count} notification(s) marked as read"}, status=200)

    except Exception as e:
        # ⚠️ Replace with production logging
        return Response({"error": "Failed to mark notifications as read", "details": str(e)}, status=500)




















# Helper function to send notification
def send_notification(user_id, type_, message, order_id=None):
    notifications.insert_one({
        "user_id": ObjectId(user_id),
        "type": type_,
        "message": message,
        "order_id": ObjectId(order_id) if order_id else None,
        "read": False,
        "created_at": datetime.now(LOCAL_TZ).isoformat()
    })











#..................................................................................................................
#Drivers Logic
#......................................................................................................................
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from bson import ObjectId
import traceback

@api_view(['GET'])
@permission_classes([AllowAny])  # ✅ Allow anyone to access
def get_driver_profile(request, driver_id):
    """
    Fetch the profile of a specific driver by ID.
    No authentication required — just needs a valid driver ID.
    """
    try:
        # Validate driver_id format
        try:
            oid = ObjectId(driver_id)
        except Exception:
            return Response({"error": "Invalid driver ID format."}, status=400)

        # Fetch driver from database
        driver = drivers_collection.find_one({"_id": oid})
        if not driver:
            return Response({"error": "Driver not found."}, status=404)

        # Minimal output (only essential fields)
        driver_data = {
            "_id": str(driver["_id"]),
            "username": driver.get("username"),
            "vehicle_number": driver.get("vehicle_number"),
            "vehicle_color": driver.get("vehicle_color"),
            "currentLocation": driver.get("currentLocation", {"lat": 0.0, "lng": 0.0}),
            "speed": driver.get("speed", 0),
            "lastUpdate": driver.get("lastUpdate"),
        }

        return Response({"driver": driver_data}, status=200)

    except Exception:
        print(f"🔥 Error fetching driver profile:\n{traceback.format_exc()}")
        return Response({"error": "Server error fetching driver profile."}, status=500)




# ---------- REGISTER DRIVER ----------


# ---------- REGISTER DRIVER ----------
# ---------- REGISTER DRIVER ----------
# ---------- REGISTER DRIVER ----------

# ---------- REGISTER DRIVER (OTP ONLY, NO PASSWORD) ----------
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.core.mail import EmailMessage
from datetime import datetime, timedelta
import bcrypt, uuid, re, traceback

# Constants
OTP_EXPIRY_MINUTES = 10

# Helper: Validate email
def is_valid_email(email):
    return re.match(r"[^@]+@[^@]+\.[^@]+", email)

# Helper: Generate OTP
def generate_otp():
    from random import randint
    return str(randint(100000, 999999))

# Helper: Send verification email
def dispatch_verification_code(email, otp_code):
    try:
        email = email.strip()
        if not is_valid_email(email):
            return False
        msg = EmailMessage(
            subject="Your Driver Verification Code",
            body=f"Your OTP code is: {otp_code}",
            from_email="no-reply@myapp.com",
            to=[email]
        )
        msg.send(fail_silently=False)
        return True
    except Exception as e:
        print("⚠️ Email sending failed:", e)
        return False


  
# ---------- SIMPLE DRIVER REGISTRATION + PIN + TRACKING ----------
import re
import uuid
import bcrypt
import traceback
from datetime import datetime, timedelta, timezone
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from bson import ObjectId

# --- CONFIGURATION ---
OTP_EXPIRY_MINUTES = 10
MAX_FAILED_ATTEMPTS = 5
LOCKOUT_TIME_MINUTES = 15

# Collections
# pending_drivers_collection
# drivers_collection
# Assumed already defined elsewhere

import secrets
import re
import smtplib
from email.message import EmailMessage

# -------------------------
# OTP GENERATION
# -------------------------
def generate_otp(length=6):
    """
    Generate a numeric OTP of given length using a cryptographically secure method.
    """
    return ''.join(str(secrets.randbelow(10)) for _ in range(length))


# -------------------------
# EMAIL SENDING LOGIC
# -------------------------
def send_email(subject, body, recipient_email, sender_email, sender_password, smtp_server="smtp.gmail.com", smtp_port=587):
    """
    Send an email using SMTP.
    """
    try:
        msg = EmailMessage()
        msg.set_content(body)
        msg['Subject'] = subject
        msg['From'] = sender_email
        msg['To'] = recipient_email

        # Connect and send email
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(sender_email, sender_password)
        server.send_message(msg)
        server.quit()
        print(f"✅ Email sent to {recipient_email}")
        return True
    except Exception as e:
        print(f"❌ Failed to send email to {recipient_email}: {e}")
        return False


# -------------------------
# OTP DISPATCH
# -------------------------
from django.core.mail import send_mail
from django.conf import settings

def dispatch_verification_code(email, otp):
    try:
        subject = "Your LuminaN OTP Verification Code"
        message = f"Hello,\n\nYour verification code is: {otp}\n\nIt will expire in {OTP_EXPIRY_MINUTES} minutes."
        from_email = settings.DEFAULT_FROM_EMAIL
        recipient_list = [email]

        send_mail(subject, message, from_email, recipient_list, fail_silently=False)
        print(f"✅ OTP {otp} sent to {email}")
        return True
    except Exception as e:
        print(f"❌ Failed to send OTP: {e}")
        return False



# -------------------------
# WELCOME EMAIL
# -------------------------
def dispatch_welcome_email(user_email, username):
    """
    Send a welcome email after successful registration.
    """
    subject = "Welcome to LuminaN Driver Network!"
    body = f"Hi {username},\n\nWelcome to LuminaN! Your driver account has been successfully verified.\n\nHappy driving!"
    
    sender_email = "your_email@example.com"
    sender_password = "your_email_password"

    return send_email(subject, body, user_email, sender_email, sender_password)


# -------------------------
# EMAIL VALIDATION
# -------------------------
def is_valid_email(email):
    """
    Simple email validation using regex.
    """
    return re.fullmatch(r"[^@]+@[^@]+\.[^@]+", email) is not None


# ---------- DRIVER REGISTRATION ----------

# ---------- DRIVER REGISTRATION ----------
@api_view(['POST'])
@permission_classes([AllowAny])
def register_driver(request):
    try:
        data = request.data
        print("📩 Received driver registration data:", data)

        # --- Minimal required fields ---
        required_fields = ["username", "email", "pin"]
        for field in required_fields:
            if not data.get(field):
                return Response({"error": f"{field} is required."}, status=400)

        # --- Validate email ---
        if not is_valid_email(data["email"]):
            return Response({"error": "Invalid email address."}, status=400)

        # --- Validate PIN ---
        if not re.fullmatch(r"\d{4,6}", data["pin"]):
            return Response({"error": "PIN must be 4-6 digits."}, status=400)

        # --- Check for duplicates ---
        existing_driver = pending_drivers_collection.find_one({"$or": [
            {"username": data["username"]}, {"email": data["email"]}
        ]}) or drivers_collection.find_one({"$or": [
            {"username": data["username"]}, {"email": data["email"]}
        ]})
        if existing_driver:
            return Response({"error": "Driver already exists."}, status=409)

        # --- Hash PIN ---
        hashed_pin = bcrypt.hashpw(data["pin"].encode(), bcrypt.gensalt()).decode()

        # --- Generate OTP ---
        otp_code = generate_otp()
        otp_expiry = datetime.now(timezone.utc) + timedelta(minutes=OTP_EXPIRY_MINUTES)

        # --- Send OTP email ---
        sent = dispatch_verification_code(data["email"], otp_code)
        if not sent:
            return Response({"error": "Failed to send verification code. Check email configuration."}, status=503)

        # --- Create pending driver record ---
        pending_driver_doc = {
            "username": data["username"],
            "email": data["email"],
            "pin": hashed_pin,
            "otp_code": otp_code,
            "otp_expiry": otp_expiry,
            "is_verified": False,
            "created_at": datetime.now(timezone.utc),
            "failed_attempts": 0,
            "lockout_start": None,
            # Frontend tracking fields
            "currentLocation": {"lat": 0.0, "lng": 0.0},
            "speed": 0,
            "lastUpdate": None,
        }

        inserted_result = pending_drivers_collection.insert_one(pending_driver_doc)

        return Response({
            "success": True,
            "message": "Driver registration initiated. Verification code sent to email.",
            "temp_driver_id": str(inserted_result.inserted_id),
            "verification_type": "email",
            "contact_sent_to": data["email"]
        }, status=202)

    except Exception:
        print(f"🔥 DRIVER REGISTRATION ERROR:\n{traceback.format_exc()}")
        return Response({"error": "Registration failed due to a server error."}, status=500)


# ---------- VERIFY DRIVER OTP ----------
@api_view(['POST'])
@permission_classes([AllowAny])
def verify_driver_otp(request):
    try:
        data = request.data
        required_fields = ["temp_driver_id", "otp_code"]
        for field in required_fields:
            if not data.get(field):
                return Response({"error": f"{field} is required."}, status=400)

        temp_driver_id = data["temp_driver_id"]
        submitted_otp = data["otp_code"]

        # Validate ObjectId
        try:
            driver_id_obj = ObjectId(temp_driver_id)
        except Exception:
            return Response({"error": "Invalid verification ID format."}, status=400)

        # Fetch pending driver
        temp_driver = pending_drivers_collection.find_one({"_id": driver_id_obj})
        if not temp_driver:
            return Response({"error": "Verification session expired or invalid ID."}, status=404)

        # --- Lockout check ---
        failed_attempts = temp_driver.get("failed_attempts", 0)
        if failed_attempts >= MAX_FAILED_ATTEMPTS:
            if not temp_driver.get("lockout_start"):
                pending_drivers_collection.update_one(
                    {"_id": driver_id_obj},
                    {"$set": {"lockout_start": datetime.now(timezone.utc)}}
                )
            return Response({
                "error": f"Too many failed attempts. Try again after {LOCKOUT_TIME_MINUTES} minutes."
            }, status=429)

        # --- OTP expiry check (timezone safe) ---
        otp_expiry = temp_driver.get("otp_expiry")
        if otp_expiry and otp_expiry.tzinfo is None:
            otp_expiry = otp_expiry.replace(tzinfo=timezone.utc)
        if not otp_expiry or datetime.now(timezone.utc) > otp_expiry:
            pending_drivers_collection.delete_one({"_id": driver_id_obj})
            return Response({"error": "Verification code expired. Please re-register."}, status=410)

        # --- OTP match check ---
        if submitted_otp != temp_driver.get("otp_code"):
            pending_drivers_collection.update_one({"_id": driver_id_obj}, {"$inc": {"failed_attempts": 1}})
            return Response({"error": "Invalid verification code."}, status=400)

        # --- OTP correct — finalize driver ---
        final_driver_doc = {
            k: v for k, v in temp_driver.items()
            if k not in ["otp_code", "otp_expiry", "failed_attempts", "_id", "lockout_start"]
        }
        final_driver_doc["is_verified"] = True
        final_driver_doc["verified_at"] = datetime.now(timezone.utc)

        # Insert into permanent collection
        inserted_result = drivers_collection.insert_one(final_driver_doc)
        pending_drivers_collection.delete_one({"_id": driver_id_obj})

        # Optional: send welcome email
        try:
            dispatch_welcome_email(final_driver_doc["email"], final_driver_doc["username"])
        except Exception as e:
            print("⚠️ Failed to send welcome email:", e)

        # Response
        driver_response = {
            "_id": str(inserted_result.inserted_id),
            "username": final_driver_doc.get("username"),
            "email": final_driver_doc.get("email"),
            "is_verified": True,
            "currentLocation": final_driver_doc.get("currentLocation"),
            "speed": final_driver_doc.get("speed"),
            "lastUpdate": final_driver_doc.get("lastUpdate"),
        }

        return Response({"success": True, "message": "Driver verified successfully.", "driver": driver_response}, status=200)

    except Exception:
        print(f"🔥 DRIVER VERIFY ERROR:\n{traceback.format_exc()}")
        return Response({"error": "Unexpected server error during verification."}, status=500)



# ---------- DRIVER AUTH DECORATOR ----------
def driver_authenticated(view_func):
    """
    Decorator to authenticate a driver using Bearer token.
    Adds 'driver' as a kwarg to the view function on success.
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        auth_header = request.headers.get("Authorization", "")
        token = auth_header.replace("Bearer ", "").strip()

        if not token:
            return Response({"error": "Authorization token required"}, status=401)

        driver = drivers_collection.find_one({"auth_token": token})
        if not driver:
            return Response({"error": "Invalid or expired token"}, status=401)

        # Pass the driver object to the view
        return view_func(request, driver=driver, *args, **kwargs)

    return wrapper







# ---------- LOGIN DRIVER ----------
@api_view(['POST'])
@permission_classes([AllowAny])
def login_driver(request):
    try:
        data = request.data
        identifier = data.get("identifier")  # can be username or email
        password = data.get("password")

        if not identifier or not password:
            return Response({"error": "Identifier and password are required"}, status=400)

        # Find driver by username or email
        driver = drivers_collection.find_one({
            "$or": [
                {"username": identifier},
                {"email": identifier}
            ]
        })

        if not driver:
            return Response({"error": "Invalid username/email or password"}, status=401)

        # Check if account is verified
        if not driver.get('is_verified', False):
            return Response({"error": "Account not verified."}, status=403)

        # Verify password
        stored_password = driver.get('password_hash')
        if not stored_password:
            return Response({"error": "Password not set for this account."}, status=500)

        if isinstance(stored_password, str):
            stored_password = stored_password.encode('utf-8')

        if not checkpw(password.encode('utf-8'), stored_password):
            return Response({"error": "Invalid username/email or password"}, status=401)

        # Generate new permanent auth token
        auth_token = secrets.token_hex(32)
        last_login = datetime.utcnow()
        drivers_collection.update_one(
            {"_id": driver["_id"]},
            {"$set": {"auth_token": auth_token, "last_login": last_login}}
        )

        # Build driver response
        driver_resp = {
            "_id": str(driver["_id"]),
            "username": driver.get("username"),
            "email": driver.get("email"),
            "phone": driver.get("phone"),
            "operational_area": driver.get("operational_area"),
            "drivers_licence_number": driver.get("drivers_licence_number"),
            "valid_zimbabwe_id": driver.get("valid_zimbabwe_id"),
            "bio": driver.get("bio"),
            "vehicle_number": driver.get("vehicle_number"),
            "vehicle_color": driver.get("vehicle_color"),
            "role": driver.get("role", "driver"),
            "is_verified": driver.get("is_verified", False),
            "auth_token": auth_token,
            "last_login": last_login
        }

        return Response({"success": True, "driver": driver_resp}, status=200)

    except Exception:
        print(f"🔥 DRIVER LOGIN ERROR:\n{traceback.format_exc()}")
        return Response({"error": "Login failed"}, status=500)





def safe_datetime(dt):
    if not dt:
        return None
    return dt.isoformat() if not isinstance(dt, str) else dt

def get_updated_order(order_id):
    order = gas_orders.find_one({"_id": ObjectId(order_id)})
    if not order:
        return None
    return {
        "order_id": str(order.get("_id")),
        "product_id": str(order.get("product_id")) if order.get("product_id") else None,
        "quantity": order.get("quantity", 0),
        "total_price": order.get("total_price"),
        "weight": order.get("weight", 1),
        "unit_price": order.get("unit_price") or drivers_collection.get("price_per_kg", 2),
        "order_status": order.get("status", "pending"),
        "delivery_address": order.get("delivery_address"),
        "scheduled_time": order.get("scheduled_time"),
        "payment_method": order.get("payment_method"),
        "notes": order.get("notes"),
        "created_at": safe_datetime(order.get("created_at")),
        "updated_at": safe_datetime(order.get("updated_at")),
        "delivered_at": safe_datetime(order.get("delivered_at")),
        "assigned_driver_id": str(order.get("assigned_driver_id")) if order.get("assigned_driver_id") else None,
        "customer_id": str(order.get("customer_id")) if order.get("customer_id") else None
    }

# ---------------- PATCH ENDPOINTS ----------------


from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from bson import ObjectId
from datetime import datetime

@api_view(['PATCH', 'POST'])
@permission_classes([AllowAny])
def confirm_order(request, order_id):
    """
    Confirms an order by a driver.
    Assigns the driver to the order when confirmed.
    """
    try:
        # Validate order ObjectId
        try:
            oid_order = ObjectId(order_id)
        except Exception:
            return Response({"error": "Invalid order ID format"}, status=400)

        # Fetch order
        order = gas_orders.find_one({"_id": oid_order})
        if not order:
            return Response({"error": "Order not found"}, status=404)

        # Get driver_id from request
        driver_id = request.data.get("driver_id")
        if not driver_id:
            return Response({"error": "driver_id is required"}, status=400)

        # Validate driver_id
        try:
            oid_driver = ObjectId(driver_id)
        except Exception:
            return Response({"error": "Invalid driver ID format"}, status=400)

        # Optional: check if driver exists
        driver = drivers_collection.find_one({"_id": oid_driver})
        if not driver:
            return Response({"error": "Driver not found"}, status=404)

        # Check if already confirmed by someone
        if order.get("order_status") == "confirmed":
            return Response({
                "message": "Order is already confirmed",
                "order": get_updated_order(order_id)
            }, status=200)

        # Update order with driver assignment
        gas_orders.update_one(
            {"_id": oid_order},
            {"$set": {
                "order_status": "confirmed",
                "assigned_driver_id": driver_id,
                "updated_at": datetime.now()
            }}
        )

        # Return updated order
        updated_order = get_updated_order(order_id)
        return Response({
            "message": "Order confirmed successfully",
            "order": updated_order
        }, status=200)

    except Exception as e:
        print(f"Error confirming order: {e}")
        return Response({"error": "Failed to confirm order", "details": str(e)}, status=500)



from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from bson import ObjectId
from datetime import datetime

# ---- CANCEL ORDER ----
@api_view(['PATCH', 'POST'])
@permission_classes([AllowAny])
def cancel_order(request, order_id):
    """
    Cancels any order without driver restrictions.
    Anyone can cancel an order.
    """
    try:
        # Validate ObjectId
        try:
            oid_order = ObjectId(order_id)
        except Exception:
            return Response({"error": "Invalid order ID format"}, status=400)

        # Find the order
        order = gas_orders.find_one({"_id": oid_order})
        if not order:
            return Response({"error": "Order not found"}, status=404)

        # If already cancelled
        if order.get("order_status") == "cancelled":
            return Response({
                "message": "Order is already cancelled",
                "order": get_updated_order(order_id)
            }, status=200)

        # Get cancellation reason
        reason = request.data.get("reason", "Cancelled by system")

        # Update the order
        gas_orders.update_one(
            {"_id": oid_order},
            {"$set": {
                "order_status": "cancelled",
                "cancel_reason": reason,
                "updated_at": datetime.now()
            }}
        )

        # Return updated order
        updated_order = get_updated_order(order_id)
        return Response({"message": "Order cancelled successfully", "order": updated_order}, status=200)

    except Exception as e:
        print(f"Error cancelling order: {e}")
        return Response({"error": "Failed to cancel order", "details": str(e)}, status=500)


# ---- MARK DELIVERED ----
@api_view(['PATCH', 'POST'])
@permission_classes([AllowAny])
def mark_delivered(request, order_id):
    """
    Marks any order as delivered without driver restrictions.
    Anyone can mark an order as delivered.
    """
    try:
        # Validate ObjectId
        try:
            oid_order = ObjectId(order_id)
        except Exception:
            return Response({"error": "Invalid order ID format"}, status=400)

        # Find the order
        order = gas_orders.find_one({"_id": oid_order})
        if not order:
            return Response({"error": "Order not found"}, status=404)

        # If already delivered
        if order.get("order_status") == "delivered":
            return Response({
                "message": "Order already marked as delivered",
                "order": get_updated_order(order_id)
            }, status=200)

        # Update the order
        gas_orders.update_one(
            {"_id": oid_order},
            {"$set": {
                "order_status": "delivered",
                "delivered_at": datetime.now(),
                "updated_at": datetime.now()
            }}
        )

        # Return updated order
        updated_order = get_updated_order(order_id)
        return Response({"message": "Order marked as delivered successfully", "order": updated_order}, status=200)

    except Exception as e:
        print(f"Error marking order delivered: {e}")
        return Response({"error": "Failed to mark order as delivered", "details": str(e)}, status=500)



from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from bson import ObjectId
from datetime import datetime, timedelta, timezone # <-- ADDED timezone
import calendar
import math # For isclose in average calculation (though not strictly necessary here, good practice)

# Assuming 'gas_orders' is your MongoDB collection object
# Assuming 'drivers_collection' is your MongoDB collection object

# ---------------- Date Utility Functions (UTC-Aware Fix) ----------------

def start_of_day_utc(dt_utc):
    """Returns the datetime object at the start of the day in UTC."""
    return datetime(dt_utc.year, dt_utc.month, dt_utc.day, 0, 0, 0, tzinfo=timezone.utc)

def start_of_week_utc(dt_utc):
    """Returns the datetime object at the start of the current week (Monday) in UTC."""
    # weekday() returns 0 for Monday, 6 for Sunday
    start_date = dt_utc - timedelta(days=dt_utc.weekday())
    return datetime(start_date.year, start_date.month, start_date.day, 0, 0, 0, tzinfo=timezone.utc)

def start_of_month_utc(dt_utc):
    """Returns the datetime object at the start of the current month in UTC."""
    return datetime(dt_utc.year, dt_utc.month, 1, 0, 0, 0, tzinfo=timezone.utc)

# ---------------- Core Metric Calculation Logic (Enhanced) ----------------
def calculate_metrics_for_driver(driver_id):
    """
    Calculates key performance metrics for a specific driver using MongoDB aggregation.
    Filters orders based on the driver who *accepted* the order (self-assignment model).
    """
    if not driver_id:
        return {"error": "Driver ID is required"}

    try:
        # Renamed variable to reflect driver's acceptance/confirmation
        oid_accepting_driver = ObjectId(driver_id) 
    except Exception:
        return {"error": "Invalid Driver ID format"}

    # Use UTC for all time-based comparisons to match MongoDB BSON Date type
    now_utc = datetime.now(timezone.utc) 
    today_utc = start_of_day_utc(now_utc)
    this_week_utc = start_of_week_utc(now_utc)
    this_month_utc = start_of_month_utc(now_utc)

    # Statuses used
    # This remains correct for calculating *potential* sales that are in progress
    potential_sales_statuses = ["confirmed", "accepted", "picked_up", "in_transit"]
    delivered_status = "delivered"
    canceled_status = "canceled"
    
    # 1. Pipeline to get all orders for the driver
    pipeline = [
        # *** REFINED FILTER: Change 'assigned_driver_id' to 'accepted_driver_id' (or your actual field name) ***
        # This assumes your app writes the accepting driver's ID to a field named 'accepted_driver_id'
        {"$match": {"accepted_driver_id": oid_accepting_driver}}, 
        
        # Add necessary fields and perform preliminary type conversions
        {"$addFields": {
            "total_amount_num": {"$toDouble": {"$ifNull": ["$total_price", 0]}},
            "status_lower": {"$toLower": {"$ifNull": ["$order_status", ""]}},
            "is_potential_sale": {"$in": ["$status_lower", potential_sales_statuses]},
            "is_delivered": {"$eq": ["$status_lower", delivered_status]},
            "is_canceled": {"$eq": ["$status_lower", canceled_status]}, 
            
            "delivery_date": {"$ifNull": ["$delivered_at", None]},
            "order_date": {"$ifNull": ["$created_at", None]},
            # Calculate time difference in seconds for completed orders
            "delivery_duration_seconds": {
                "$cond": [
                    {"$and": [
                        "$is_delivered", 
                        {"$ne": ["$created_at", None]}, 
                        {"$ne": ["$delivered_at", None]}
                    ]},
                    {"$divide": [
                        {"$subtract": ["$delivered_at", "$created_at"]}, 
                        1000
                    ]}, # Convert milliseconds to seconds
                    None
                ]
            }
        }},
        
        # Ensure dates are datetime objects for comparison (Filter out bad data)
        {"$match": {
            "$or": [
                {"order_date": {"$type": 9}},
                {"delivery_date": {"$type": 9}}
            ]
        }},
        
        # Group and calculate metrics
        {"$group": {
            "_id": None,
            "lifetime_assigned_orders": {"$sum": 1}, # Now counts accepted/confirmed orders
            "lifetime_deliveries": {"$sum": {"$cond": ["$is_delivered", 1, 0]}},
            "lifetime_canceled_orders": {"$sum": {"$cond": ["$is_canceled", 1, 0]}}, 
            "lifetime_sales": {"$sum": {"$cond": ["$is_delivered", "$total_amount_num", 0]}}, # Only count delivered sales
            "total_delivery_duration_seconds": {"$sum": {"$ifNull": ["$delivery_duration_seconds", 0]}}, 
            
            # --- Potential Sales (Based on Confirmed/In-Progress Orders) ---
            "daily_potential_sales": {"$sum": {"$cond": [
                {"$and": [
                    {"$gte": ["$order_date", today_utc]}, 
                    {"$lte": ["$order_date", now_utc]}, 
                    "$is_potential_sale"
                ]}, "$total_amount_num", 0
            ]}},
            "weekly_potential_sales": {"$sum": {"$cond": [
                {"$and": [
                    {"$gte": ["$order_date", this_week_utc]},
                    {"$lte": ["$order_date", now_utc]},
                    "$is_potential_sale"
                ]}, "$total_amount_num", 0
            ]}},
            "monthly_potential_sales": {"$sum": {"$cond": [
                {"$and": [
                    {"$gte": ["$order_date", this_month_utc]},
                    {"$lte": ["$order_date", now_utc]},
                    "$is_potential_sale"
                ]}, "$total_amount_num", 0
            ]}},
            
            # --- Actual Deliveries (Based on Delivered Status and delivered_at date) ---
            "daily_deliveries": {"$sum": {"$cond": [
                {"$and": [
                    {"$gte": ["$delivery_date", today_utc]},
                    {"$lte": ["$delivery_date", now_utc]},
                    "$is_delivered"
                ]}, 1, 0
            ]}},
            "weekly_deliveries": {"$sum": {"$cond": [
                {"$and": [
                    {"$gte": ["$delivery_date", this_week_utc]},
                    {"$lte": ["$delivery_date", now_utc]},
                    "$is_delivered"
                ]}, 1, 0
            ]}},
            "monthly_deliveries": {"$sum": {"$cond": [
                {"$and": [
                    {"$gte": ["$delivery_date", this_month_utc]},
                    {"$lte": ["$delivery_date", now_utc]},
                    "$is_delivered"
                ]}, 1, 0
            ]}},
        }}
    ]

    result = list(gas_orders.aggregate(pipeline))

    # --- Rest of the function (Derived Metrics and Output) remains identical ---
    
    if not result:
        # Return zeros if no orders are found for the driver
        return {
            "daily_sales": 0.0, "daily_deliveries": 0,
            "weekly_sales": 0.0, "weekly_deliveries": 0,
            "monthly_sales": 0.0, "monthly_deliveries": 0,
            "lifetime_sales": 0.0, "lifetime_deliveries": 0,
            "total_assigned_orders": 0, "total_canceled_orders": 0,
            "delivery_completion_rate": 0.0, 
            "cancellation_rate": 0.0,
            "average_delivery_time_minutes": 0.0,
        }

    data = result[0]
    
    total_assigned = data.get("lifetime_assigned_orders", 0)
    total_delivered = data.get("lifetime_deliveries", 0)
    total_canceled = data.get("lifetime_canceled_orders", 0)
    total_duration_seconds = data.get("total_delivery_duration_seconds", 0)

    # --- Derived Metrics Calculation ---
    
    # 1. Delivery Completion Rate
    completion_rate = (total_delivered / total_assigned * 100) if total_assigned > 0 else 0.0

    # 2. Cancellation Rate (Canceled vs. Total Assigned)
    cancellation_rate = (total_canceled / total_assigned * 100) if total_assigned > 0 else 0.0

    # 3. Average Delivery Time (in Minutes)
    avg_delivery_time_seconds = (total_duration_seconds / total_delivered) if total_delivered > 0 else 0
    avg_delivery_time_minutes = avg_delivery_time_seconds / 60
    
    # --- Final Output ---
    return {
        # Time-based Metrics
        "daily_sales": round(data.get("daily_potential_sales", 0.0), 2),
        "daily_deliveries": data.get("daily_deliveries", 0),
        
        "weekly_sales": round(data.get("weekly_potential_sales", 0.0), 2),
        "weekly_deliveries": data.get("weekly_deliveries", 0),
        
        "monthly_sales": round(data.get("monthly_potential_sales", 0.0), 2),
        "monthly_deliveries": data.get("monthly_deliveries", 0),
        
        # Lifetime Metrics
        "lifetime_sales": round(data.get("lifetime_sales", 0.0), 2),
        "lifetime_deliveries": total_delivered,
        "total_assigned_orders": total_assigned, 
        "total_canceled_orders": total_canceled, 
        "total_pending_orders": total_assigned - total_delivered - total_canceled, 
        
        # Derived Metrics
        "delivery_completion_rate": round(completion_rate, 2), # %
        "cancellation_rate": round(cancellation_rate, 2), # %
        "average_delivery_time_minutes": round(avg_delivery_time_minutes, 1), # Minutes
    }


# ---------------- DRF API View ----------------

@api_view(['GET'])
@permission_classes([AllowAny]) 
def driver_performance_metrics(request, driver_id):
    
    """
    Retrieves key performance and sales metrics (Daily, Weekly, Monthly, Lifetime)
    for a specific driver.
    """
    try:
        metrics = calculate_metrics_for_driver(driver_id)
        
        if "error" in metrics:
             return Response({"error": metrics["error"]}, status=400)

        return Response({
            "success": True,
            "message": "Driver performance metrics retrieved successfully.",
            "metrics": metrics
        }, status=200)

    except Exception as e:
        # NOTE: In a production environment, use proper logging instead of print()
        print(f"Error retrieving driver performance: {e}")
        return Response({"error": "Failed to retrieve performance data", "details": str(e)}, status=500)





from bson import ObjectId
from bson.errors import InvalidId # Imported for specific error handling
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny

# IMPORTANT: You must ensure 'drivers_collection' and 'gas_orders' 
# are accessible in this scope (e.g., imported from a settings or db file).

# NOTE: The get_updated_order function is assumed to be defined elsewhere and 
# takes only ONE positional argument: order_id.

def get_driver_details(driver_id):
    """
    Fetches essential driver profile details.
    """
    try:
        # 1. Validate ID format
        oid_driver = ObjectId(driver_id) 
    except InvalidId:
        return None 

    # 2. Fetch the driver document
    # NOTE: 'drivers_collection' must be defined/accessible.
    driver_doc = drivers_collection.find_one({"_id": oid_driver}) 

    if not driver_doc:
        return None

    # 3. Format and return
    return {
        "driver_id": str(driver_doc.get("_id")),
        "driver_name": driver_doc.get("username"),
        "phone": driver_doc.get("phone"),
        "vehicle_number": driver_doc.get("vehicle_number"),
        "vehicle_color": driver_doc.get("vehicle_color"),
        "photo_url": driver_doc.get("photo_url"),
    }


# views.py
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from .utils import fetch_order_tracking_data

@api_view(['GET'])
@permission_classes([AllowAny])
def get_order_tracking_details(request, order_id):
    """
    DRF view to return order tracking details.
    """
    data, status_code = fetch_order_tracking_data(order_id)
    return Response(data, status=status_code)



# ---------------- GET ENDPOINT ----------------
# ---------- GET ALL ORDERS FOR DRIVERS (No tokens, no assignment) ----------
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from bson import ObjectId
from datetime import datetime

# ----------------- Helpers -----------------
def safe_float(value, default=0.0):
    if isinstance(value, dict) and "$numberDouble" in value:
        return float(value["$numberDouble"])
    try:
        return float(value)
    except (ValueError, TypeError):
        return default

def safe_int(value, default=0):
    if isinstance(value, dict) and "$numberInt" in value:
        return int(value["$numberInt"])
    try:
        return int(value)
    except (ValueError, TypeError):
        return default

def safe_datetime(dt):
    if not dt:
        return None
    if isinstance(dt, dict) and "$date" in dt and "$numberLong" in dt["$date"]:
        timestamp = int(dt["$date"]["$numberLong"]) / 1000
        return datetime.utcfromtimestamp(timestamp).isoformat()
    if isinstance(dt, datetime):
        return dt.isoformat()
    return str(dt)

# ----------------- Endpoint -----------------
@api_view(['GET'])
@permission_classes([AllowAny])
def driver_assigned_orders(request):
    """
    Fetch all gas orders for drivers with correct numeric parsing and customer/product info.
    """
    try:
        orders_cursor = gas_orders.find()
        orders = []

        for order in orders_cursor:
            # ---------- Numeric Fields ----------
            quantity = safe_int(order.get("quantity"))
            weight = safe_float(order.get("weight"))
            unit_price = safe_float(order.get("unit_price"))
            delivery_surcharge = safe_float(order.get("delivery_surcharge"))
            driver_surcharge = safe_float(order.get("driver_surcharge"))
            total_price = safe_float(order.get("total_price", unit_price * weight * quantity + delivery_surcharge + driver_surcharge))

            # ---------- Product Info ----------
            product_name = order.get("product_name") or "Custom Gas Order"
            product_id = str(order.get("product_id")) if order.get("product_id") else None
            description = order.get("product_description") if order.get("product_name") else order.get("notes", "")

            items = [{
                "product_id": product_id,
                "name": product_name,
                "quantity": quantity,
                "description": description,
                "total_price": total_price,
                "weight": weight,
                "unit_price": unit_price,
                "driver_surcharge": driver_surcharge,
            }]

            # ---------- Customer Info ----------
            customer_id = order.get("customer_id")
            customer_name = order.get("customer_name") or "N/A"
            customer_phone = order.get("customer_phone") or "N/A"
            customer_email = "N/A"
            if customer_id:
                customer_doc = users_collection.find_one({"_id": ObjectId(customer_id)})
                if customer_doc:
                    customer_name = customer_doc.get("username", customer_name)
                    customer_email = customer_doc.get("email", "N/A")

            # ---------- Build Order ----------
            orders.append({
                "order_id": str(order.get("_id")),
                "customer_id": str(customer_id) if customer_id else None,
                "customer": {
                    "name": customer_name,
                    "phone": customer_phone,
                    "email": customer_email,
                },
                "items": items,
                "delivery_address": order.get("delivery_address", "N/A"),
                "delivery_type": order.get("delivery_type", "home_delivery"),
                "notes": order.get("notes", "None"),
                "order_status": order.get("order_status", "pending"),
                "payment_method": order.get("payment_method", "N/A"),
                "payment_status": order.get("payment_status", "pending"),
                "total_price": total_price,
                "scheduled_time": safe_datetime(order.get("scheduled_time")),
                "created_at": safe_datetime(order.get("created_at")),
                "updated_at": safe_datetime(order.get("updated_at")),
                "delivered_at": safe_datetime(order.get("delivered_at")),
                "assigned_driver_id": str(order.get("assigned_driver_id")) if order.get("assigned_driver_id") else None,
                "paynow_poll_url": order.get("paynow_poll_url", None),
            })

        return Response({"orders": orders}, status=200)

    except Exception as e:
        print(">>> Exception in driver_assigned_orders:", e)
        return Response(
            {"error": "Failed to fetch orders", "details": str(e)},
            status=500
        )





from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from bson import ObjectId
from datetime import datetime

# NOTE: 'gas_orders' and 'users_collection' must be globally accessible or passed in the real environment.

# ------------------ Helpers ------------------
def safe_float(value, default=0.0):
    """Safely converts a value (including MongoDB's $numberDouble dict) to a float."""
    try:
        if isinstance(value, dict) and "$numberDouble" in value:
            return float(value["$numberDouble"])
        return float(value)
    except (ValueError, TypeError):
        return default

def safe_int(value, default=0):
    """Safely converts a value (including MongoDB's $numberInt dict) to an integer."""
    try:
        if isinstance(value, dict) and "$numberInt" in value:
            return int(value["$numberInt"])
        return int(value)
    except (ValueError, TypeError):
        return default

def safe_datetime(dt):
    """Safely converts various date formats (including MongoDB $date) to an ISO string."""
    if not dt:
        return None
    if isinstance(dt, dict) and "$date" in dt and "$numberLong" in dt["$date"]:
        # Assuming the date is stored as a milliseconds timestamp
        timestamp = int(dt["$date"]["$numberLong"]) / 1000
        return datetime.utcfromtimestamp(timestamp).isoformat()
    if isinstance(dt, datetime):
        return dt.isoformat()
    return str(dt)

# ------------------ Endpoint ------------------
@api_view(['GET'])
@permission_classes([AllowAny])
def driver_get_order(request, order_id):
    try:
        order_doc = gas_orders.find_one({"_id": ObjectId(order_id)})
        if not order_doc:
            return Response({"error": "Order not found"}, status=404)

        # ---------- Numeric Fields ----------
        quantity = safe_int(order_doc.get("quantity"))
        weight = safe_float(order_doc.get("weight"))
        unit_price = safe_float(order_doc.get("unit_price"))
        delivery_surcharge = safe_float(order_doc.get("delivery_surcharge"))
        
        # REFINEMENT: If total_price is missing, assume price is calculated by unit_price * quantity 
        # (common model for items), NOT by unit_price * weight * quantity, which implies price-per-kg.
        # This reduces the confusion you saw in the financial details.
        default_total = unit_price * quantity + delivery_surcharge
        total_price = safe_float(order_doc.get("total_price", default_total)) 

        # ---------- Items ----------
        # The frontend expects the main product details in order.items[0]
        items = [{
            "product_id": str(order_doc.get("product_id")) if order_doc.get("product_id") else None,
            "name": order_doc.get("product_name", "Custom Gas Order"),
            "quantity": quantity,
            "description": order_doc.get("notes", ""),
            "total_price": total_price,
            "weight": weight,
            "unit_price": unit_price,
            "driver_surcharge": delivery_surcharge,
        }]

        # ---------- Customer Info ----------
        customer_id = order_doc.get("customer_id")
        customer_name = order_doc.get("customer_name", "N/A")
        customer_phone = order_doc.get("customer_phone", "N/A")
        customer_email = "N/A"
        
        # Attempt to enrich customer data from the users collection
        if customer_id:
            try:
                # REFINEMENT: Wrap the ObjectId conversion/lookup to handle potentially invalid IDs gracefully
                customer_doc = users_collection.find_one({"_id": ObjectId(customer_id)})
                if customer_doc:
                    customer_name = customer_doc.get("username", customer_name)
                    customer_email = customer_doc.get("email", "N/A")
            except:
                # Fail silently if the ID is invalid, using the original order data
                pass 

        # ---------- Response ----------
        response = {
            # REFINEMENT: Use order_id as key, and explicitly use the _id value.
            "order_id": str(order_doc.get("_id")), 
            
            # This is the crucial top-level field that the frontend fix relies on
            "customer_id": str(customer_id) if customer_id else None, 
            
            "customer": {
                "name": customer_name,
                "phone": customer_phone,
                "email": customer_email, # Ensured it is always included
            },
            "items": items,
            # Data quality note: Junk values like 'rxtcfyguhin' come from the DB/data entry, not this API
            "delivery_address": order_doc.get("delivery_address", "N/A"), 
            "delivery_type": order_doc.get("delivery_type", "home_delivery"),
            "notes": order_doc.get("notes", "None"),
            "order_status": order_doc.get("order_status", "pending"),
            "payment_method": order_doc.get("payment_method", "N/A"),
            "payment_status": order_doc.get("payment_status", "pending"),
            "total_price": total_price,
            
            # REFINEMENT: Include delivery_surcharge at the top level for Financial Details
            "delivery_surcharge": delivery_surcharge, 

            "scheduled_time": safe_datetime(order_doc.get("scheduled_time")),
            "created_at": safe_datetime(order_doc.get("created_at")),
            "updated_at": safe_datetime(order_doc.get("updated_at")),
            "delivered_at": safe_datetime(order_doc.get("delivered_at")),
            "assigned_driver_id": str(order_doc.get("assigned_driver_id")) if order_doc.get("assigned_driver_id") else None,
            "paynow_poll_url": order_doc.get("paynow_poll_url", None),
        }

        return Response(response, status=200)

    except Exception as e:
        # This is the correct error handling block
        return Response({"error": "Failed to fetch order", "details": str(e)}, status=500)











from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from datetime import datetime

@api_view(['PATCH'])
@permission_classes([AllowAny])
def set_price_per_kg(request):
    """
    Open endpoint to set price_per_kg for a driver.
    WARNING: No authentication is performed.
    """
    try:
        price_per_kg_raw = request.data.get("price_per_kg")
        print("Raw price_per_kg from request:", price_per_kg_raw)

        if price_per_kg_raw is None:
            return Response({"error": "price_per_kg is required"}, status=400)

        # Convert to float safely
        try:
            price_per_kg = float(price_per_kg_raw)
        except (ValueError, TypeError):
            return Response({"error": "price_per_kg must be a number"}, status=400)

        if price_per_kg <= 0:
            return Response({"error": "price_per_kg must be greater than 0"}, status=400)

        # NOTE: Replace this with a specific driver ID or logic since no auth
        driver_id = request.data.get("driver_id")
        if not driver_id:
            return Response({"error": "driver_id is required"}, status=400)

        print(f"Updating driver {driver_id} price_per_kg to {price_per_kg}...")
        drivers_collection.update_one(
            {"_id": driver_id},
            {"$set": {"price_per_kg": price_per_kg, "updated_at": datetime.now()}}
        )

        print("Price update successful")
        return Response(
            {"message": "Price per kg updated successfully", "price_per_kg": price_per_kg},
            status=200
        )

    except Exception as e:
        print("Exception occurred while setting price_per_kg:", str(e))
        return Response({"error": "Failed to set price", "details": str(e)}, status=500)





#____________________________________________
#Admin 
#______________________________








# --- Main register route











@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_admin(request):
    """
    Logs out the current admin (invalidates auth token)
    """
    try:
        admin_email = request.user.get("email")

        # Invalidate token
        admins_collection.update_one(
            {"email": admin_email},
            {"$set": {
                "auth_token": None,
                "last_logout": datetime.utcnow()
            }}
        )

        # Log the event
        log_admin_activity(
            admin_email,
            "logout_admin",
            "success",
            {"ip": request.META.get("REMOTE_ADDR")}
        )

        return Response({"message": "Logout successful"}, status=200)

    except Exception as e:
        log_admin_activity(
            request.user.get("email", "unknown"),
            "logout_admin",
            "failed",
            {"error": str(e)}
        )
        return Response({"error": "Logout failed", "details": str(e)}, status=500)








@api_view(['GET'])
@permission_classes([IsAuthenticated])
def system_overview(request):
    """
    Admin Dashboard Overview - real-time system stats.
    """
    try:
        total_users = users_collection.count_documents({})
        verified_users = users_collection.count_documents({"verified": True})
        total_drivers = drivers_collection.count_documents({})
        active_drivers = drivers_collection.count_documents({"status": "active"})
        total_orders = orders_collection.count_documents({})
        pending_orders = orders_collection.count_documents({"status": "pending"})
        completed_orders = orders_collection.count_documents({"status": "completed"})
        total_companies = companies_collection.count_documents({})

        # Calculate revenue
        pipeline = [
            {"$match": {"status": "completed"}},
            {"$group": {"_id": None, "total_revenue": {"$sum": "$total_price"}}},
        ]
        revenue_data = list(orders_collection.aggregate(pipeline))
        total_revenue = revenue_data[0]["total_revenue"] if revenue_data else 0

        data = {
            "users": {"total": total_users, "verified": verified_users},
            "drivers": {"total": total_drivers, "active": active_drivers},
            "orders": {
                "total": total_orders,
                "pending": pending_orders,
                "completed": completed_orders,
            },
            "companies": total_companies,
            "financials": {"total_revenue": total_revenue},
            "timestamp": datetime.utcnow(),
        }

        return Response({"status": "success", "data": data}, status=200)
    except Exception as e:
        return Response({"error": "Failed to fetch system overview", "details": str(e)}, status=500)







@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_all_users(request):
    """
    View all users (optionally filter by verified/active status)
    """
    try:
        query = {}
        if request.GET.get("verified"):
            query["verified"] = request.GET["verified"].lower() == "true"
        if request.GET.get("active"):
            query["active"] = request.GET["active"].lower() == "true"

        users = list(users_collection.find(query, {"password": 0}))
        for u in users:
            u["_id"] = str(u["_id"])
        return Response({"users": users}, status=200)
    except Exception as e:
        return Response({"error": "Failed to load users", "details": str(e)}, status=500)
















@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_all_drivers(request):
    """
    Admin - View all drivers with optional filters
    """
    try:
        query = {}
        if request.GET.get("status"):
            query["status"] = request.GET["status"]  # active, suspended, pending
        if request.GET.get("verified"):
            query["verified"] = request.GET["verified"].lower() == "true"

        drivers = list(drivers_collection.find(query, {"password": 0}))
        for d in drivers:
            d["_id"] = str(d["_id"])

        return Response({"drivers": drivers}, status=200)
    except Exception as e:
        return Response({"error": "Failed to fetch drivers", "details": str(e)}, status=500)






@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_driver_details(request, driver_id):
    """
    Admin - View single driver details, performance stats, and payout summary
    """
    try:
        driver = drivers_collection.find_one({"_id": ObjectId(driver_id)}, {"password": 0})
        if not driver:
            return Response({"error": "Driver not found"}, status=404)

        # Fetch orders delivered by driver
        completed_orders = list(orders_collection.find({"driver_id": driver_id, "status": "completed"}))
        total_deliveries = len(completed_orders)

        # Calculate total earnings
        total_earnings = sum(o.get("driver_earning", 0) for o in completed_orders)

        # Compute average rating
        ratings = [o.get("rating", 0) for o in completed_orders if "rating" in o]
        avg_rating = round(sum(ratings) / len(ratings), 2) if ratings else None

        # Prepare payout history (optional collection can be added)
        payouts = list(db["payouts"].find({"driver_id": driver_id})) if "payouts" in db.list_collection_names() else []

        for p in payouts:
            p["_id"] = str(p["_id"])

        driver["_id"] = str(driver["_id"])
        driver["performance"] = {
            "total_deliveries": total_deliveries,
            "total_earnings": total_earnings,
            "average_rating": avg_rating,
            "payouts": payouts
        }

        return Response({"driver": driver}, status=200)
    except Exception as e:
        return Response({"error": "Failed to load driver details", "details": str(e)}, status=500)




from bson import ObjectId
from bson.errors import InvalidId # Import this
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def track_driver_location(request, driver_id):
    """
    Admin - View driver's latest live location
    """
    try:
        try:
            # 1. Validate ID format
            oid_driver = ObjectId(driver_id)
        except InvalidId:
            return Response({"error": "Invalid driver ID format"}, status=400)

        # 2. Fetch driver data
        driver = drivers_collection.find_one(
            {"_id": oid_driver}, # Use the validated ObjectId
            {"_id": 1, "first_name": 1, "last_name": 1, "current_location": 1, "status": 1} 
            # Note: Changed 'location' to 'current_location' as per your other file
        )
        if not driver:
            return Response({"error": "Driver not found"}, status=404)

        # 3. Format and return
        response_data = {
            "driver_id": str(driver["_id"]),
            "first_name": driver.get("first_name"),
            "last_name": driver.get("last_name"),
            "status": driver.get("status"),
            "current_location": driver.get("current_location", {}), # Safely get location
        }
        
        return Response({"driver_location": response_data}, status=200)
        
    except Exception as e:
        print(f"Error tracking driver: {e}") # Keep print for debugging
        return Response({"error": "Failed to track driver", "details": str(e)}, status=500)






















@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_all_orders(request):
    """
    Admin - View all gas orders (with optional filters)
    """
    try:
        query = {}
        if request.GET.get("status"):
            query["status"] = request.GET["status"]
        if request.GET.get("driver_id"):
            query["driver_id"] = request.GET["driver_id"]
        if request.GET.get("user_id"):
            query["user_id"] = request.GET["user_id"]

        orders = list(gas_orders.find(query))
        for o in orders:
            o["_id"] = str(o["_id"])

        return Response({"orders": orders}, status=200)
    except Exception as e:
        return Response({"error": "Failed to fetch orders", "details": str(e)}, status=500)













@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def modify_order(request, order_id):
    """
    Admin - Modify or cancel a gas order
    """
    try:
        update_data = request.data.get("update", {})
        cancel = request.data.get("cancel", False)

        order = gas_orders.find_one({"_id": ObjectId(order_id)})
        if not order:
            return Response({"error": "Order not found"}, status=404)

        if cancel:
            gas_orders.update_one(
                {"_id": ObjectId(order_id)},
                {"$set": {"status": "canceled", "canceled_at": datetime.utcnow()}}
            )

            notifications.insert_one({
                "user_id": order["user_id"],
                "title": "Order Canceled",
                "message": f"Your order {order_id} was canceled by admin.",
                "timestamp": datetime.utcnow(),
                "read": False
            })

            return Response({"message": "Order canceled successfully"}, status=200)

        if update_data:
            gas_orders.update_one({"_id": ObjectId(order_id)}, {"$set": update_data})
            return Response({"message": "Order updated successfully"}, status=200)

        return Response({"message": "No changes provided"}, status=400)
    except Exception as e:
        return Response({"error": "Failed to modify order", "details": str(e)}, status=500)









@api_view(['GET'])
@permission_classes([IsAuthenticated])
def order_overview_stats(request):
    """
    Admin - View summary stats for all gas orders
    """
    try:
        total_orders = gas_orders.count_documents({})
        completed = gas_orders.count_documents({"status": "completed"})
        pending = gas_orders.count_documents({"status": "pending"})
        canceled = gas_orders.count_documents({"status": "canceled"})
        refunded = gas_orders.count_documents({"status": "refunded"})

        total_revenue = sum(o.get("total_price", 0) for o in gas_orders.find({"status": "completed"}))

        return Response({
            "total_orders": total_orders,
            "completed": completed,
            "pending": pending,
            "canceled": canceled,
            "refunded": refunded,
            "total_revenue": total_revenue
        }, status=200)
    except Exception as e:
        return Response({"error": "Failed to load stats", "details": str(e)}, status=500)







@api_view(['GET'])
@permission_classes([IsAuthenticated])
def view_all_transactions(request):
    """
    Admin - View all transactions with filters (date, user, status)
    """
    try:
        query = {}
        if request.GET.get("status"):
            query["status"] = request.GET["status"]
        if request.GET.get("user_id"):
            query["user_id"] = request.GET["user_id"]
        if request.GET.get("date"):
            query["created_at"] = {"$gte": request.GET["date"]}

        transactions = list(transactions_collection.find(query))
        for t in transactions:
            t["_id"] = str(t["_id"])

        return Response({"transactions": transactions}, status=200)
    except Exception as e:
        return Response({"error": "Failed to fetch transactions", "details": str(e)}, status=500)


















@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def update_pricing(request):
    """
    Admin - Set or update platform pricing
    """
    try:
        price_per_kg = request.data.get("price_per_kg")
        delivery_fee = request.data.get("delivery_fee")
        discount = request.data.get("discount")

        updates = {}
        if price_per_kg is not None:
            updates["price_per_kg"] = float(price_per_kg)
        if delivery_fee is not None:
            updates["delivery_fee"] = float(delivery_fee)
        if discount is not None:
            updates["discount"] = float(discount)

        if not updates:
            return Response({"error": "No values provided"}, status=400)

        pricing_collection.update_one({}, {"$set": updates, "$currentDate": {"updated_at": True}}, upsert=True)
        return Response({"message": "Pricing updated successfully", "data": updates}, status=200)
    except Exception as e:
        return Response({"error": "Failed to update pricing", "details": str(e)}, status=500)




























@api_view(['GET'])
@permission_classes([IsAuthenticated])
def sales_performance_report(request):
    """
    Admin - Generate sales performance report (daily, weekly, monthly)
    """
    try:
        period = request.GET.get("period", "monthly")

        if period == "daily":
            group_format = "%Y-%m-%d"
        elif period == "weekly":
            group_format = "%Y-%U"  # Week of the year
        else:
            group_format = "%Y-%m"

        pipeline = [
            {"$match": {"status": {"$in": ["completed", "delivered"]}}},
            {"$group": {
                "_id": {"$dateToString": {"format": group_format, "date": "$created_at"}},
                "total_orders": {"$sum": 1},
                "total_revenue": {"$sum": "$total_amount"},
                "average_order_value": {"$avg": "$total_amount"}
            }},
            {"$sort": {"_id": 1}}
        ]

        data = list(gas_orders.aggregate(pipeline))
        for d in data:
            d["period"] = d.pop("_id")

        total_revenue = sum(item["total_revenue"] for item in data)
        total_orders = sum(item["total_orders"] for item in data)

        return Response({
            "summary": {
                "total_revenue": total_revenue,
                "total_orders": total_orders,
                "average_order_value": round(total_revenue / total_orders, 2) if total_orders else 0,
            },
            "data": data
        }, status=200)
    except Exception as e:
        return Response({"error": "Failed to generate sales report", "details": str(e)}, status=500)






@api_view(['GET'])
@permission_classes([IsAuthenticated])
def driver_performance_report(request):
    """
    Admin - Analyze driver performance (orders completed, earnings, rating)
    """
    try:
        pipeline = [
            {"$lookup": {
                "from": "gas_orders",
                "localField": "_id",
                "foreignField": "driver_id",
                "as": "orders"
            }},
            {"$project": {
                "driver_name": "$name",
                "email": 1,
                "total_orders": {"$size": "$orders"},
                "completed_orders": {
                    "$size": {
                        "$filter": {
                            "input": "$orders",
                            "as": "o",
                            "cond": {"$eq": ["$$o.status", "delivered"]}
                        }
                    }
                },
                "cancelled_orders": {
                    "$size": {
                        "$filter": {
                            "input": "$orders",
                            "as": "o",
                            "cond": {"$eq": ["$$o.status", "cancelled"]}
                        }
                    }
                },
                "total_earnings": {"$sum": "$orders.total_amount"},
            }}
        ]

        drivers = list(drivers_collection.aggregate(pipeline))
        for d in drivers:
            d["_id"] = str(d["_id"])
            d["completion_rate"] = round((d["completed_orders"] / d["total_orders"] * 100), 2) if d["total_orders"] else 0

        return Response({"drivers": drivers}, status=200)
    except Exception as e:
        return Response({"error": "Failed to generate driver performance report", "details": str(e)}, status=500)
























# ================================
# 🧠 Admin Utilities & System Management
# ================================

import platform, psutil, csv, io
from django.http import FileResponse

# === 1. View Admin Activity Logs ===
def view_activity_logs(request):
    """View recent admin actions for auditing."""
    logs = list(admin_activity_logs.find().sort("timestamp", -1).limit(100))
    for log in logs:
        log["_id"] = str(log["_id"])
    return ok(logs, "Recent admin activity logs retrieved")


# === 2. Dashboard Overview ===
def get_admin_dashboard_overview(request):
    """Returns real-time system stats for admin dashboard."""
    try:
        overview = {
            "total_users": users_collection.count_documents({}),
            "active_drivers": drivers_collection.count_documents({"status": "active"}),
            "pending_orders": gas_orders.count_documents({"status": {"$in": ["pending", "assigned"]}}),
            "completed_orders": gas_orders.count_documents({"status": "delivered"}),
            "total_revenue": sum(o.get("total_price", 0) for o in gas_orders.find()),
            "total_companies": companies_collection.count_documents({}),
        }
        return ok(overview, "Dashboard stats loaded")
    except Exception as e:
        return error(f"Error fetching dashboard overview: {e}")









# === 5. System Health Check ===
def system_health_check(request):
    """Monitor system resources and DB status."""
    try:
        cpu = psutil.cpu_percent(interval=0.5)
        mem = psutil.virtual_memory().percent
        db_status = "connected" if users_collection is not None else "disconnected"

        health = {
            "server_time": datetime.utcnow().isoformat(),
            "cpu_usage_percent": cpu,
            "memory_usage_percent": mem,
            "database_status": db_status,
            "python_version": platform.python_version(),
            "system": platform.system(),
        }
        return ok(health, "System health check successful")
    except Exception as e:
        return error(f"System health check failed: {e}")






#____________
#________________________________________
# Track order logic___________________________________________________
#_______________________
#_____________





import json
from datetime import datetime, timedelta
from bson import ObjectId
from django.http import JsonResponse
from rest_framework.decorators import api_view
from geopy.distance import geodesic
from django.conf import settings

from pymongo.errors import PyMongoError
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer




# ============================================================
# Utility: Calculate ETA (based on driver → delivery distance)
# ============================================================

def calculate_eta(driver_location, delivery_location):
    """
    Calculates ETA (Estimated Time of Arrival) between two coordinates.
    """
    try:
        distance_km = geodesic(driver_location, delivery_location).km
        avg_speed = 30  # km/h (you can adjust for realism)
        eta_minutes = distance_km / avg_speed * 60
        return datetime.utcnow() + timedelta(minutes=eta_minutes)
    except Exception as e:
        print("ETA calculation error:", e)
        return None


# ============================================================
# (1) Update Driver Location (ping from driver app)
# ============================================================

@api_view(["POST"])
def update_driver_location(request, driver_id):
    """
    Drivers call this periodically to update their live GPS position.
    Also updates any active order they’re assigned to and recalculates ETA.
    """
    try:
        data = json.loads(request.body)
        lat = data.get("lat")
        lng = data.get("lng")

        if lat is None or lng is None:
            return JsonResponse({"success": False, "message": "Missing lat/lng"}, status=400)

        # Update driver location
        drivers_collection.update_one(
            {"_id": ObjectId(driver_id)},
            {"$set": {"current_location": {"lat": lat, "lng": lng, "timestamp": datetime.utcnow()}}}
        )

        # Find active order
        active_order = gas_orders.find_one({
            "driver_id": driver_id,
            "status": {"$in": ["On the way", "Picked up"]}
        })

        if active_order:
            delivery_address = active_order.get("delivery_address", {})
            coords = delivery_address.get("coords")

            update_fields = {
                "current_location": {"lat": lat, "lng": lng, "timestamp": datetime.utcnow()}
            }

            if coords:
                eta = calculate_eta((lat, lng), (coords["lat"], coords["lng"]))
                if eta:
                    update_fields["estimated_arrival"] = eta

            # Update order in DB
            gas_orders.update_one(
                {"_id": active_order["_id"]},
                {"$set": update_fields}
            )

            # Broadcast via WebSocket for real-time tracking
            try:
                channel_layer = get_channel_layer()
                async_to_sync(channel_layer.group_send)(
                    f"order_{str(active_order['_id'])}",
                    {
                        "type": "location.update",
                        "order_id": str(active_order["_id"]),
                        "location": {"lat": lat, "lng": lng, "timestamp": datetime.utcnow().isoformat()}
                    }
                )
            except Exception as ws_err:
                print("WebSocket broadcast failed:", ws_err)

        return JsonResponse({"success": True, "message": "Driver location updated"})

    except PyMongoError as db_err:
        return JsonResponse({"success": False, "error": f"Database error: {db_err}"}, status=500)
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=500)


# ============================================================
# (2) Track Order (User endpoint)
# ============================================================

@api_view(["GET"])
def track_order(request, order_id):
    """
    Returns live tracking info for a specific order.
    Includes driver info, order status, location, and ETA.
    """
    try:
        order = gas_orders.find_one({"_id": ObjectId(order_id)})
        if not order:
            return JsonResponse({"success": False, "message": "Order not found"}, status=404)

        driver = None
        if order.get("driver_id"):
            driver = drivers_collection.find_one(
                {"_id": ObjectId(order["driver_id"])},
                {"password": 0}
            )

        tracking_data = {
            "order_id": str(order["_id"]),
            "status": order.get("status", "Unknown"),
            "driver_name": driver.get("name") if driver else "Unassigned",
            "driver_phone": driver.get("phone") if driver else None,
            "driver_location": order.get("current_location"),
            "delivery_address": order.get("delivery_address"),
            "estimated_arrival": order.get("estimated_arrival"),
            "last_updated": order.get("updated_at", datetime.utcnow()),
        }

        return JsonResponse({"success": True, "tracking": tracking_data})

    except PyMongoError as db_err:
        return JsonResponse({"success": False, "error": f"Database error: {db_err}"}, status=500)
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=500)









@api_view(["GET"])
@permission_classes([IsAuthenticated])
def track_all_drivers(request):
    """
    Admin can view all drivers' current GPS locations and delivery status.
    Includes last update timestamp, active order (if any), and ETA.
    """
    try:
        # Fetch all drivers with location info
        drivers = list(drivers_collection.find({}, {
            "_id": 1,
            "name": 1,
            "phone": 1,
            "status": 1,
            "current_location": 1,
            "updated_at": 1
        }))

        tracked_drivers = []

        for driver in drivers:
            driver_id = str(driver["_id"])
            location = driver.get("current_location")

            # Get active order (if assigned)
            active_order = gas_orders.find_one({
                "driver_id": driver_id,
                "status": {"$in": ["On the way", "Picked up"]}
            })

            order_info = None
            if active_order:
                order_info = {
                    "order_id": str(active_order["_id"]),
                    "customer_name": active_order.get("customer_name"),
                    "delivery_address": active_order.get("delivery_address"),
                    "status": active_order.get("status"),
                    "eta": active_order.get("estimated_arrival")
                }

            tracked_drivers.append({
                "driver_id": driver_id,
                "name": driver.get("name"),
                "phone": driver.get("phone"),
                "status": driver.get("status", "Unknown"),
                "current_location": location,
                "last_updated": location.get("timestamp") if location else None,
                "active_order": order_info
            })

        return JsonResponse({
            "success": True,
            "count": len(tracked_drivers),
            "drivers": tracked_drivers
        })

    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({"success": False, "message": str(e)}, status=500)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def track_user_orders(request):
    """
    Returns real-time tracking data for all orders of the authenticated user.
    Includes order status, driver location, ETA, and driver details if assigned.
    """
    try:
        user = request.user
        user_id = str(user.id)

        # Fetch user's orders
        orders_cursor = gas_orders.find({"customer_id": ObjectId(user_id)})
        orders = list(orders_cursor)

        tracked_orders = []
        for order in orders:
            order_data = {
                "order_id": str(order["_id"]),
                "product_id": str(order.get("product_id")) if order.get("product_id") else None,
                "quantity": order.get("quantity", 0),
                "total_price": order.get("total_price", 0),
                "order_status": order.get("order_status", "unknown"),
                "delivery_address": order.get("delivery_address", ""),
                "created_at": order.get("created_at").isoformat() if isinstance(order.get("created_at"), datetime) else None,
                "updated_at": order.get("updated_at").isoformat() if isinstance(order.get("updated_at"), datetime) else None,
                "driver_location": order.get("current_location"),
                "estimated_arrival": order.get("estimated_arrival").isoformat() if isinstance(order.get("estimated_arrival"), datetime) else None,
            }

            # Enrich with driver details if assigned
            driver_id = order.get("assigned_driver_id")
            if driver_id:
                driver = drivers_collection.find_one({"_id": ObjectId(driver_id)}, {"password": 0})
                if driver:
                    order_data["driver"] = {
                        "id": str(driver["_id"]),
                        "username": driver.get("username", ""),
                        "phone": driver.get("phone", ""),
                        "rating": driver.get("rating", 0),
                    }
                else:
                    order_data["driver"] = None
            else:
                order_data["driver"] = None

            tracked_orders.append(order_data)

        return Response({
            "message": "User orders tracking data retrieved successfully.",
            "orders": tracked_orders
        }, status=200)

    except Exception as e:
        logger.exception(f"Error in track_user_orders: {e}")
        return Response({"error": "Failed to retrieve order tracking data."}, status=500)


# ------------------------- Missing Driver Views Implementation -------------------------









@api_view(['GET'])
@permission_classes([AllowAny])
def get_driver_wallet(request):
    """
    Driver gets their wallet balance, total earnings, and total payouts.
    Wallet balance is calculated as total earnings minus total payouts.
    """
    driver, error_resp = get_driver_from_token(request)
    if error_resp:
        return error_resp

    try:
        driver_id = str(driver["_id"])

        # Calculate total earnings from completed orders
        completed_orders = list(gas_orders.find({
            "assigned_driver_id": driver_id,
            "order_status": "delivered"
        }))
        total_earnings = sum(order.get("driver_surcharge", 0) for order in completed_orders)

        # Calculate total payouts
        total_payouts = sum(payout.get("amount", 0) for payout in payouts_collection.find({"driver_id": driver_id}))

        # Wallet balance = earnings - payouts
        wallet_balance = total_earnings - total_payouts

        return Response({
            "wallet_balance": wallet_balance,
            "total_earnings": total_earnings,
            "total_payouts": total_payouts
        }, status=200)

    except Exception as e:
        return Response({"error": "Failed to fetch wallet", "details": str(e)}, status=500)










 





    



      


@api_view(['PATCH'])
@permission_classes([AllowAny])  # Change to IsAuthenticated if you require auth
def start_break(request):
    """
    Driver starts a break period.
    Updates driver status to 'on_break' and records the start time.
    """
    try:
        driver, error_resp = get_driver_from_token(request)
        if error_resp:
            return error_resp

        driver_id = driver["_id"]

        # Fetch current driver record
        current_driver = drivers_collection.find_one({"_id": ObjectId(driver_id)})
        if not current_driver:
            return Response({"error": "Driver not found"}, status=404)

        # Prevent starting break if already on break
        if current_driver.get("status") == "on_break":
            return Response({"message": "You are already on break."}, status=200)

        # Update status to 'on_break'
        update_data = {
            "status": "on_break",
            "break_started_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }

        drivers_collection.update_one(
            {"_id": ObjectId(driver_id)},
            {"$set": update_data}
        )

        return Response({
            "message": "Break started successfully.",
            "status": "on_break",
            "break_started_at": update_data["break_started_at"].isoformat()
        }, status=200)

    except Exception as e:
        return Response({
            "error": "Failed to start break",
            "details": str(e)
        }, status=500)        



@api_view(['PATCH'])
@permission_classes([AllowAny])  # Use IsAuthenticated if drivers must be logged in
def end_break(request):
    """
    Driver ends their break period.
    Sets driver status back to 'online' and logs break duration if available.
    """
    try:
        driver, error_resp = get_driver_from_token(request)
        if error_resp:
            return error_resp

        driver_id = driver["_id"]

        # Fetch current driver record
        current_driver = drivers_collection.find_one({"_id": ObjectId(driver_id)})
        if not current_driver:
            return Response({"error": "Driver not found"}, status=404)

        if current_driver.get("status") != "on_break":
            return Response({"message": "You are not currently on break."}, status=400)

        # Compute duration of break
        break_start = current_driver.get("break_started_at")
        if break_start:
            break_duration = (datetime.utcnow() - break_start).total_seconds() / 60  # minutes
        else:
            break_duration = None

        # Update driver back to 'online'
        update_data = {
            "status": "online",
            "break_ended_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }

        # Optionally store total break time (could be logged in an array)
        if break_duration:
            update_data["last_break_duration_min"] = round(break_duration, 2)

        drivers_collection.update_one(
            {"_id": ObjectId(driver_id)},
            {"$set": update_data, "$unset": {"break_started_at": ""}}
        )

        response = {
            "message": "Break ended successfully.",
            "status": "online",
            "break_ended_at": update_data["break_ended_at"].isoformat()
        }

        if break_duration:
            response["break_duration_minutes"] = round(break_duration, 2)

        return Response(response, status=200)

    except Exception as e:
        return Response({
            "error": "Failed to end break",
            "details": str(e)
        }, status=500)        







@api_view(['GET'])
@permission_classes([AllowAny]) 
def get_driver_performance(request):
    """
    Returns detailed performance metrics for a driver.
    Metrics include completion rate, acceptance rate, average delivery time, and total earnings.
    """
    try:
        # Authenticate driver
        driver, error_resp = get_driver_from_token(request)
        if error_resp:
            return error_resp

        driver_id = ObjectId(driver["_id"])

        # Fetch all orders assigned to this driver
        all_orders = list(orders_collection.find({"driver_id": driver_id}))

        total_orders = len(all_orders)
        accepted_orders = [o for o in all_orders if o.get("status") in ["accepted", "completed"]]
        completed_orders = [o for o in all_orders if o.get("status") == "completed"]
        cancelled_orders = [o for o in all_orders if o.get("status") == "cancelled"]

        # Avoid division by zero
        completion_rate = (len(completed_orders) / len(accepted_orders) * 100) if accepted_orders else 0
        acceptance_rate = (len(accepted_orders) / total_orders * 100) if total_orders else 0

        # Average delivery time for completed orders
        durations = [o.get("duration_min") for o in completed_orders if o.get("duration_min")]
        avg_delivery_time = round(sum(durations) / len(durations), 2) if durations else 0

        # Total earnings
        total_earnings = sum(o.get("earning", 0) for o in completed_orders)

        # Average customer rating
        ratings = [o.get("rating") for o in completed_orders if o.get("rating") is not None]
        avg_rating = round(sum(ratings) / len(ratings), 2) if ratings else None

        # Last 30 days summary
        last_30_days = datetime.utcnow() - timedelta(days=30)
        monthly_orders = [o for o in completed_orders if o.get("completed_at") and o["completed_at"] >= last_30_days]
        monthly_earnings = sum(o.get("earning", 0) for o in monthly_orders)

        performance = {
            "driver_id": str(driver_id),
            "total_orders": total_orders,
            "accepted_orders": len(accepted_orders),
            "completed_orders": len(completed_orders),
            "cancelled_orders": len(cancelled_orders),
            "completion_rate_percent": round(completion_rate, 2),
            "acceptance_rate_percent": round(acceptance_rate, 2),
            "average_delivery_time_min": avg_delivery_time,
            "average_rating": avg_rating,
            "total_earnings": round(total_earnings, 2),
            "monthly_earnings": round(monthly_earnings, 2),
        }

        return Response({"performance": performance}, status=200)

    except Exception as e:
        return Response({
            "error": "Failed to fetch driver performance",
            "details": str(e)
        }, status=500)












      











      








# views.py

# Import the new permission class
from .permissions import IsAdminWithSecretPin 

# ... (Your existing imports, helpers, and driver views remain here)

# ----------------- ADMIN ENDPOINT 1: Get All Orders -----------------




@api_view(['GET'])
@permission_classes([IsAdminWithSecretPin])
def admin_get_all_orders(request):
    """
    ADMIN VIEW: Fetch all gas orders. Requires X-Admin-Pin in header.
    """
    try:
        orders_cursor = gas_orders.find().sort("created_at", -1)
        orders = []

        for o in orders_cursor:
            orders.append({
                "id": str(o.get("_id")),
                "customer": o.get("customer_name", ""),
                "driver": o.get("driver_name", ""),
                "status": o.get("order_status", ""),
                "time": o.get("created_at").strftime("%I:%M %p") if o.get("created_at") else ""
            })

        print("Fetched orders from DB:", orders)  # <-- DEBUG LOG

        return Response({"orders": orders}, status=200)

    except Exception as e:
        print("Error fetching admin orders:", e)  # <-- DEBUG LOG
        return Response(
            {"error": "Failed to fetch admin orders", "details": str(e)},
            status=500
        )





# ----------------- ADMIN ENDPOINT 2: Update Order Status -----------------
@api_view(['POST'])
@permission_classes([IsAdminWithSecretPin]) # <-- SECURITY: Use the PIN check
def admin_update_order_details(request, order_id):
    """
    ADMIN VIEW: Updates the order status and/or assigns a driver. Requires X-Admin-Pin in header.
    """
    try:
        # ... (rest of your admin_update_order_details logic)
        
        # ... (validation and update_fields prep)

        result = gas_orders.update_one(
            {"_id": ObjectId(order_id)},
            {"$set": update_fields}
        )
        
        # ... (return success/error response)
        return Response(
            {
                "message": f"Order {order_id} updated successfully.",
                "updated_fields": list(update_fields.keys()),
                "status": update_fields.get("order_status")
            }, 
            status=200
        )

    except Exception as e:
        # ... (error handling)
        return Response(
            {"error": "Failed to update order", "details": str(e)},
            status=500
        )

                               
       
# ----------------- ADMIN ENDPOINT: Get All Users -----------------
@api_view(['GET'])
@permission_classes([IsAdminWithSecretPin])  # Keep the same security as orders
def admin_get_all_users(request):
    """
    ADMIN VIEW: Fetch all users. Requires X-Admin-Pin in header.
    """
    try:
        # Fetch all users from MongoDB, sorted by creation date (newest first)
        users_cursor = users_collection.find().sort("created_at", -1)
        users = []

        for user in users_cursor:
            users.append({
                "id": str(user.get("_id")),
                "name": user.get("name"),
                "email": user.get("email"),
                "phone": user.get("phone"),
                "created_at": user.get("created_at").strftime("%Y-%m-%d %H:%M:%S") if user.get("created_at") else None,
                "is_active": user.get("is_active", True)
            })

        # Debug: log to console so we know what's being fetched
        print("Fetched users from DB:", users)

        return Response({"users": users}, status=200)

    except Exception as e:
        return Response(
            {"error": "Failed to fetch users", "details": str(e)},
            status=500
        )



# ----------------- ADMIN ENDPOINT: Get Full User Details -----------------
@api_view(['GET'])
@permission_classes([IsAdminWithSecretPin])  # Admin PIN check
def admin_get_all_user_details(request):
    """
    ADMIN VIEW: Fetch complete details of all users. Requires X-Admin-Pin in header.
    """
    try:
        users_cursor = users_collection.find().sort("created_at", -1)
        users = []

        for user in users_cursor:
            users.append({
                "id": str(user.get("_id")),
                "username": user.get("username"),
                "email": user.get("email"),
                "phone_number": user.get("phone_number"),
                "role": user.get("role"),
                "is_verified": user.get("is_verified", False),
                "created_at": user.get("created_at").strftime("%Y-%m-%d %H:%M:%S") if user.get("created_at") else None,
                "verified_at": user.get("verified_at").strftime("%Y-%m-%d %H:%M:%S") if user.get("verified_at") else None,
                "last_login": user.get("last_login").strftime("%Y-%m-%d %H:%M:%S") if user.get("last_login") else None,
                "failed_login_attempts": user.get("failed_login_attempts", 0),
                "lockout_time": user.get("lockout_time").strftime("%Y-%m-%d %H:%M:%S") if user.get("lockout_time") else None
            })

        # Debug: log users to console
        print("Fetched full user details:", users)

        return Response({"users": users}, status=200)

    except Exception as e:
        return Response(
            {"error": "Failed to fetch user details", "details": str(e)},
            status=500
        )


# ----------------- ADMIN ENDPOINT: Delete a User -----------------
@api_view(['DELETE'])
@permission_classes([IsAdminWithSecretPin])  # Admin PIN check
def admin_delete_user(request, user_id):
    """
    ADMIN VIEW: Delete a specific user by ID. Requires X-Admin-Pin in header.
    """
    try:
        # Check if the user exists
        user = users_collection.find_one({"_id": ObjectId(user_id)})
        if not user:
            return Response({"error": f"User with ID {user_id} not found."}, status=404)

        # Prevent admin from deleting themselves (optional safety)
        if request.user and str(request.user["_id"]) == user_id:
            return Response({"error": "Admins cannot delete themselves."}, status=403)

        # Delete the user
        result = users_collection.delete_one({"_id": ObjectId(user_id)})

        if result.deleted_count == 1:
            return Response({"message": f"User {user_id} deleted successfully."}, status=200)
        else:
            return Response({"error": f"Failed to delete user {user_id}."}, status=500)

    except Exception as e:
        return Response({"error": "Failed to delete user", "details": str(e)}, status=500)
     



# ----------------- ADMIN ENDPOINT: Count Drivers -----------------
@api_view(['GET'])
@permission_classes([IsAdminWithSecretPin])  # Admin PIN check
def admin_get_driver_count(request):
    """
    ADMIN VIEW: Get the total number of drivers in the system.
    """
    try:
        driver_count = drivers_collection.count_documents({})
        return Response({"total_drivers": driver_count}, status=200)
    except Exception as e:
        return Response({"error": "Failed to fetch driver count", "details": str(e)}, status=500)



from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from bson import ObjectId
from .permissions import IsAdminWithSecretPin

@api_view(['POST'])
@permission_classes([IsAdminWithSecretPin])
def admin_update_order_unit_price(request, order_id):
    """
    ADMIN VIEW: Update unit price per kg for a specific order
    and recalculate the total_price.
    """
    try:
        new_unit_price = request.data.get("unit_price")
        if new_unit_price is None:
            return Response({"error": "unit_price is required"}, status=400)
        
        try:
            new_unit_price = float(new_unit_price)
            if new_unit_price <= 0:
                return Response({"error": "unit_price must be positive"}, status=400)
        except ValueError:
            return Response({"error": "unit_price must be a number"}, status=400)
        
        # Fetch the order
        order = gas_orders.find_one({"_id": ObjectId(order_id)})
        if not order:
            return Response({"error": "Order not found"}, status=404)
        
        weight = float(order.get("weight", 0))
        new_total_price = round(weight * new_unit_price, 2)
        
        # Update order in MongoDB
        gas_orders.update_one(
            {"_id": ObjectId(order_id)},
            {"$set": {"unit_price": new_unit_price, "total_price": new_total_price}}
        )
        
        # Return updated order
        order["unit_price"] = new_unit_price
        order["total_price"] = new_total_price
        return Response({"message": "Order updated successfully", "order": {
            "_id": str(order["_id"]),
            "weight": weight,
            "unit_price": order["unit_price"],
            "total_price": order["total_price"]
        }}, status=200)
    
    except Exception as e:
        return Response({"error": "Failed to update order", "details": str(e)}, status=500)

from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from datetime import datetime
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

from .permissions import IsAdminWithSecretPin

@api_view(['POST', 'OPTIONS'])
@permission_classes([IsAdminWithSecretPin])
@csrf_exempt  # must come LAST (below api_view)
def admin_update_global_price(request):
    """
    ADMIN VIEW: Update global unit price per kg for a product.
    """
    try:
        print("🔹 admin_update_global_price called")
        print("Request headers:", request.headers)
        print("Request data:", request.data)

        product_name = request.data.get("product_name")
        new_unit_price = request.data.get("unit_price")

        if not product_name or new_unit_price is None:
            print("❌ Missing product_name or unit_price")
            return Response(
                {"error": "product_name and unit_price are required"}, status=400
            )

        try:
            new_unit_price = float(new_unit_price)
            if new_unit_price <= 0:
                print(f"❌ Invalid unit_price: {new_unit_price}")
                return Response(
                    {"error": "unit_price must be positive"}, status=400
                )
        except ValueError:
            print(f"❌ unit_price not a number: {new_unit_price}")
            return Response({"error": "unit_price must be a number"}, status=400)

        print(f"✅ Updating global price: {product_name} -> {new_unit_price}")
        result = global_config.update_one(
            {"_id": "global_config"},
            {"$set": {
                f"product_prices.{product_name}": new_unit_price,
                "updated_at": datetime.now()
            }},
            upsert=True
        )
        print("Update result:", result.raw_result)

        return Response(
            {"message": f"Global price for {product_name} updated to {new_unit_price}"},
            status=200
        )

    except Exception as e:
        print("❌ Exception in admin_update_global_price:", str(e))
        import traceback
        traceback.print_exc()
        return Response(
            {"error": "Failed to update global price", "details": str(e)}, status=500
        )



# views.py
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from .permissions import IsAdminWithSecretPin

@api_view(['GET'])
@permission_classes([IsAdminWithSecretPin])
def admin_get_total_revenue(request):
    """
    ADMIN VIEW: Calculate total revenue from delivered orders using MongoDB aggregation.
    """
    try:
        pipeline = [
            {"$match": {"order_status": "delivered"}},
            {
                "$group": {
                    "_id": None,
                    "total_revenue": {"$sum": "$total_price"},
                    "delivered_orders_count": {"$sum": 1}
                }
            }
        ]

        result = list(gas_orders.aggregate(pipeline))
        if result:
            total_revenue = result[0].get("total_revenue", 0)
            order_count = result[0].get("delivered_orders_count", 0)
        else:
            total_revenue = 0
            order_count = 0

        return Response({
            "total_revenue": total_revenue,
            "delivered_orders_count": order_count
        }, status=200)

    except Exception as e:
        return Response({
            "error": "Failed to fetch revenue",
            "details": str(e)
        }, status=500)



from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from .permissions import IsAdminWithSecretPin
from bson import ObjectId
from datetime import datetime, timedelta
from collections import defaultdict

@api_view(['GET'])
@permission_classes([IsAdminWithSecretPin])
def admin_sales_volume(request):
    """
    ADMIN VIEW: Get daily sales volume (m³) for the last 7 days from delivered/confirmed orders
    """
    try:
        # Get last 7 days
        end_date = datetime.now()
        start_date = end_date - timedelta(days=7)
        
        # Aggregate by date
        pipeline = [
            {
                "$match": {
                    "order_status": {"$in": ["delivered", "confirmed"]},
                    "created_at": {"$gte": start_date, "$lte": end_date}
                }
            },
            {
                "$group": {
                    "_id": {
                        "$dateToString": {
                            "format": "%Y-%m-%d",
                            "date": "$created_at"
                        }
                    },
                    "total_volume": {"$sum": "$volume"}  # Assuming 'volume' field in m³
                }
            },
            {
                "$sort": {"_id": 1}
            }
        ]
        
        results = list(gas_orders.aggregate(pipeline))
        
        # Create list for last 7 days, defaulting to 0 if no data
        sales_volume = []
        for i in range(7):
            date_str = (start_date + timedelta(days=i)).strftime("%Y-%m-%d")
            volume = next((r["total_volume"] for r in results if r["_id"] == date_str), 0)
            sales_volume.append(volume)
        
        return Response({
            "sales_volume": sales_volume
        }, status=200)

    except Exception as e:
        return Response({
            "error": "Failed to fetch sales volume",
            "details": str(e)
        }, status=500)






# views.py
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from .permissions import IsAdminWithSecretPin
from bson.objectid import ObjectId

@api_view(['GET'])
@permission_classes([IsAdminWithSecretPin])
def admin_get_all_orders_details(request):
    """
    ADMIN VIEW: Fetch all orders with complete details.
    """
    try:
        # Fetch all orders from DB
        orders_cursor = gas_orders.find().sort("created_at", -1)
        orders = []

        for order in orders_cursor:
            # Convert ObjectId and datetime to string for JSON serialization
            orders.append({
                "_id": str(order.get("_id")),
                "customer_id": str(order.get("customer_id")),
                "customer_name": order.get("customer_name"),
                "customer_phone": order.get("customer_phone"),
                "product_id": str(order.get("product_id")),
                "product_name": order.get("product_name"),
                "quantity": order.get("quantity"),
                "weight": float(order.get("weight", 0)),
                "unit_price": float(order.get("unit_price", 0)),
                "total_price": float(order.get("total_price", 0)),
                "delivery_address": order.get("delivery_address"),
                "delivery_type": order.get("delivery_type"),
                "payment_method": order.get("payment_method"),
                "payment_status": order.get("payment_status"),
                "order_status": order.get("order_status"),
                "notes": order.get("notes"),
                "delivery_surcharge": float(order.get("delivery_surcharge", 0)),
                "created_at": order.get("created_at").isoformat() if order.get("created_at") else None,
                "updated_at": order.get("updated_at").isoformat() if order.get("updated_at") else None,
                "assigned_driver_id": order.get("assigned_driver_id"),
                "delivered_at": order.get("delivered_at").isoformat() if order.get("delivered_at") else None,
            })

        return Response({"orders": orders}, status=200)

    except Exception as e:
        return Response(
            {"error": "Failed to fetch orders details", "details": str(e)},
            status=500
        )

from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from bson import ObjectId

from .permissions import IsAdminWithSecretPin  # your existing admin PIN check


@api_view(['GET'])
@permission_classes([IsAdminWithSecretPin])
def admin_get_driver_details(request, driver_id):
    """
    ADMIN VIEW: Fetch full driver details by ID.
    Requires `X-Admin-Pin` header for access.
    """
    try:
        # Find driver in the database
        driver = drivers_collection.find_one({"_id": ObjectId(driver_id)})
        if not driver:
            return Response({"error": "Driver not found"}, status=404)

        # Clean ObjectId and convert timestamps
        driver["_id"] = str(driver["_id"])
        if "created_at" in driver:
            driver["created_at"] = driver["created_at"].isoformat() if hasattr(driver["created_at"], "isoformat") else str(driver["created_at"])
        if "updated_at" in driver:
            driver["updated_at"] = driver["updated_at"].isoformat() if hasattr(driver["updated_at"], "isoformat") else str(driver["updated_at"])

        return Response({"driver": driver}, status=200)

    except Exception as e:
        return Response(
            {"error": "Failed to fetch driver details", "details": str(e)},
            status=500
        )



from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from bson import ObjectId

from .permissions import IsAdminWithSecretPin


@api_view(['GET'])
@permission_classes([IsAdminWithSecretPin])
def admin_get_all_drivers(request):
    """
    ADMIN VIEW: Fetch all drivers for the admin dashboard.
    Requires `X-Admin-Pin` header for access.
    """
    try:
        # Fetch all drivers from MongoDB, sorted by creation date (if exists)
        cursor = drivers_collection.find().sort("created_at", -1)
        drivers = []

        for d in cursor:
            drivers.append({
                "id": str(d.get("_id")),
                "name": d.get("name") or d.get("username") or "Unknown",
                "email": d.get("email", "N/A"),
                "phone_number": d.get("phone_number", "N/A"),
                "status": d.get("status", "inactive"),
                "vehicle_number": d.get("vehicle_number", "N/A"),
                "created_at": str(d.get("created_at", "")),
                "last_login": str(d.get("last_login", "")),
                "current_location": d.get("current_location", {}),
                "total_deliveries": d.get("total_deliveries", 0)
            })

        return Response({"drivers": drivers}, status=200)

    except Exception as e:
        return Response(
            {"error": "Failed to fetch drivers", "details": str(e)},
            status=500
        )


@api_view(['GET'])
@permission_classes([AllowAny])
def get_delivery_history(request):
    """
    Returns the authenticated driver's completed delivery history.
    Includes order details, delivery time, and earnings per order.
    """
    try:
        # Authenticate driver
        driver, error_resp = get_driver_from_token(request)
        if error_resp:
            return error_resp

        driver_id = str(driver["_id"])

        # Fetch completed deliveries
        completed_orders = list(gas_orders.find({
            "assigned_driver_id": driver_id,
            "order_status": "delivered"
        }).sort("updated_at", -1))

        history = []
        for order in completed_orders:
            history.append({
                "order_id": str(order["_id"]),
                "customer_name": order.get("customer_name"),
                "delivery_address": order.get("delivery_address"),
                "total_price": order.get("total_price", 0),
                "driver_earning": order.get("driver_surcharge", 0),
                "delivered_at": order.get("updated_at").isoformat() if order.get("updated_at") else None
            })

        return Response({
            "message": "Delivery history retrieved successfully",
            "total_deliveries": len(history),
            "history": history
        }, status=200)

    except Exception as e:
        return Response({
            "error": "Failed to fetch delivery history",
            "details": str(e)
        }, status=500)


        












             




        