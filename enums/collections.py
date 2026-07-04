import os
from dotenv import load_dotenv

load_dotenv()

# Actively changes, remember to change every ngrok invokation
urls = {"endpoint": os.getenv("NGROK_BACKUP_ENDPOINT_URL")}

credentials = {
    "twilio": {
        "account_sid": os.getenv("TWILIO_ACCOUNT_SID"),
        "auth_token": os.getenv("TWILIO_AUTH_TOKEN"),
        "from_phone_number": os.getenv("TWILIO_PHONE_NUMBER"),
        "to_phone_number": os.getenv("TEST_NUMBER"),
    },
    "ngrok": {
        "auth_token": os.getenv("NGROK_AUTH_TOKEN"),
    },
    "groq": {
        "api_key": os.getenv("GROQ_API_KEY"),
    },
}
