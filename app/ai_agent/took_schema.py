github_events = {
    "name": "github_events",
    "description": "Get CI/CD workflow, build, and pipeline execution details",
    "parameters": {
        "type": "object",
        "properties": {},
        "required": []
    },
}

list_repos = {
    "name": "list_repos",
    "description": "List all GitHub repositories for the authenticated user",
    "parameters": {
        "type": "object",
        "properties": {},
        "required": []
    },
}

tools = [
    {"type": "function", "function": github_events},
    {"type": "function", "function": list_repos},
]