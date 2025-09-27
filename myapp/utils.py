# myapp/utils.py
import requests
from django.conf import settings

TEXTBEE_API_URL = "https://api.textbee.dev/sms/send"

def send_sms(to_number, message):
    """
    Send SMS using TextBee API.

    Args:
        to_number (str): Recipient phone number in international format, e.g., '+1234567890'
        message (str): Text message content

    Returns:
        dict: API response from TextBee
    """
    headers = {
        "Authorization": f"Bearer {settings.TEXTBEE_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "to": to_number,
        "message": message
    }

    try:
        response = requests.post(TEXTBEE_API_URL, json=payload, headers=headers)
        response.raise_for_status()
        return {"success": True, "data": response.json()}
    except requests.exceptions.HTTPError as errh:
        return {"success": False, "error": f"HTTP Error: {errh}"}
    except requests.exceptions.ConnectionError as errc:
        return {"success": False, "error": f"Connection Error: {errc}"}
    except requests.exceptions.Timeout as errt:
        return {"success": False, "error": f"Timeout Error: {errt}"}
    except requests.exceptions.RequestException as err:
        return {"success": False, "error": f"Request Error: {err}"}
