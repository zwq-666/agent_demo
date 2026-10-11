"""列出当前网关支持的模型。运行: python list_models.py"""

import os

import requests
from dotenv import load_dotenv

load_dotenv()

base_url = os.environ["BASE_URL"].rstrip("/")
api_key = os.environ["API_KEY"]

r = requests.get(
    f"{base_url}/models",
    headers={"Authorization": f"Bearer {api_key}"},
    timeout=30,
)
print("HTTP", r.status_code)

if r.status_code != 200:
    print(r.text[:1000])
    raise SystemExit(1)

data = r.json()
items = data.get("data", data) if isinstance(data, dict) else data
ids = sorted(str(m.get("id")) for m in items if isinstance(m, dict))

print(f"\n共 {len(ids)} 个模型:\n")
for i in ids:
    print(" -", i)

with open("models.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(ids))
print("\n已保存到 models.txt")
