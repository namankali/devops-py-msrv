from enum import Enum


class Intent(str, Enum):
    ACTION = "action"
    REPOSITORY_QUERY = "repository_query"
    BUILD_QUERY = "build_query"
    RAG = "rag"
    GENERAL = "general"


# class GenerateIntent:
#     def __init__(self, message: str, history: list = None):
#         self.message = message.lower().strip
#         self.history = history if history is not None else []

#     def _isFollowUp(self, message, history):
#         follow_up_keywords = [
#             "them",
#             "their",
#             "those",
#             "these",
#             "it",
#             "its",
#             "that",
#             "this",
#             "ones",
#             "details",
#             "more",
#             "show me",
#         ]
#         if not any(k in message for k in follow_up_keywords):
#             return False

#         print("intent check for follow up message", history)

#         previous_context = " ".join(
#             h.get("content", "").lower() for h in history if h.get("content")
#         )

#         repository_keywords = [
#             "repository",
#             "repositories",
#             "repo",
#             "registered repos",
#             "github",
#         ]

#         return any(k in previous_context for k in repository_keywords)

#     def classify_intent(self):
#         actions_ = [
#             "create",
#             "add",
#             "update",
#             "delete",
#             "trigger",
#             "run",
#             "save",
#             "register",
#         ]

#         rag_ = [
#             "why did",
#             "why",
#             "root cause",
#             "failure reason",
#             "cause of",
#             "error",
#             "logs",
#             "probable fix",
#             "failed",
#         ]

#         repo_query_ = [
#             "repo",
#             "repos",
#             "repository",
#             "repositories",
#             "github repository",
#             "github repositories",
#         ]

#         build_query_ = [
#             "build",
#             "builds",
#             "workflow",
#             "workflows",
#             "pipeline",
#             "pipelines",
#         ]

#         if any(word in self.message for word in actions_):
#             return Intent.ACTION

#         if any(word in self.message for word in rag_):
#             return Intent.RAG

#         if any(word in self.message for word in repo_query_):
#             return Intent.REPOSITORY_QUERY

#         if any(word in self.message for word in build_query_):
#             return Intent.BUILD_QUERY

#         if self._isFollowUp(message=self.message, history=self.history):
#             return Intent.REPOSITORY_QUERY

#         return Intent.GENERAL

#     @staticmethod
#     def resolve_registered_status(text: str, state, history):
#         if "unregistered" in text:
#             return "unregistered"
#         if "not registered" in text:
#             return "unregistered"
#         if "registered" in text:
#             return "registered"

#         #  Follow up
#         if state.repository_scope:
#             return state.repository_scope

#         # Look at recent conversation
#         recent_text = " ".join(str(h.get("content", "")).lower() for h in history[-8:])

#         if "unregistered" in recent_text:
#             return "unregistered"

#         if "registered" in recent_text:
#             return "registered"

#         return "all"


def require_explanation(message):
    message = message.lower()
    intent = ["failed", "fail", "failed jobs"]


def classify_intent(message: str, history=None) -> str:
    message = message.lower().strip()

    if any(
        k in message
        for k in ["create", "add", "update", "delete", "trigger", "run", "save"]
    ):
        return "action"

    if any(
        k in message for k in ["why", "error", "failed", "failure", "logs", "reason"]
    ):
        return "rag"  # vector DB

    if any(
        k in message
        for k in [
            "how many",
            "count",
            "latest",
            "current",
            "status",
            "repos",
            "github repos",
            "github repositories",
        ]
    ):
        return "live_query"  # API

    print(
        "Bull's eye ->>>>>>>>>>>>>>>>>>>>> ",
        is_follow_up(message=message, history=history),
    )
    if history and is_follow_up(message=message, history=history):
        return "live_query"

    if any(k in message for k in ["what", "explain", "show"]):
        return "question"

    return "general"


def is_follow_up(message, history):
    follow_up_keywords = [
        "them",
        "their",
        "those",
        "these",
        "it",
        "its",
        "that",
        "this",
        "ones",
        "details",
        "more",
        "show me",
    ]
    if not any(k in message for k in follow_up_keywords):
        return False

    previous_context = " ".join(
        h.get("content", "").lower() for h in history if h.get("content")
    )
    print("previous context -************* ", previous_context)

    repository_keywords = [
        "repository",
        "repositories",
        "repo",
        "registered repos",
        "github",
    ]

    return any(k in previous_context for k in repository_keywords)
