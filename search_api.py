import json

path = r"C:\Users\Admin\.gemini\antigravity\brain\29d3c65f-d037-4dba-b34c-8193a27dc0cc\.system_generated\steps\284\content.md"

with open(path, "r", encoding="utf-8") as f:
    lines = f.readlines()

json_str = ""
for line in lines:
    if line.strip().startswith("{"):
        json_str = line
        break
    if json_str:
        json_str += line

data = json.loads(json_str)
schemas = data.get("components", {}).get("schemas", {})

for s in ["CreateImagePixfluxRequest", "CreateImagePixenRequest"]:
    if s in schemas:
        print(f"=== Schema: {s} ===")
        print(json.dumps(schemas[s], indent=2))
