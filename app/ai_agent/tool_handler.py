import json
from .tools import get_build_details_by_branch

ALLOWED_TOOLS = ["github_events", "list_repos"]


class ToolHandler:
    def __init__(self, message, token):
        self.message = message
        self.token = token or ""

    def handle_tool_call(self):
        tool_call = self.message.tool_calls[0]
        tool_name = tool_call.function.name
        arguments = json.loads(tool_call.function.arguments or "{}")

        print("🔧 Tool call:", tool_name, "args:", arguments)

        if tool_name not in ALLOWED_TOOLS:
            return {
                "role": "tool",
                "name": tool_name,
                "content": json.dumps({
                    "success": False,
                    "error": f"Unknown tool: {tool_name}"
                }),
            }

        try:
            if tool_name == "github_events":
                result = get_build_details_by_branch(self.token)

            elif tool_name == "list_repos":
                result = get_build_details_by_branch(self.token, repos=True)

            return {
                "role": "tool",
                "name": tool_name,
                "content": json.dumps(result),
            }

        except Exception as e:
            return {
                "role": "tool",
                "name": tool_name,
                "content": json.dumps({
                    "success": False,
                    "error": str(e)
                }),
            }