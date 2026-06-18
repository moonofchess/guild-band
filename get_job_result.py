import requests
import json

TOKEN = '0933c226-0065-4f9d-aca9-79d97716b72b'
HEADERS = {
    'Authorization': f'Bearer {TOKEN}',
    'Content-Type': 'application/json'
}

job_id = 'b6cb229c-1014-4954-ba46-2b867b048776'
res = requests.get(f'https://api.pixellab.ai/v2/background-jobs/{job_id}', headers=HEADERS)
print("Job Response:")
print(json.dumps(res.json(), indent=2))

char_id = 'c1083196-418a-467d-906e-1595bb12a4fa'
char_res = requests.get(f'https://api.pixellab.ai/v2/characters/{char_id}', headers=HEADERS)
print("Character Response:")
print(json.dumps(char_res.json(), indent=2))
