import os
from litellm import completion
from dotenv import load_dotenv

load_dotenv()

# The user has GOOGLE_API_KEY in .env, trip_planner_system.py sets GEMINI_API_KEY from it.
if "GEMINI_API_KEY" not in os.environ and "GOOGLE_API_KEY" in os.environ:
    os.environ["GEMINI_API_KEY"] = os.environ["GOOGLE_API_KEY"]

# Test possible model names
models = ["gemini/gemini-1.5-flash", "gemini/gemini-2.0-flash-exp", "gemini/gemini-2.0-flash"]

for model in models:
    try:
        print(f"Testing model: {model}")
        response = completion(
            model=model,
            messages=[{"role": "user", "content": "Say hello!"}]
        )
        print(f"Success with {model}!")
        print(response.choices[0].message.content)
        break
    except Exception as e:
        print(f"Failed with {model}: {e}")
