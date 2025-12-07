import os
from typing import Dict
import requests
from dotenv import load_dotenv
from api_client import ApiClient
from models import *

from dataclasses import dataclass
from state import State
from context import Context
from decision_maker import DecisionMaker
from utils import encode_time

DATA_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data"
)

@dataclass
class App:
    context: Context = field(default_factory=Context)
    state: State = field(init=False)
    decisionMaker: DecisionMaker = field(init=False)

    def __post_init__(self):
        # All share the same context reference
        self.state = State(self.context)
        self.decisionMaker = DecisionMaker(self.context)

    def connect_api(self):
        load_dotenv()
        BASE_URL = os.getenv("BASE_URL", "http://localhost:8080")
        API_KEY = os.getenv("API_KEY")

        if not API_KEY:
            raise ValueError("API_KEY not found in .env file or environment variables.")
        # play with the api
        self.client = ApiClient(base_url=BASE_URL, api_key=API_KEY)

    def run(self):
        # connect the api
        self.connect_api()
        try:
            self.client.start_session()

            end_time = 30 * 24
            lastCost = -1
            totalPenalty = 0
            penal = {}
            # main loop for every hour
            while self.state.time < end_time:
                self.state.init_update_state()
                # 1. make a descision
                #decision = self.decisionMaker.empty_decision(self.state)
                decision = self.decisionMaker.make_decision(self.state)

                # print(decision)
                # 2. send the decision and get the next round
                response = self.client.play_round(decision)
                #print(response['penalties'])
                lastCost = response['totalCost']

                for penalty in response['penalties']:
                    totalPenalty += penalty['penalty']
                    pen_code = penalty['code']
                    
                    if pen_code not in penal:
                        penal[pen_code] = 0

                    penal[pen_code] += 1

                # 3. update the state with the next round
                self.state.update_state(response)

            print(f"Last Cost: {lastCost:,.2f} Total penalty: {totalPenalty:,.2f}")
            print(penal)
        except requests.exceptions.HTTPError as e:
            print(f"HTTP Error: {e.response.status_code} {e.response.reason}")
            print(e.response.json())
        except Exception as e:
            print(f"Exception: {e}")
        finally:
            MAX_END_TIME = 24 * 30
            if self.state.time < MAX_END_TIME:
                self.client.end_session()
