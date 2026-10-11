"""
1.3.3 执行行动循环

运行前请在 .env 里填好 API_KEY / BASE_URL / MODEL_ID / TAVILY_API_KEY，
然后执行:  python agent.py
"""

import os
import re

from dotenv import load_dotenv

from llm_client import OpenAICompatibleClient
from tools import available_tools

load_dotenv()

# --- 0. 指令模板（智能体的"说明书"） ---
AGENT_SYSTEM_PROMPT = """你是一个智能旅行助手。你的任务是分析用户的请求，并使用可用工具一步步地解决问题。

# 可用工具:
- `get_weather(city: str)`: 查询指定城市的实时天气。
- `get_attraction(city: str, weather: str)`: 根据城市和天气搜索推荐的旅游景点。

# 输出格式要求:
你的每次回复必须严格遵循以下格式，包含一对Thought和Action：

Thought: [你的思考过程和下一步计划]
Action: [你要执行的具体行动]

Action的格式必须是以下之一：
1. 调用工具：function_name(arg_name="arg_value")
2. 结束任务：Finish[最终答案]

# 重要提示:
- 每次只输出一对Thought-Action
- Action必须在同一行，不要换行
- 当收集到足够信息可以回答用户问题时，必须使用 Action: Finish[最终答案] 格式结束

请开始吧！"""

# --- 1. 配置LLM客户端 ---
API_KEY = os.environ.get("API_KEY", "")
BASE_URL = os.environ.get("BASE_URL", "")
MODEL_ID = os.environ.get("MODEL_ID", "")


def main():
    if not (API_KEY and BASE_URL and MODEL_ID):
        raise SystemExit(
            "缺少配置：请在 .env 中填写 API_KEY / BASE_URL / MODEL_ID"
        )

    llm = OpenAICompatibleClient(model=MODEL_ID, api_key=API_KEY, base_url=BASE_URL)

    # --- 2. 初始化 ---
    user_prompt = "你好，请帮我查询一下今天北京的天气，然后根据天气推荐一个合适的旅游景点。"
    prompt_history = [f"用户请求: {user_prompt}"]

    print(f"用户输入: {user_prompt}\n" + "=" * 40)

    # --- 3. 运行主循环 ---
    for i in range(5):  # 设置最大循环次数
        print(f"--- 循环 {i + 1} ---\n")

        # 3.1 构建 Prompt
        full_prompt = "\n".join(prompt_history)

        # 3.2 调用LLM进行思考
        llm_output = llm.generate(full_prompt, system_prompt=AGENT_SYSTEM_PROMPT)

        # 模型可能会输出多余的 Thought-Action，需要截断
        match = re.search(
            r"(Thought:.*?Action:.*?)(?=\n\s*(?:Thought:|Action:|Observation:)|\Z)",
            llm_output,
            re.DOTALL,
        )
        if match:
            truncated = match.group(1).strip()
            if truncated != llm_output.strip():
                llm_output = truncated
                print("已截断多余的 Thought-Action 对")
        print(f"模型输出:\n{llm_output}\n")
        prompt_history.append(llm_output)

        # 3.3 解析并执行行动
        action_match = re.search(r"Action: (.*)", llm_output, re.DOTALL)
        if not action_match:
            observation = (
                "错误: 未能解析到 Action 字段。请确保你的回复严格遵循 "
                "'Thought: ... Action: ...' 的格式。"
            )
            observation_str = f"Observation: {observation}"
            print(f"{observation_str}\n" + "=" * 40)
            prompt_history.append(observation_str)
            continue

        action_str = action_match.group(1).strip()

        # 结束任务
        if action_str.startswith("Finish"):
            final_match = re.match(r"Finish\[(.*)\]", action_str, re.DOTALL)
            final_answer = final_match.group(1) if final_match else action_str
            print(f"任务完成，最终答案: {final_answer}")
            break

        # 调用工具
        tool_match = re.search(r"(\w+)\(", action_str)
        args_match = re.search(r"\((.*)\)", action_str, re.DOTALL)
        if not tool_match or not args_match:
            observation = f"错误: 无法解析工具调用 '{action_str}'"
            observation_str = f"Observation: {observation}"
            print(f"{observation_str}\n" + "=" * 40)
            prompt_history.append(observation_str)
            continue

        tool_name = tool_match.group(1)
        args_str = args_match.group(1)
        kwargs = dict(re.findall(r'(\w+)="([^"]*)"', args_str))

        if tool_name in available_tools:
            observation = available_tools[tool_name](**kwargs)
        else:
            observation = f"错误:未定义的工具 '{tool_name}'"

        # 3.4 记录观察结果
        observation_str = f"Observation: {observation}"
        print(f"{observation_str}\n" + "=" * 40)
        prompt_history.append(observation_str)


if __name__ == "__main__":
    main()
