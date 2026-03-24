import requests
import json
import os

key = "AIzaSyBCmf-8l6zR7qhwGBxxbIsgAyv09c20iV4"
url = f"https://generativelanguage.googleapis.com/v1beta/models?key={key}"

try:
    response = requests.get(url)
    models = response.json().get('models', [])
    for m in models:
        # We want models supported for 'generateContent'
        if 'generateContent' in m.get('supportedGenerationMethods', []):
            print(f"Model ID: {m['name']}, Method: generateContent")
except Exception as e:
    print("Error:", e)
