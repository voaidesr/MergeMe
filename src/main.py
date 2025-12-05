import os
import sys

import requests
from dotenv import load_dotenv
from api_client import ApiClient
from app import App
from utils import HourRequestDto
import json

if __name__ == "__main__":
    # here you setup the environment variables
    load_dotenv()
    BASE_URL = os.getenv("BASE_URL", "http://localhost:8080")
    API_KEY = os.getenv("API_KEY")

    if not API_KEY:
        raise ValueError("API_KEY not found in .env file or environment variables.")

    app = App()
    app.initialize()
