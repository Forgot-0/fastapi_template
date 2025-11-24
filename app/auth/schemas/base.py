import re

from pydantic import BaseModel, Field, field_validator


class PasswordMixinSchema(BaseModel):
    password: str = Field(
        ...,
        min_length=8,
        max_length=128,
        description="Password must be at least 8 characters long.",
        kw_only=True
    )
    password_repeat: str = Field(..., kw_only=True)

    @field_validator("password")
    @classmethod
    def validate_password(cls, value: str) -> str:
        """
        Validate the password complexity.

        The password must contain at least one uppercase letter,
        at least one lowercase letter, at least one digit, and
        at least one special character.
        """
        if not re.search(r"[A-Z]", value):
            raise ValueError("Password must contain at least one uppercase letter")
        if not re.search(r"[a-z]", value):
            raise ValueError("Password must contain at least one lowercase letter")
        if not re.search(r"[0-9]", value):
            raise ValueError("Password must contain at least one digit")
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', value):
            raise ValueError("Password must contain at least one special character")
        return value
