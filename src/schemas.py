import re

from pydantic import BaseModel, Field, field_validator

SAFE_NAME_RE = re.compile(r"^[A-Za-zА-Яа-яЁё0-9 _.-]+$")


class RegisterRequest(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    password: str = Field(min_length=4, max_length=72)

    @field_validator("username")
    @classmethod
    def validate_username(cls, v: str):
        v = v.strip()
        if not SAFE_NAME_RE.fullmatch(v):
            raise ValueError("Username contains invalid characters")
        return v


class LoginRequest(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    password: str = Field(min_length=4, max_length=72)

    @field_validator("username")
    @classmethod
    def validate_username(cls, v: str):
        v = v.strip()
        if not SAFE_NAME_RE.fullmatch(v):
            raise ValueError("Username contains invalid characters")
        return v


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class CreateRoomRequest(BaseModel):
    name: str = Field(min_length=3, max_length=100)
    password: str = Field(min_length=3, max_length=72)

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str):
        v = v.strip()

        if len(v) < 3:
            raise ValueError("Room name must be at least 3 characters")

        if any(ch in "\n\r\t" for ch in v):
            raise ValueError("Room name cannot contain newlines or tabs")

        return v


class JoinRoomRequest(BaseModel):
    room: str = Field(min_length=3, max_length=100)
    password: str = ""

    @field_validator("room")
    @classmethod
    def validate_room(cls, v: str):
        v = v.strip()
        if not v:
            raise ValueError("Room name cannot be empty")
        if not SAFE_NAME_RE.fullmatch(v):
            raise ValueError("Room name contains invalid characters")
        return v


class SendMessageRequest(BaseModel):
    text: str = Field(min_length=1, max_length=1000)


class EditMessageRequest(BaseModel):
    text: str = Field(min_length=1, max_length=1000)
