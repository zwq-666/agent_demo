"""最小连通性测试：只验证 key + base_url + model 能不能通。运行: python test_llm.py"""

import os
import sys

from dotenv import load_dotenv

from llm_client import OpenAICompatibleClient

load_dotenv()

api_key = os.environ.get("API_KEY", "")
base_url = os.environ.get("BASE_URL", "")
model = sys.argv[1] if len(sys.argv) > 1 else os.environ.get("MODEL_ID", "")

if not all([api_key, base_url, model]) or model.startswith("YOUR"):
    raise SystemExit("请先在 .env 填好 API_KEY / BASE_URL / MODEL_ID，或: python test_llm.py 模型名")

print(f"BASE_URL = {base_url}")
print(f"MODEL_ID = {model}")
print("-" * 40)

client = OpenAICompatibleClient(model=model, api_key=api_key, base_url=base_url)
reply = client.generate("请只回复两个字：你好", system_prompt="你是一个简洁的助手。")

print("-" * 40)
print("模型回复:", reply)
