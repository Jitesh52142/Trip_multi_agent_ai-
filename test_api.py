import requests
import sys

key = 'NgNQCzCKrNvRCJe7AcMz29gS'

# 1. Test Serper
try:
    r = requests.post("https://google.serper.dev/search", headers={"X-API-KEY": key}, json={"q": "flights"})
    if r.status_code == 200:
        print("Serper works!")
        sys.exit(0)
    else:
        print("Serper failed:", r.status_code, r.text)
except Exception as e:
    print("Serper error:", e)

# 2. Test Serpapi
try:
    r = requests.get(f"https://serpapi.com/search?api_key={key}&q=flights")
    if r.status_code == 200:
        print("Serpapi works!")
        sys.exit(0)
    else:
        print("Serpapi failed:", r.status_code, r.text)
except Exception as e:
    print("Serpapi error:", e)
