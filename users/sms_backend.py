# users/sms_backend.py
from django.conf import settings
from kavenegar import KavenegarAPI, APIException, HTTPException

def send_sms_via_kavenegar(receptor: str, message: str) -> dict:
    """
    Send SMS via official Kavenegar SDK.
    receptor: target phone number (like '09120001234')
    message: text body (string)
    """
    api_key = settings.KAVENEGAR_API_KEY
    if not api_key:
        raise RuntimeError("KAVENEGAR_API_KEY not configured in settings.py")

    try:
        api = KavenegarAPI(api_key)
        params = {
            'sender': getattr(settings, "KAVENEGAR_SENDER", ""),  # Optional: your sender number
            'receptor': receptor,
            'message': message,
        }
        response = api.sms_send(params)
        return response  # usually a dict or list of status entries
    except APIException as e:
        print("API error:", e)
        raise
    except HTTPException as e:
        print("HTTP error:", e)
        raise
