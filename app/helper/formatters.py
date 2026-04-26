def format_repos(data):
    if not data:
        return "There are no repositories stored in our DB."

    lines = ["Repositories:\n"]

    for i, repo in enumerate(data, 1):
        visibility = "Private" if repo.get("is_private") else "Public"
        lines.append(
            f"{i}. {repo.get('repo_name')} ({visibility}) - Branch: {repo.get('default_branch')}"
        )

    return "\n".join(lines)


# Future-ready (example)
def format_workflows(data):
    if not data:
        return "No workflow data available."

    lines = ["Workflows:\n"]

    for i, wf in enumerate(data, 1):
        lines.append(f"{i}. {wf.get('job_name')} - Status: {wf.get('status')}")

    return "\n".join(lines)



FORMATTERS = {
    "list_repos": format_repos,
    "github_events": format_workflows,
}
