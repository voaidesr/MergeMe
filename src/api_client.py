import requests
from utils import HourRequestDto
class ApiClient:
    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url
        self.api_key = api_key
        self.session_id = None
        self._session = requests.Session()

    def _get_headers(self):
        headers = {"API-KEY": self.api_key}
        if self.session_id:
            headers["SESSION-ID"] = self.session_id
        return headers

    def start_session(self) -> str:
        url = f"{self.base_url}/api/v1/session/start"
        headers = {"API-KEY": self.api_key}
        response = self._session.post(url, headers=headers)
        response.raise_for_status()
        self.session_id = response.text
        print(f"Session started: {self.session_id}")
        return self.session_id

    def play_round(self, hour_request: HourRequestDto) -> dict:
        if not self.session_id:
            raise Exception("Session not started. Call start_session() first.")

        url = f"{self.base_url}/api/v1/play/round"

        request_body = hour_request.to_dict()

        response = self._session.post(url, headers=self._get_headers(), json=request_body)
        response.raise_for_status()
        return response.json()

    def end_session(self) -> dict:
        if not self.session_id:
            raise Exception("Session not started.")

        url = f"{self.base_url}/api/v1/session/end"
        response = self._session.post(url, headers=self._get_headers())
        response.raise_for_status()
        print("Session ended.")
        return response.json()

if __name__ == '__main__':
    BASE_URL = "http://127.0.0.1:8080"
    API_KEY = "38287-aed3-4556-9328-329188b39a7a"

    client = ApiClient(base_url=BASE_URL, api_key=API_KEY)

    try:
        client.start_session()

        hour_request = HourRequestDto(day=0, hour=0)

        response = client.play_round(hour_request)
        print("Play round response:", response)

    except requests.exceptions.HTTPError as e:
        print(f"HTTP Error: {e.response.status_code} {e.response.reason}")
        print(e.response.json())
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        if client.session_id:
            client.end_session()
