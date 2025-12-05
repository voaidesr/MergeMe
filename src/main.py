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

    # play with the api
    client = ApiClient(base_url=BASE_URL, api_key=API_KEY)

    try:
        client.start_session()
        hour_request = HourRequestDto(day=0, hour=0)
        response = client.play_round(hour_request)
        print(response)


    except requests.exceptions.HTTPError as e:
        print(f"HTTP Error: {e.response.status_code} {e.response.reason}")
        print(e.response.json())
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        if client.session_id:
            client.end_session()
