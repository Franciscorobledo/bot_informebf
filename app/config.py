import os


class Settings:
    slack_signing_secret = os.getenv("SLACK_SIGNING_SECRET", "")
    slack_bot_token = os.getenv("SLACK_BOT_TOKEN", "")
    openai_api_key = os.getenv("OPENAI_API_KEY", "")
    google_api_base = os.getenv("GOOGLE_API_BASE", "https://www.googleapis.com/calendar/v3")
    base_url = os.getenv("BASE_URL", "http://localhost:8000")


settings = Settings()
