"""Inline data.json into template.html to produce the final self-contained index.html."""
import json

with open("../site/data.json") as f:
    data = json.load(f)

with open("../site/template.html", encoding="utf-8") as f:
    template = f.read()

output = template.replace("__DATA_JSON__", json.dumps(data))

with open("../site/index.html", "w", encoding="utf-8") as f:
    f.write(output)

print(f"Built ../site/index.html ({len(output):,} bytes)")
