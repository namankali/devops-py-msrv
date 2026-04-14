from .config import ollama, OLLAMA_MODEL
from .prompts import system_message
from .tool_schema import tools
from .tool_handler import handle_tool_call
from .logger import log_event
from app.ai_agent.rag.index import query_rag


# Intent Detection
def is_log_query(message: str) -> bool:
    message = message.lower()
    return any(k in message for k in ["error", "fail", "failure", "log", "why"])


def is_data_query(message: str) -> bool:
    message = message.lower()
    return any(k in message for k in ["list", "get", "fetch", "show", "students"])


def is_action_query(message: str) -> bool:
    message = message.lower()
    return any(k in message for k in ["issue", "revoke", "create"])


def run_agent(message, history, token):
    history = [{"role": h["role"], "content": h["content"][0]["text"]} for h in history]

    # avoid stale memory
    history = history[-6:]

    rag_context = ""
    if is_log_query(message):
        rag_context = query_rag(message, k=5, log_type="tool_response")

    messages = [{"role": "system", "content": system_message}]

    if rag_context:
        messages.append(
            {
                "role": "system",
                "content": f"""Relevant system logs:

            {rag_context}

        If answer can be derived from logs → DO NOT call tools.
        """,
            }
        )

    messages += history
    messages.append({"role": "user", "content": message})

    MAX_STEPS = 5

    try:
        log_event("user_input", message)

        for step in range(MAX_STEPS):
            print(f"\n----- Agent step {step+1} -----")

            response = ollama.chat(
                model=OLLAMA_MODEL,
                messages=messages,
                tools=tools,
                options={"temperature": 0},
            )

            msg = response.message

            log_event("llm_step", {"step": step + 1, "response": str(msg)})
            print(f"LLM Response: {msg}")
            
            if not getattr(msg, "tool_calls", None):
                print("Final response reached ----")

                if not msg.content:
                    return "No response generated. Please try again."

                log_event("final_output", msg.content)
                return msg.content

            # BLOCK tools for log queries
            if is_log_query(message) and not is_action_query(message):
                print("Tool call blocked (log query)")

                messages.append(
                    {
                        "role": "system",
                        "content": "Answer using logs only. Do NOT call tools.",
                    }
                )

                continue

            # TOOL for data queries
            if is_data_query(message):
                print("Forcing fresh tool call (data query)")

            elif not is_action_query(message):
                # normal question → don't force tool
                if msg.content:
                    return msg.content

            tool_response = handle_tool_call(msg, token)

            log_event("tool_response", tool_response)

            messages.append({"role": "assistant", "tool_calls": msg.tool_calls})

            messages.append(tool_response)

            # invalidate stale memory
            messages.append(
                {
                    "role": "system",
                    "content": "System state updated. Previous data may be outdated. Always use latest tool results.",
                }
            )

        return "Reached max steps. Please refine your request."

    except Exception as e:
        print("Agent Error:", e)
        return f"System error: {str(e)}"
