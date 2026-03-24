import requests
params = {
    "engine": "google",
    "q": "Flights to Delhi",
    "api_key": "NgNQCzCKrNvRCJe7AcMz29gS"
}
try:
    res = requests.get("https://www.searchapi.io/api/v1/search", params=params)
    print(res.status_code)
    print(str(res.json().keys()))
except Exception as e:
    print(e)
