"""Inline data.json into template.html to produce the final self-contained index.html."""
import json
import shutil
from datetime import datetime, timezone

with open("../site/data.json") as f:
    data = json.load(f)

with open("../site/template.html", encoding="utf-8") as f:
    template = f.read()

build_time = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
output = template.replace("__DATA_JSON__", json.dumps(data)).replace("__BUILD_TIME__", build_time)

with open("../site/index.html", "w", encoding="utf-8") as f:
    f.write(output)

print(f"Built ../site/index.html ({len(output):,} bytes)")

# Copy the PDF into site/ so the "Open full PDF report" links resolve as a
# same-directory relative path once the site is deployed on its own (the
# deployed site does not have access to sibling folders like ../output).
shutil.copyfile(
    "../output/RZR_Lead_Quality_Analysis.pdf",
    "../site/RZR_Lead_Quality_Analysis.pdf",
)
print("Copied PDF into ../site/")
