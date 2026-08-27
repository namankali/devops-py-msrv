from rich.console import Console
from app.rag.index import get_failure_by_run_id

console = Console()


class GeneralHelpers:

    def __init__(self, failure_data):
        self.failure_data: str = failure_data

    @staticmethod
    def get_run_ids(runs):
        return [int(run["run_id"]) for run in runs]

    def get_failed_run_reason(self):
        print("initailize build failure integration")

        run_ids = self.get_run_ids(self.failure_data)

        vector_result = get_failure_by_run_id(run_id=run_ids)
        console.print("vector_result", vector_result, style="purple")
        
        for obj in vector_result:
            console.print("obj ->>>>>>>>> ", obj, style="pink")
