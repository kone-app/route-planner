import os
from dotenv import load_dotenv

env = os.getenv("ENV", "dev")

# Try local first, then default to .env.dev
dotenv_path = f".env.{env}"
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)
else:
    # When running inside Docker, look inside Lambda root
    lambda_path = os.path.join(os.getcwd(), f".env.{env}")
    if os.path.exists(lambda_path):
        load_dotenv(lambda_path)

API_KEY = os.getenv("DIGITRANSIT_API_KEY")
FROM_EMAIL = os.getenv("FROM_EMAIL")
TO_EMAIL = os.getenv("TO_EMAIL")
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD")
GEO_CODING_URL = os.getenv("GEO_CODING_URL")
ROUTING_URL = os.getenv("ROUTING_URL")
JOURNEY_COUNT = int(os.getenv("JOURNEY_COUNT", "5"))
CRON_HOUR = os.getenv("CRON_HOUR")
CRON_MINUTE = os.getenv("CRON_MINUTE")
ENABLE_SCHEDULE = os.getenv("ENABLE_SCHEDULE")
