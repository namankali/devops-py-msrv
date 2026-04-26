import requests
import os

from dotenv import load_dotenv


load_dotenv(override=True)

NODE_BACKEND = os.getenv("NODE_BACKEND")
URL = f"{NODE_BACKEND}/ai/v1/info"


def get_build_details_by_branch(token, branch="main", repo="all", repos=False):

    headers = {"x-access-token": token}

    params = {"branch": branch, "repo": repo, "repos": repos}

    try:
        res = requests.get(url=URL, headers=headers, params=params)

        print("Status Code: ", res.status_code)

        res.raise_for_status()

        data = res.json()
        print("Response: ", data)

        return {"success": True, "data": data.get("data", [])}
    except Exception as e:
        print(f"Error: {e}")

        return {"success": False, "error": str(e), "data": []}
