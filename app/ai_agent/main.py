from .config import ollama, OLLAMA_MODEL
from .prompts import system_prompt
from app.utils.validator import Validator
from .tool_handler import ToolHandler
from .took_schema import tools
from app.helper.formatters import FORMATTERS
import json


def run_agent(message, history, token):
    # Normalize history
    history = [
        {"role": h["role"], "content": h["content"][0]["text"]}
        for h in history
    ][-6:]

    messages = [{"role": "system", "content": system_prompt}]
    messages += history
    messages.append({"role": "user", "content": message})

    MAX_STEPS = 2

    try:
        print("🚀 Agent Input ->>>> ", messages)

        for step in range(MAX_STEPS):
            print(f"🔁 Step {step + 1}")

            response = ollama.chat(
                model=OLLAMA_MODEL,
                messages=messages,
                tools=tools,
                options={"temperature": 0},
            )

            msg = response.message

            # FINAL RESPONSE (no tool call)
            if not getattr(msg, "tool_calls", None):
                print("Final response ->>>> ", msg)

                return msg.content or "No response generated"

            # Optional: RAG routing (you already have hook)
            if not Validator.is_rag_call(message):
                pass

            # Execute tool
            handler = ToolHandler(msg, token=token)
            tool_response = handler.handle_tool_call()

            print("Tool response ->>>> ", tool_response)

            # Parse tool output
            try:
                parsed = json.loads(tool_response["content"])
            except Exception:
                return "Invalid tool response format"

            if not parsed.get("success"):
                return "Failed to fetch data. Please try again."

            tool_name = msg.tool_calls[0].function.name

            # FORMAT DIRECTLY (NO SECOND LLM CALL)
            formatter = FORMATTERS.get(tool_name)

            if formatter:
                return formatter(parsed.get("data", []))

            # ⚠ fallback (if no formatter defined)
            return parsed

        return "Reached max steps. Please refine your request"

    except Exception as e:
        print("❌ Agent Error:", e)
        return f"System error: {str(e)}"