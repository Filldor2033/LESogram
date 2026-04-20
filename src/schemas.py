from pydantic import BaseModel, Field, field_validator
from datetime import datetime

class RegisterRequest(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    password: str = Field(min_length=4, max_length=128)

class LoginRequest(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

class MessageResponse(BaseModel):
    username: str
    text: str
    room: str
    timestamp: datetime

class WSMessage(BaseModel):
    type: str
    username: str | None = None
    text: str | None = None
    room: str | None = None
    timestamp: str | None = None

class RegisterRequest(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    password: str = Field(min_length=4, max_length=128)

    @field_validator("password")
    @classmethod
    def validate_password_bytes(cls, v: str):
        if len(v.encode("utf-8")) > 72:
            raise ValueError("Password is too long for bcrypt (max 72 UTF-8 bytes)")
        return v


class LoginRequest(BaseModel):
    username: str
    password: str

    @field_validator("password")
    @classmethod
    def validate_password_bytes(cls, v: str):
        if len(v.encode("utf-8")) > 72:
            raise ValueError("Password is too long for bcrypt (max 72 UTF-8 bytes)")
        return v