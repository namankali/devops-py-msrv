class Validator:

    @staticmethod
    def is_data_for_query(message: str) -> bool:
        message = message.lower()
        return any(
            k in message
            for k in ["list", "get", "logs", "failed", "failure", "success"]
        )

    @staticmethod
    def is_rag_call(message: str) -> bool:
        message = message.lower()
        return any(
            k in message for k in ["older", "previous", "previous logs", "older logs"]
        )
    