import json
import re
import dateparser
from datetime import datetime
from .tools import (
    get_build_details_by_branch,
    save_repo_to_db,
    get_repo_details,
)
from app.helper.formatters import FORMATTERS
from app.rag.index import search_build_failure

from app.helper.general import GeneralHelpers

from rich.console import Console
from rich.pretty import Pretty

# Schema
from app.helper.schema import FailureData

console = Console()

from app.helper.formatters import get_repo_name

ALLOWED_TOOLS = [
    "github_events",
    "list_repos",
    "single_repo_detail",
    "save_repo_to_db",
]


class ToolHandler:
    def __init__(self, message, token):
        self.message = message
        self.token = token or ""

    def handle_tool_call(self):
        tool_call = self.message.tool_calls[0]
        tool_name = tool_call.function.name
        arguments = tool_call.function.arguments or "{}"

        if isinstance(arguments, str):
            arguments = json.loads(arguments)

        if tool_name not in ALLOWED_TOOLS:
            return {
                "role": "tool",
                "name": tool_name,
                "content": json.dumps(
                    {"success": False, "error": f"Unknown tool: {tool_name}"}
                ),
            }

        try:
            if tool_name == "github_events":
                if ("start_date" in arguments and "end_date" in arguments) or (
                    "date" in arguments
                ):
                    result = get_build_details_by_branch(
                        self.token,
                        branch=arguments.get("branch") or "development",
                        start_date=arguments.get("start_date") or arguments.get("date"),
                        end_date=arguments.get("end_date") or arguments.get("date"),
                        repo_name=arguments.get("repo_name"),
                        repo="single",
                        build=arguments.get("build"),
                    )
                else:
                    result = get_build_details_by_branch(
                        self.token,
                        branch=arguments.get("branch") or "development",
                        repo="single",
                        repo_name=arguments.get("repo_name"),
                        start_date=arguments.get("start_date"),
                        count=arguments.get("include_count", False),
                        build=arguments.get("build"),
                    )

            elif tool_name == "list_repos":
                result = get_repo_details(
                    self.token,
                    registered_status=arguments.get("registered_status"),
                    visibility=arguments.get("visibility"),
                )

            elif tool_name == "single_repo_detail":
                result = get_build_details_by_branch(
                    self.token,
                    repo_name=arguments.get("repo_name"),
                    repo="single",
                )

            elif tool_name == "save_repo_to_db":
                # print("arguments ", arguments)
                result = save_repo_to_db(self.token, arguments.get("repo_ids"))

            if arguments.get("include_failed_reason"):
                failure_data_node: list[FailureData] = result.get("data", [])

                general = GeneralHelpers(failure_data=failure_data_node)

                run_ids = general.get_failed_run_reason()

            formatter = FORMATTERS.get(tool_name)

            if formatter and result.get("success"):
                if tool_name == "github_events":
                    formatted_content = formatter(
                        result.get("data", []),
                        bool(arguments.get("start_date") or arguments.get("date")),
                        bool(arguments.get("include_count")),
                    )
                elif tool_name == "list_repos":
                    if arguments.get("registered_status") == "unregistered":
                        formatter = FORMATTERS.get("fetch_unregistered_repos")
                        formatted_content = formatter(result.get("data", []))
                    else:
                        formatted_content = formatter(result.get("data", []))

                else:
                    formatted_content = formatter(result.get("data", []))
            else:
                formatted_content = json.dumps(result)

            return {
                "role": "tool",
                "name": tool_name,
                "content": formatted_content,
            }

        except Exception as e:
            return {
                "role": "tool",
                "name": tool_name,
                "content": json.dumps({"success": False, "error": str(e)}),
            }

    @staticmethod
    def extract_repo_hint(message: str):
        """
        Extract repo name from messages like:
        - why build failed related to repo devops-frontend
        - why did namankali/devops-frontend fail
        - check build failure for repository devops-frontend
        """

        if not message:
            return None

        message = message.strip()

        full_repo_match = re.search(r"([a-zA-Z0-9_.-]+/[a-zA-Z0-9_.-]+)", message)

        if full_repo_match:
            return full_repo_match.group(1)

        repo_match = re.search(
            r"(?:repo|repository)\s+([a-zA-Z0-9_.-]+)", message, re.IGNORECASE
        )

        if repo_match:
            return repo_match.group(1)

        return None

    @staticmethod
    def get_rag_context(message: str, token: str):

        repo_hint = ToolHandler.extract_repo_hint(message=message)

        full_repo_name = get_repo_name(repo_hint)

        failure_date = ToolHandler.extract_date(message=message)

        req_branch = ToolHandler.extract_repo_name(message=message)

        # DB search
        points = search_build_failure(
            query=message,
            repo_name=full_repo_name,
            failure_date=failure_date,
            branch=req_branch,
        )

        if not points:
            print("No RAG points found")
            return ""

        if repo_hint and "/" not in repo_hint:
            filtered_points = []

            for point in points:
                payload = point.payload or {}
                stored_repo_name = str(payload.get("repo_name", "")).lower()

                if repo_hint.lower() in stored_repo_name:
                    filtered_points.append(point)

            if filtered_points:
                points = filtered_points

        context_blocks = []

        for index, point in enumerate(points, start=1):
            payload = point.payload or {}

            context_blocks.append(f"""
                    Result: {index}
                    Score: {getattr(point, "score", None)}
                    
                    Repository: {payload.get("repo_name")}
                    Workflow: {payload.get("workflow_name")}
                    Job: {payload.get("job_name")}
                    Branch: {payload.get("branch")}
                    Commit: {payload.get("commit_sha")}
                    Run ID: {payload.get("run_id")}
                    Job ID: {payload.get("job_id")}
                    URL: {payload.get("html_url")}
                    
                    Failure Category:
                    {payload.get("failure_category")}

                    Failure Reason:
                    {payload.get("failure_reason")}

                    Probable Fix:
                    {payload.get("probable_fix", "No probable fix stored. Infer carefully from the failure reason.")}
                """)

            rag_context = "\n\n".join(context_blocks)

            return rag_context

    @staticmethod
    def extract_date(message: str):
        if not message:
            return None

        date_patterns = [
            # YYYY-MM-DD / YYYY/MM/DD
            r"\b\d{4}[-/]\d{1,2}[-/]\d{1,2}\b",
            # DD-MM-YYYY / DD/MM/YYYY
            r"\b\d{1,2}[-/]\d{1,2}[-/]\d{4}\b",
            # 12 August 2026 / 12 August, 2026
            r"\b\d{1,2}\s+"
            r"(?:January|February|March|April|May|June|July|August|"
            r"September|October|November|December)"
            r"(?:,)?\s+\d{4}\b",
            # August 12 2026 / August 12, 2026
            r"\b(?:January|February|March|April|May|June|July|August|"
            r"September|October|November|December)"
            r"\s+\d{1,2}(?:st|nd|rd|th)?"
            r"(?:,)?\s+\d{4}\b",
            # Aug 12, 2026
            r"\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)"
            r"\s+\d{1,2}(?:st|nd|rd|th)?"
            r"(?:,)?\s+\d{4}\b",
        ]

        for pattern in date_patterns:
            match = re.search(pattern, message, re.IGNORECASE)

            if match:
                date_text = match.group(0)

                parsed_date = dateparser.parse(
                    date_text,
                    languages=["en"],
                    settings={
                        "DATE_ORDER": "DMY",
                    },
                )

                if parsed_date:
                    return parsed_date.strftime("%Y-%m-%d")

        return None

    @staticmethod
    def extract_repo_name(message: str):
        branches = ["development", "devlopment", "staging", "production", "main"]
        for ele in branches:
            if ele in message.lower():
                return ele

        return None
