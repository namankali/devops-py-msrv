from .tools import (
    student_without_degree,
    issue_degree_to_single_student,
    revoke_degree_call,
)
import json
from .tool_schema import IssueDegreeInput, revokeDegreeInput

ALLOWED_TOOLS = {
    "unissued_degree_function",
    "issue_degree_single_function",
    "revoke_degree",
}


def handle_tool_call(message, token):
    tool_call = message.tool_calls[0]
    tool_name = tool_call.function.name

    if tool_name not in ALLOWED_TOOLS:
        return {
            "role": "tool",
            "name": tool_name,
            "content": json.dumps({"error": f"Unknown tool: {tool_name}"}),
        }
    else:
        tool_arguments = tool_call.function.arguments

        if not isinstance(tool_arguments, dict):
            try:
                tool_arguments = json.loads(tool_arguments)
            except Exception as e:
                return {
                    "role": "tool",
                    "name": tool_name,
                    "content": json.dumps(
                        {"error": "invalid tool arguments", "details": str(e)}
                    ),
                }

        if tool_name == "unissued_degree_function":
            print("unissued degree function has started")

            result = student_without_degree(token=token)

            if not result or not result.get("success"):
                return {
                    "role": "tool",
                    "name": tool_name,
                    "content": json.dumps(
                        {
                            "error": "Failed to load student details",
                            "details": result.get("error") if result else "No response",
                        }
                    ),
                }

            try:
                students = [
                    {
                        "student_id": s["id"],
                        "name": s["name"],
                        "email": s["email"],
                        "wallet": s["wallet_address"],
                    }
                    for s in result.get("data", [])
                ]

                return {
                    "role": "tool",
                    "name": tool_name,
                    "content": json.dumps({"students_without_degree": students}),
                }

            except Exception as e:
                return {
                    "role": "tool",
                    "name": tool_name,
                    "content": json.dumps(
                        {"error": "Data processing failed", "details": str(e)}
                    ),
                }

        elif tool_name == "issue_degree_single_function":
            print("issue degree tool started...")

            try:
                validated = IssueDegreeInput(**tool_arguments)
            except Exception as e:
                return {
                    "role": "tool",
                    "name": tool_name,
                    "content": json.dumps(
                        {
                            "error": "Validation failed for issuing degree",
                            "details": str(e),
                        }
                    ),
                }

            student_id = validated.student_id
            student_email = validated.student_email

            students_data = None  # cache

            # FETCH STUDENTS ONLY IF NEEDED
            if student_email or not student_id:
                students_response = student_without_degree(token=token)

                if not students_response or not students_response.get("success"):
                    return {
                        "role": "tool",
                        "name": tool_name,
                        "content": json.dumps(
                            {
                                "error": "Failed to fetch student list",
                                "details": (
                                    students_response.get("error")
                                    if students_response
                                    else "No response"
                                ),
                            }
                        ),
                    }

                students_data = students_response.get("data", [])

            if student_email and not student_id:
                for s in students_data:
                    if s["email"].lower() == student_email:
                        student_id = s["id"]
                        break

            #  VALIDATE student_id
            if not student_id:
                return {
                    "role": "tool",
                    "name": tool_name,
                    "content": json.dumps(
                        {
                            "error": "Unable to resolve student_id",
                            "details": {"student_email": student_email},
                            "suggestion": "Please provide a valid student email or ID",
                        }
                    ),
                }

            #  GD
            if students_data is not None:
                eligible_ids = [s["id"] for s in students_data]

                if student_id not in eligible_ids:
                    return {
                        "role": "tool",
                        "name": tool_name,
                        "content": json.dumps(
                            {
                                "error": "Student is not eligible for degree issuance",
                                "details": {"student_id": student_id},
                                "suggestion": "The student may already have a degree. Consider revoking if needed.",
                            }
                        ),
                    }

            try:
                result = issue_degree_to_single_student(
                    token=token, student_id=student_id
                )
            except Exception as e:
                return {
                    "role": "tool",
                    "name": tool_name,
                    "content": json.dumps(
                        {
                            "error": "Tool execution failed",
                            "details": str(e),
                        }
                    ),
                }

            if not result or not result.get("success"):
                return {
                    "role": "tool",
                    "name": tool_name,
                    "content": json.dumps(
                        {
                            "error": "Failed to issue degree",
                            "details": result.get("error") if result else "No response",
                        }
                    ),
                }

            return {
                "role": "tool",
                "name": tool_name,
                "content": json.dumps(
                    {
                        "success": True,
                        "message": "Degree issued successfully",
                        "student_id": student_id,
                    }
                ),
            }

        elif tool_name == "revoke_degree":
            print("revoke degree tool has tarted")

            try:
                validated = revokeDegreeInput(**tool_arguments)
            except Exception as e:
                return {
                    "role": "tool",
                    "name": tool_name,
                    "content": json.dumps(
                        {
                            "error": "validation failed for revoke degree",
                            "details": str(e),
                        }
                    ),
                }

            student_email = validated.student_email

            node_response = revoke_degree_call(token=token, email=student_email)

            if not node_response or not node_response.get("success"):
                return {
                    "role": "tool",
                    "name": tool_name,
                    "content": json.dumps(
                        {
                            "error": "Failed to revoke student degree",
                            "details": (
                                node_response.get("error")
                                if node_response
                                else "No resposne"
                            ),
                        }
                    ),
                }

            return {
                "role": "tool",
                "name": tool_name,
                "content": json.dumps(
                    {
                        "message": f"Degree related to {student_email} revoked successfully"
                    }
                ),
            }


# def handle_tool_call(message, token):

#     tool_call = message.tool_calls[0]

#     tool_name = tool_call.function.name
#     tool_call_id = tool_call.id

#     try:
#         tool_arguments = json.loads(tool_call.function.arguments or "{}")
#     except Exception:
#         tool_arguments = {}

#     if tool_name == "unissued_degree_function":

#         print("unissued degree function has started.............")

#         result = student_without_degree(token=token)
#         print("node result:", result)

#         students = [
#             {
#                 "student_id": s["id"],
#                 "name": s["name"],
#                 "email": s["email"],
#                 "wallet": s["wallet_address"]
#             }
#             for s in result["data"]
#         ]

#         return {
#             "role": "tool",
#             "tool_call_id": tool_call_id,
#             "name": tool_name,
#             "content": json.dumps({
#                 "students_without_degrees": students
#             })
#         }

#     elif tool_name == "issue_degree_single_function":

#         print(f"issue degree tool started.........:: {tool_arguments}")

#         student_id = tool_arguments.get("student_id")
#         student_name = tool_arguments.get("student_name")

#         if student_name:
#             print("searching student by name....")

#             result = student_without_degree(token=token)
#             students = result["data"]

#             for s in students:
#                 if s["name"].lower() == student_name.lower():
#                     student_id = s["id"]
#                     break

#         if not student_id:
#             return {
#                 "role": "tool",
#                 "tool_call_id": tool_call_id,
#                 "name": tool_name,
#                 "content": f"Student '{student_name}' not found among unissued degrees."
#             }

#         result = issue_degree_to_single_student(
#             token=token,
#             student_id=student_id
#         )

#         print("node js result:", result)

#         return {
#             "role": "tool",
#             "tool_call_id": tool_call_id,
#             "name": tool_name,
#             "content": json.dumps({
#                 "message": f"Degree issued successfully",
#                 "student_id": student_id
#             })
#         }

# return {
#     "role": "tool",
#     "name": tool_name,
#     "content": json.dumps(students)
# }
