import requests
import time
import json

TOKEN = '0933c226-0065-4f9d-aca9-79d97716b72b'
HEADERS = {
    'Authorization': f'Bearer {TOKEN}',
    'Content-Type': 'application/json'
}

print("Submitting vanguard character creation job...")
res = requests.post(
    'https://api.pixellab.ai/v2/create-character-v3',
    headers=HEADERS,
    json={
        "description": "heavy armored knight vanguard, dark fantasy style, highly detailed pixel art",
        "detail": "high detail",
        "image_size": {"width": 64, "height": 64},
        "outline": "single color black outline",
        "view": "side"
    }
)
res.raise_for_status()
job = res.json()
print("Job submitted:", job)

if 'background_job_id' in job:
    job_id = job['background_job_id']
elif 'job_id' in job:
    job_id = job['job_id']
elif 'id' in job:
    job_id = job['id']
else:
    print("Cannot find job ID in response")
    exit(1)

print(f"Polling job {job_id}...")
while True:
    time.sleep(5)
    res = requests.get(f'https://api.pixellab.ai/v2/background-jobs/{job_id}', headers=HEADERS)
    res.raise_for_status()
    status = res.json()
    state = status.get('status')
    print(f"Status: {state}")
    if state == 'completed':
        print(json.dumps(status['result'], indent=2))
        
        # Now get the character info
        char_id = status['result'].get('character_id') or status['result'].get('id')
        if char_id:
            char_res = requests.get(f'https://api.pixellab.ai/v2/characters/{char_id}', headers=HEADERS)
            print("Character info:")
            print(json.dumps(char_res.json(), indent=2))
        break
    elif state == 'failed':
        print("Failed!", status)
        break
