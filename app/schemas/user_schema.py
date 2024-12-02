from pydantic import BaseModel

class UserRegisterRequest(BaseModel):
    email: str
    password: str
    email: str

class UserUpdateRequest(BaseModel):
    username: str
    email: str

class PasswordResetRequest(BaseModel):
    new_password: str