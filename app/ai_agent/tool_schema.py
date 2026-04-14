from pydantic import BaseModel, ConfigDict, field_validator, model_validator, EmailStr


class BaseToolInput(BaseModel):
    model_config = ConfigDict(
        extra="forbid", str_strip_whitespace=True, validate_assignment=True
    )

    @classmethod
    def validate_inputs(cls, data: dict):
        try:
            return cls(**data)
        except Exception as e:
            raise ValueError(f"{cls.__name__} validation failed {e}")

    @field_validator("*")
    @classmethod
    def no_empty_str(cls, v):
        if isinstance(v, str) and not v.strip():
            raise ValueError("Empty str is not allowed")
        return v


class IssueDegreeInput(BaseToolInput):
    student_id: str | None = None
    student_email: str | None = None

    @field_validator("student_id")
    @classmethod
    def validate_student_id(cls, v):
        if v and not v.isdigit():
            raise ValueError("student id must be number")
        return v

    @field_validator("student_email")
    @classmethod
    def normalize_email(cls, v):
        return v.lower() if v else v

    @model_validator(mode="after")
    def check_required(self):
        if not self.student_id and not self.student_email:
            raise ValueError("Either student id or student email must me provided")
        return self


class revokeDegreeInput(BaseToolInput):
    student_email: EmailStr

    @field_validator("student_email")
    @classmethod
    def normalize_email(cls, v):
        return v.lower()


unissued_degree_function = {
    "name": "unissued_degree_function",
    "description": "Get students who do not have issued degrees",
    "parameters": {"type": "object", "properties": {}},
}

issue_degree_single_function = {
    "name": "issue_degree_single_function",
    "description": "Issue a blockchain degree NFT to a single student using their student_id",
    "parameters": {
        "type": "object",
        "properties": {
            "student_id": {
                "type": "string",
                "description": "The unique identifier of the student whose degree should be issued",
            },
            "student_email": {"type": "string", "description": "Email of student"},
        },
        "required": [],
    },
}

revoke_degree = {
    "name": "revoke_degree",
    "description": "Revoke a bloackchain degree related to single student by email id",
    "parameters": {
        "type": "object",
        "properties": {
            "student_email": {
                "type": "string",
                "description": "Unique identifier of the styudent whose degree should be revoked",
            }
        },
        "required": ["student_email"],
    },
}

tools = [
    {"type": "function", "function": unissued_degree_function},
    {"type": "function", "function": issue_degree_single_function},
    {"type": "function", "function": revoke_degree},
]
