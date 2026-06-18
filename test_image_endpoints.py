import requests
import json
import base64

TOKEN = '0933c226-0065-4f9d-aca9-79d97716b72b'
HEADERS = {
    'Authorization': f'Bearer {TOKEN}',
    'Content-Type': 'application/json'
}

def save_base64_image(base64_str, output_path):
    if "," in base64_str:
        base64_str = base64_str.split(",")[1]
    img_data = base64.b64decode(base64_str)
    with open(output_path, "wb") as f:
        f.write(img_data)
    print(f"Saved to {output_path}")

print("Testing vanguard sheet generation...")
try:
    res = requests.post(
        'https://api.pixellab.ai/v2/create-image-pixflux',
        headers=HEADERS,
        json={
            "description": "vanguard warrior in heavy armor with sword and shield, dark fantasy style. pixel art spritesheet, contains idle, walk, attack, hit, death animation frames, horizontal grid layout, transparent background",
            "image_size": {"width": 256, "height": 128},
            "no_background": True
        }
    )
    res.raise_for_status()
    data = res.json()
    save_base64_image(data['image']['base64'], 'test_vanguard_sheet.png')
except Exception as e:
    print("Vanguard sheet error:", e)
