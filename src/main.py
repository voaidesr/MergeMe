import os
import sys

import requests
from dotenv import load_dotenv
from api_client import ApiClient
from app import App
from utils import HourRequestDto
import json

if __name__ == "__main__":
    app = App()
    
    app.initialize()
    app.run()
