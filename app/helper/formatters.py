from rich.console import Console
from collections import Counter
from datetime import datetime

console = Console()


def format_repos(data):
    console.print("bull's eye ->>>> ", data)
    if not data:
        return "There are no repositories stored in our DB."

    lines = ["here are your registered repositories:\n"]

    for i, repo in enumerate(data, 1):
        visibility = "Private" if repo.get("is_private") else "Public"
        lines.append(
            f"{i}. {repo.get('repo_name')} ({visibility}) - Branch: {repo.get('default_branch')} - Github Repo ID: {repo.get('github_repo_id')}"
        )

    return "\n".join(lines)


def format_workflows(data, has_date_filter, include_count):

    if not data:
        return "No workflow data available."

    if include_count:
        repo_details = []

        for repo in data:
            repo_name = repo.get("repo_name", "Unknown")
            builds = repo.get("builds", [])

            build_count = int(repo.get("count", len(builds)))

            branches = {build.get("branch") for build in builds if build.get("branch")}

            branch_text = (
                f" on the {', '.join(sorted(branches))} branch" if branches else ""
            )

            # Count builds by date
            date_counts = Counter()

            for build in builds:
                created_at = build.get("created_at")

                if created_at:
                    try:
                        build_date = datetime.fromisoformat(
                            created_at.replace("Z", "+00:00")
                        ).date()

                        date_counts[build_date] += 1

                    except ValueError:
                        continue

            date_details = []

            for build_date, date_count in sorted(date_counts.items(), reverse=True):
                formatted_date = build_date.strftime("%B %-d, %Y")

                date_details.append(
                    f"   - {formatted_date}: "
                    f"{date_count} failed build"
                    f"{'s' if date_count != 1 else ''}"
                )

            repo_detail = (
                f"- `{repo_name}`: "
                f"{build_count} failed build"
                f"{'s' if build_count != 1 else ''}"
                f"{branch_text}."
            )

            if date_details:
                repo_detail += "\n" + "\n".join(date_details)

            repo_details.append(repo_detail)

        total_builds = sum(
            int(repo.get("count", len(repo.get("builds", [])))) for repo in data
        )

        repo_count = len(repo_details)

        return (
            f"There {'was' if total_builds == 1 else 'were'} "
            f"{total_builds} failed build"
            f"{'s' if total_builds != 1 else ''} "
            f"across {repo_count} "
            f"repositor{'y' if repo_count == 1 else 'ies'}:\n\n"
            + "\n".join(repo_details)
        )

    elif has_date_filter:
        builds = []

        for repo in data:
            builds.extend(repo.get("builds", []))

        failed_count = len(builds)

        lines = [
            f"Found {failed_count} failed build"
            f"{'s' if failed_count != 1 else ''}:\n"
        ]

        for i, wf in enumerate(builds, 1):
            lines.append(
                f"{i}. Workflow: {wf.get('workflow_run_name', 'Unknown')}\n"
                f"   Build Number: {wf.get('run_number', 'Unknown')}\n"
                f"   Run ID: {wf.get('run_id', 'Unknown')}\n"
                f"   Commit: {wf.get('commit_sha', 'Unknown')}\n"
                f"   URL: {wf.get('html_url', 'N/A')}"
            )

        return "\n\n".join(lines)

    else:
        lines = ["Workflows:\n"]

        for repo in data:
            for i, wf in enumerate(repo.get("builds", []), 1):
                lines.append(
                    f"{i}. "
                    f"{wf.get('workflow_run_name', 'Unknown')} - "
                    f"Status: {wf.get('status', 'Unknown')}"
                )

        return "\n".join(lines)


def format_single_repo_response(data):
    if not data:
        return "No single repo data available"

    lines = [""]


def format_unregistered_repos(data):
    console.print("unregistered ->>>> ", data)
    if not data:
        return "All available GitHub repositories are already registered."

    lines = ["Here are your unregistered GitHub repositories:\n"]

    for i, repo in enumerate(data, 1):
        visibility = repo.get("visibility", "unknown").capitalize()
        language = repo.get("language") or "Not specified"
        repo_id = repo.get("github_repo_id") or "N/A"

        repo_type = repo.get("type", "Unknown")
        if repo_type == "User":
            repo_type = "Personal"
        elif repo_type == "Organization":
            repo_type = "Organization"

        lines.append(
            f"{i}. {repo.get('repo_name')} "
            f"Visibility: {visibility}, RepoType: {repo_type}"
            f"Language: {language}"
            f" and the repository ID is {repo_id}"
        )

    return "\n".join(lines)


def format_save_repo(data):
    saved = data.get("saved", [])
    failed = data.get("failed", [])

    lines = []

    if saved:
        lines.append("Saved repositories to DB:")
        for repo in saved:
            lines.append(f"- {repo}")

    if failed:
        lines.append("\nFailed to save:")
        for item in failed:
            lines.append(f"- {item.get('name')} — {item.get('error')}")

    return "\n".join(lines) or "No repositories were saved."


def get_repo_name(repo_name):
    if repo_name == "devops-frontend":
        return "namankali/devops-frontend"
    elif repo_name == "devops-backend":
        return "namankali/devops-backend"
    else:
        return repo_name


FORMATTERS = {
    "list_repos": format_repos,
    "github_events": format_workflows,
    "fetch_unregistered_repos": format_unregistered_repos,
    "save_repo_to_db": format_save_repo,
    "get_repo_fullname": get_repo_name,
}
