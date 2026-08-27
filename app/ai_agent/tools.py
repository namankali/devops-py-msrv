import requests
import os
from dotenv import load_dotenv

load_dotenv(override=True)

NODE_BACKEND = os.getenv("NODE_BACKEND")
URL = f"{NODE_BACKEND}/"


def get_build_details_by_branch(
    token,
    branch="main",
    repo="all",
    repos=False,
    repo_name="",
    start_date="",
    end_date="",
    count=False,
    build="total",
):
    headers = {"x-access-token": token}

    params = {
        "branch_name": branch,
        "repo": repo,
        "repos": repos,
        "count": count,
        "build": build,
    }

    if end_date != "":
        params["start_date"] = start_date
        params["end_date"] = end_date
    else:
        params["start_date"] = start_date
        params["end_date"] = start_date

    try:
        url = f"{NODE_BACKEND}/ai/v1/info"
        if repo and repo == "single" and repo_name:
            params["repo_name"] = repo_name
            res = requests.get(url=url, headers=headers, params=params)

            res.raise_for_status()
            data = res.json()

            return {"success": True, "data": data.get("data", [])}
        else:
            res = requests.get(url=url, headers=headers, params=params)

            res.raise_for_status()

            data = res.json()
            # print("Response: ", data)

            return {"success": True, "data": data.get("data", [])}

    except Exception as e:
        print(f"Error: {e}")

        return {"success": False, "error": str(e), "data": []}


def get_repo_details(token, registered_status: str = "", visibility: str = ""):
    headers = {"x-access-token": token}

    params = {}
    if registered_status:
        params["registered_status"] = registered_status

    if visibility:
        params["visibility"] = visibility

    try:
        url = f"{NODE_BACKEND}/actions/v1/urr/repo"

        res = requests.get(url=url, headers=headers, params=params)

        res.raise_for_status()

        data = res.json()
        print("data************", data)
        return {"success": True, "data": data.get("data", data.get("data", []))}
    except Exception as e:
        print(f"Error: {e}")

        return {"success": False, "error": str(e), "data": []}


# def get_unregistered_repos(token):
#     headers = {"x-access-token": token}

#     try:
#         url = f"{NODE_BACKEND}/actions/v1/urr/repo"

#         res = requests.get(url=url, headers=headers)

#         res.raise_for_status()

#         data = res.json()

#         print("json data", data)

#         return {"success": True, "data": data.get("data", [])}
#     except Exception as e:
#         print(f"Error: {e}")

#         return {"success": False, "error": str(e), "data": []}


def save_repo_to_db(token: str, repo_ids: list[str]):
    headers = {"x-access-token": token}
    params = {"repo_ids": repo_ids}
    try:
        url = f"{NODE_BACKEND}/actions/v1/ind/repo/true"

        res = requests.post(url=url, headers=headers, params=params)

        res.raise_for_status()

        data = res.json()
        return {"success": True, "data": data.get("data", [])}
    except Exception as e:
        print(f"Error: {e}")

        return {"success": False, "error": str(e), "data": []}
