import requests
import os
from dotenv import load_dotenv

load_dotenv()

key = os.getenv("SEARCHAPI_API_KEY", "NgNQCzCKrNvRCJe7AcMz29gS")
params = {"engine": "google", "q": "flights to Goa", "api_key": key}

try:
    response = requests.get("https://www.searchapi.io/api/v1/search", params=params, timeout=10)
    print("Status Code:", response.status_code)
    if response.status_code == 200:
        print("Success!")
        data = response.json()
        print("Results count:", len(data.get("organic_results", [])))
    else:
        print("Error:", response.text)
except Exception as e:
    print("Request failed:", e)
