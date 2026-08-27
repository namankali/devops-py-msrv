from .config import ollama, OLLAMA_MODEL
from .prompts import system_prompt
from app.utils.validator import Validator
from .tool_handler import ToolHandler
from .took_schema import tools
from .intents import classify_intent
import json
from rich.console import Console
from .provider import get_llm_provider

console = Console()


def extract_response_content(content):
    if not content:
        return "No response generated"

    try:
        parsed = json.loads(content)
        print("parsed data: ", parsed)
        if isinstance(parsed, dict):
            response_type = parsed.get("type")
            data = parsed.get("data")

            if response_type == "repo_list" and isinstance(data, list):
                if not data:
                    return "No repositories found."

                lines = ["Here are your repositories:"]

                for repo in data:
                    name = repo.get("name", "Unknown")
                    language = repo.get("language") or "Unknown"
                    visibility = repo.get("visibility", "Unknown")

                    lines.append(f"- {name} — {language} — {visibility}")

                return "\n".join(lines)

            return (
                parsed.get("message")
                or parsed.get("response")
                or parsed.get("content")
                or parsed.get("answer")
                or json.dumps(parsed, indent=2)
            )

        return str(parsed)

    except json.JSONDecodeError:
        return content


def normalize_history(history=None):
    normalized = []

    if not history:
        return normalized

    for h in history:
        role = h.get("role", "user")
        content = h.get("content", "")

        if isinstance(content, list):
            text = content[0].get("text", "") if content else ""
        else:
            text = str(content)

        normalized.append({"role": role, "content": text})

    return normalized


def run_agent(message, history, token):
    print("incoming message ->>>>", message)
    print("history ->>>>", history)

    conversation_history = normalize_history(history=history)

    print("normalized history ->>>>", conversation_history)

    # Context-aware intent classification
    intent = classify_intent(message, conversation_history)
    print("Intent ->>>>", intent)

    messages = [
        {"role": "system", "content": (system_prompt + f"\nUser intent: {intent}")}
    ]

    messages.extend(conversation_history)

    messages.append({"role": "user", "content": message})
    rag_used = False

    if intent in ["rag"] or Validator.is_rag_call(message=message):
        try:
            print("RAG triggered")

            rag_context = ToolHandler.get_rag_context(message, token)
            print("rag context ->>>> ", rag_context)

            if rag_context:
                rag_used = True
                messages.append(
                    {
                        "role": "system",
                        "content": f"""
                            Relevant context:
                            
                            {rag_context}
                            
                            Use this context to answer the user's question.
                            Do not invent anything outside this context.
                        """,
                    }
                )
            else:
                if intent == "rag":
                    return (
                        f"No stored build failure data was found in the knowledge base for "
                        f"the repository {ToolHandler.extract_repo_hint(message=message)} "
                        f"on the {ToolHandler.extract_repo_name(message=message)} branch."
                    )

        except Exception as e:
            print("RAG Error:", e)

            if intent == "rag":
                return f"RAG search failed: {str(e)}"

    MAX_STEPS = 2

    try:
        for step in range(MAX_STEPS):
            console.print(f"Step {step + 1}", style="blue")

            use_tools = intent in ["action", "live_query", "save_repo"]

            # If RAG already found stored context, do not call live tools.
            if rag_used and intent != "live_query":
                use_tools = False

            llm = get_llm_provider()

            response = llm.chat(messages=messages, tools=tools if use_tools else None)

            msg = response.message
            print("LLM response ->>>>", msg)

            tool_calls = getattr(msg, "tool_calls", None)
            # print("tool_calls value", tool_calls)

            if not tool_calls:
                if intent == "rag" and not rag_used:
                    return "I couldn't find relevant data in the knowledge base. Try refining your query."

                return extract_response_content(msg.content)

            handler = ToolHandler(msg, token=token)

            try:
                tool_response = handler.handle_tool_call()
                print("tool_response", tool_response)
            except Exception as e:
                print("Tool Error:", e)
                return f"Tool execution failed: {str(e)}"

            tool_name = tool_calls[0].function.name

            messages.append(
                {
                    "role": "assistant",
                    "content": msg.content or "",
                    "tool_calls": tool_calls,
                }
            )

            messages.append(
                {
                    "role": "tool",
                    "name": tool_name,
                    "content": (
                        tool_response.get("content", "")
                        if isinstance(tool_response, dict)
                        else str(tool_response)
                    ),
                }
            )

        return "Reached max steps. Please refine your request."

    except Exception as e:
        print("Agent Error:", e)
        return f"System error: {str(e)}"
