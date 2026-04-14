import requests
import os
from dotenv import load_dotenv

load_dotenv(override=True)

NODE_BACKEND = os.getenv("NODE_BACKEND")


def student_without_degree(token):
    url = f"{NODE_BACKEND}/students/v1/all"

    headers = {"x-access-token": token}

    params = {"unissued": "true"}

    try:
        res = requests.get(url=url, headers=headers, params=params)

        print("Status Code:", res.status_code)

        res.raise_for_status()  # raises HTTPError for bad responses

        data = res.json()
        print("Response:", data)

        return {"success": True, "data": data.get("data", [])}

    except Exception as e:
        print(f"Error: {e}")

        return {"success": False, "error": str(e), "data": []}


def issue_degree_to_single_student(token, student_id):
    url = f"{NODE_BACKEND}/cr/v1/issue"

    headers = {"x-access-token": token, "Content-Type": "application/json"}

    body = {"student_id": student_id}

    try:
        print("\n Issuing degree...")
        print("URL:", url)
        print("Body:", body)

        res = requests.post(url=url, headers=headers, json=body)

        print("Status Code:", res.status_code)

        res.raise_for_status()

        data = res.json()
        print("Degree Issued:", data)

        return {"success": True, "data": data}

    except Exception as e:
        print(f"issue degree error: ", e)

        return {"success": False, "error": str(e)}


def revoke_degree_call(token, email):
    url = f"{NODE_BACKEND}/cr/v1/revoke/email/{email}"

    headers = {"x-access-token": token, "Content-Type": "application/json"}

    try:
        print(f"Degree revokation for student: {email} has started.....")
        
        res = requests.patch(url=url, headers=headers)
        print(f"API response: {res}")
        res.raise_for_status()
        
        data = res.json()
        print("Degree revoked: ", data)
        
        return {
            "success": True,
            "data": data
        }
        
    except Exception as e:
        print(f"revoke degree error: ", e)

        return {"success": False, "error": str(e)}
