import requests
params = {
    "engine": "google_travel_explore",
    "q": "Flights to Delhi",
    "api_key": "NgNQCzCKrNvRCJe7AcMz29gS" # As requested
}
try:
    res = requests.get("https://www.searchapi.io/api/v1/search", params=params)
    print(res.status_code)
    print(str(res.json())[:500])
except Exception as e:
    print(e)
