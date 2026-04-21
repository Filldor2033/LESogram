from pydantic import BaseModel, Field, field_validator

class RegisterRequest(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    password: str = Field(min_length=4, max_length=72)

class LoginRequest(BaseModel):
    username: str
    password: str = Field(min_length=4, max_length=72)

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

class CreateRoomRequest(BaseModel):
    name: str = Field(min_length=3, max_length=100)
    password: str = Field(min_length=1, max_length=72)

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str):
        v = v.strip()
        if not v:
            raise ValueError("Room name cannot be empty")
        return v

class JoinRoomRequest(BaseModel):
    room: str = Field(min_length=3, max_length=100)
    password: str = Field(min_length=1, max_length=72)

class SendMessageRequest(BaseModel):
    text: str = Field(min_length=1, max_length=1000)