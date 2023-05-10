""" Used to generate login information, declutter main."""
from google.auth.transport import requests
import google.oauth2.id_token

from config import AppConfig

firebase_request_adapter = requests.Request()

def is_logged_in(id_token):
    if AppConfig.STAGE == "dev":
        return "DEVELOPMENT_CLAIM"
    if id_token != "":
        try:
            claims = google.oauth2.id_token.verify_firebase_token(
                id_token, firebase_request_adapter)
            return claims
        except ValueError:
            return None
    else:
        return None
    