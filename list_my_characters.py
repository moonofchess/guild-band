import requests
import json

TOKEN = '0933c226-0065-4f9d-aca9-79d97716b72b'
HEADERS = {
    'Authorization': f'Bearer {TOKEN}',
    'Content-Type': 'application/json'
}

res = requests.get('https://api.pixellab.ai/v2/characters', headers=HEADERS)
print("My Characters:")
print(json.dumps(res.json(), indent=2))
