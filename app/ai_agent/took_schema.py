github_events = {
    "name": "github_events",
    "description": (
        "Get Github actions workflow run and build information"
        "Use this tool when user asks about build, workflow runs,"
        "CI/CD status, build failure and build history"
        "Supports one or more rpeositories and optional branch/ date filters"
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "repo_name": {
                "type": "array",
                "items": {"type": "string"},
                "description": (
                    "One or more repositories names mentioned by the user"
                    "Example: ['devops-frontend', 'devops-backend']"
                ),
            },
            "branch": {
                "type": "string",
                "enum": ["development", "devlopment", "staging", "production"],
                "description": "The Git branch to filter by.",
            },
            "include_failed_reason": {
                "type": "boolean",
                "description": (
                    "Whether to fetch detailed failure reasons for failed workflow runs. "
                    "Set to true ONLY when the user explicitly asks why a build failed, "
                    "the failure reason, error details, or the cause of a failure. "
                    "Set to false when the user only asks for the number, count, "
                    "status, or history of failed builds."
                ),
                "default": False,
            },
            "start_date": {
                "type": "string",
                "description": "Start date in YYYY-MM-DD format.",
            },
            "end_date": {
                "type": "string",
                "description": "End date in YYYY-MM-DD format.",
            },
            "include_count": {
                "type": "boolean",
                "description": (
                    "Set to true when the user asks for a count, number, total, "
                    "or how many build failures occurred. "
                    "Set to false when the user asks for failure reasons, status, "
                    "or build history."
                ),
                "default": False,
            },
            "build": {
                "type": "string",
                "enum": ["failed", "success", "total"],
                "description": (
                    "The build outcome to filter by. "
                    "Set to 'failed' when the user asks about failed builds, "
                    "build failures, failed workflow runs, or failure count. "
                    "Set to 'success' when the user asks about successful, succeeded, "
                    "passing, or passed builds/workflow runs. "
                    "Set to 'total' when the user asks about the total number of builds, "
                    "all builds, build history without specifying success or failure, "
                    "or when no build outcome is specified."
                ),
                "default": "total",
            },
        },
        "required": ["repo_name", "branch"],
    },
}

# list_repos = {
#     "name": "list_repos",
#     "description": (
#         "Fetch repositories from the user's GitHub account. "
#         "The application decides whether registered or unregistered "
#         "repositories are requested."
#     ),
#     "parameters": {
#         "type": "object",
#         "properties": {
#             "registered_status": {
#                 "type": "string",
#                 "enum": [
#                     "registered",
#                     "unregistered",
#                     "all",
#                 ],
#             },
#             "visibility": {
#                 "type": "string",
#                 "enum": [
#                     "private",
#                     "public",
#                     "all",
#                 ],
#             },
#         },
#         "required": [
#             "registered_status",
#             "visibility",
#         ],
#     },
# }

list_repos = {
    "name": "list_repos",
    "description": "List all GitHub repositories for the authenticated user",
    "parameters": {
        "type": "object",
        "properties": {
            "registered_status": {
                "type": "string",
                "enum": ["registered", "unregistered", "all"],
                "description": (
                    "Filter repositories by whether they are registered in the "
                    "application database. "
                    "Use 'registered' when the user asks for repositories that "
                    "are already registered, stored in the database, or available "
                    "in the application. "
                    "Use 'unregistered' when the user asks for GitHub repositories "
                    "that are not registered in the application database. "
                    "Use 'all' when the user asks for all repositories or does not "
                    "specify a registration status."
                ),
                "default": "all",
            },
            "visibility": {
                "type": "string",
                "enum": ["private", "public", "all"],
                "description": (
                    "Filter repositories by GitHub visibility. "
                    "Use 'private' when the user asks for private repositories. "
                    "Use 'public' when the user asks for public repositories. "
                    "Use 'all' when the user asks for all repositories or does "
                    "not specify visibility."
                ),
                "default": "all",
            },
        },
        "required": ["registered_status"],
    },
}

single_repo_detail = {
    "name": "single_repo_detail",
    "description": "Details of single repo",
    "parameters": {
        "type": "object",
        "properties": {
            "repo_name": {
                "type": "string",
                "description": "This is name of the repository in github",
            }
        },
    },
    "required": ["repo_name"],
}

save_repo_to_db = {
    "name": "save_repo_to_db",
    "description": "Save one or more GitHub repositories to the database.",
    "parameters": {
        "type": "object",
        "properties": {
            "repo_ids": {
                "type": "array",
                "items": {"type": "string"},
                "description": "List of repo ids to register",
            },
            "repositories": {
                "type": "array",
                "items": {"type": "string"},
                "description": "List of repo names to save",
            },
        },
        "required": ["repo_ids"],
    },
}

tools = [
    {"type": "function", "function": github_events},
    {"type": "function", "function": list_repos},
    {"type": "function", "function": single_repo_detail},
    {"type": "function", "function": save_repo_to_db},
]
