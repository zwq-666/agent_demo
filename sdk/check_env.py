"""环境自检：检查依赖、环境变量、网络连通性。运行: python check_env.py"""

import importlib.util
import os

from dotenv import load_dotenv

load_dotenv()


def line(name, ok, detail=""):
    print(f"[{'OK ' if ok else 'FAIL'}] {name}{(' - ' + detail) if detail else ''}")


print("=== 1. 依赖包 ===")
for pkg, mod in [
    ("requests", "requests"),
    ("tavily-python", "tavily"),
    ("openai", "openai"),
    ("python-dotenv", "dotenv"),
]:
    line(pkg, importlib.util.find_spec(mod) is not None)

print("\n=== 2. 环境变量 ===")
for key in ["API_KEY", "BASE_URL", "MODEL_ID", "TAVILY_API_KEY"]:
    val = os.environ.get(key, "")
    shown = (val[:6] + "...") if val and not val.startswith("YOUR") else ""
    line(key, bool(val) and not val.startswith("YOUR"), shown)

print("\n=== 3. 网络连通性 ===")
import requests

try:
    r = requests.get("https://wttr.in/Beijing?format=j1", timeout=10)
    line("wttr.in 天气接口", r.status_code == 200, f"HTTP {r.status_code}")
except Exception as e:
    line("wttr.in 天气接口", False, f"{type(e).__name__}: {e}")

base_url = os.environ.get("BASE_URL", "")
if base_url and not base_url.startswith("YOUR"):
    try:
        r = requests.get(base_url, timeout=10)
        line(f"LLM base_url ({base_url})", r.status_code < 500, f"HTTP {r.status_code}")
    except Exception as e:
        line(f"LLM base_url ({base_url})", False, f"{type(e).__name__}: {e}")
else:
    line("LLM base_url", False, "未配置")
