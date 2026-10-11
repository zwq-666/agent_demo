# 智能体最小实现（1.3 动手体验）

一个由真实 LLM 驱动的旅行助手智能体：查天气 -> 搜景点 -> 给出推荐。

## 文件说明

| 文件 | 作用 |
| --- | --- |
| `tools.py` | 两个工具：`get_weather`（wttr.in，免 key）、`get_attraction`（Tavily，需 key） |
| `llm_client.py` | `OpenAICompatibleClient`，兼容任何 OpenAI 风格接口的 LLM 客户端 |
| `agent.py` | 主程序：指令模板 + 行动循环（Thought -> Action -> Observation） |
| `check_env.py` | 环境自检：依赖 / 环境变量 / 网络 |
| `.env.example` | 配置模板，复制成 `.env` 后填值 |

## 快速开始

```powershell
cd D:\agent-learn\2026-10-11\sdk

# 1. 装依赖（requests/tavily-python/openai 已装，这里补 dotenv）
pip install -r requirements.txt

# 2. 创建配置文件并填写
Copy-Item .env.example .env
notepad .env

# 3. 自检
python check_env.py

# 4. 运行
python agent.py
```

## `.env` 需要填什么

```ini
API_KEY=sk-xxxxxx           # LLM 服务商的 key
BASE_URL=https://api.deepseek.com/v1
MODEL_ID=deepseek-chat
TAVILY_API_KEY=tvly-xxxxxx  # https://app.tavily.com 注册后获取
```

常见服务商组合：

| 服务商 | BASE_URL | MODEL_ID 示例 |
| --- | --- | --- |
| OpenAI 官方 | `https://api.openai.com/v1` | `gpt-4o-mini` |
| DeepSeek | `https://api.deepseek.com/v1` | `deepseek-chat` |
| 智谱 GLM | `https://open.bigmodel.cn/api/paas/v4` | `glm-4-flash` |
| 阿里通义 | `https://dashscope.aliyuncs.com/compatible-mode/v1` | `qwen-plus` |
| 本地 Ollama | `http://localhost:11434/v1` | `qwen2.5:7b` |

## 预期输出

```
用户输入: 你好，请帮我查询一下今天北京的天气，然后根据天气推荐一个合适的旅游景点。
========================================
--- 循环 1 ---
模型输出:
Thought: 首先需要获取北京今天的天气情况...
Action: get_weather(city="北京")
Observation: 北京当前天气:Sunny，气温26摄氏度
========================================
--- 循环 2 ---
Action: get_attraction(city="北京", weather="Sunny")
Observation: 北京在晴天最值得去的旅游景点是颐和园...
========================================
--- 循环 3 ---
Action: Finish[今天北京的天气是晴朗的...]
任务完成，最终答案: ...
```

## 注意事项

- `.env` 含密钥，**不要提交到 git**。
- 如果 LLM 不支持"工具调用风格"的指令模板（小模型容易不听话），可换更强的模型。
- `wttr.in` 偶发不稳定，失败会返回"错误:查询天气时遇到网络问题"，属于正常降级。
