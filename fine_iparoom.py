import requests
import os
from dotenv import load_dotenv
load_dotenv()

def get_room_id(title):
    ACCESS_TOKEN = os.getenv("webex_token")
    url = "https://webexapis.com/v1/rooms"
    headers = {"Authorization": f"Bearer {ACCESS_TOKEN}"}

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        rooms = response.json()["items"]
        for room in rooms:
            if room["title"] == title:
                return room["id"]
    return None


