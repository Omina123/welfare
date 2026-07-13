# mpesa/utils.py
import base64
import requests
from requests.auth import HTTPBasicAuth
from django.conf import settings
from datetime import datetime

def get_mpesa_access_token():
    """Fetches OAuth access token from Daraja API."""
    url = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
    try:
        response = requests.get(url, auth=HTTPBasicAuth(settings.MPESA_CONSUMER_KEY, settings.MPESA_CONSUMER_SECRET), timeout=30)
        response.raise_for_status()
        return response.json().get('access_token')
    except Exception:
        return None

def get_mpesa_password():
    """Generates password and timestamp for STK Push."""
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    data_to_encode = f"{settings.MPESA_SHORTCODE}{settings.MPESA_PASSKEY}{timestamp}"
    password = base64.b64encode(data_to_encode.encode()).decode('utf-8')
    return password, timestamp