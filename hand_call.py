import json
import os
import sys

import requests

KEY = os.environ.get("GROQ_API_KEY")  # read from the terminal, never from a file
if not KEY:
    sys.exit("GROQ_API_KEY is not set in this terminal window")

BASE = "https://api.groq.com/openai/v1"
HEADERS = {"Authorization": f"Bearer {KEY}"}

# No argument: just list the models this key can use.
if len(sys.argv) < 2:
    r = requests.get(f"{BASE}/models", headers=HEADERS, timeout=30)
    r.raise_for_status()
    for model_id in sorted(m["id"] for m in r.json()["data"]):
        print(model_id)
    sys.exit(0)

# With an argument: one chat call using that model id.
body = {
    "model": sys.argv[1],
    "temperature": 0,                              # same input -> same output
    "response_format": {"type": "json_object"},    # reply must be valid JSON
    "messages": [
        {"role": "system", "content": "You extract job info. Reply with JSON only."},
        {
            "role": "user",
            "content": 'Text: "Data Engineer - Kathmandu - Junior". '
                       'Return JSON: {"title": "", "location": "", "level": ""}',
        },
    ],
}
r = requests.post(f"{BASE}/chat/completions", headers=HEADERS, json=body, timeout=60)
print("status:", r.status_code)
for name, value in r.headers.items():  # rate-limit info lives in the headers
    if name.lower().startswith("x-ratelimit") or name.lower() == "retry-after":
        print(f"{name}: {value}")
print(json.dumps(r.json(), indent=2))