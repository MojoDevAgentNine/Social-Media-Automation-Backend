from pydantic import BaseModel, EmailStr, Field

class UserRegisterRequest(BaseModel):
    username: str
    password: str
    email: EmailStr

class UserUpdateRequest(BaseModel):
    username: str
    email: EmailStr

class PasswordResetRequest(BaseModel):
    new_password: str

class UserLoginRequest(BaseModel):
    username_or_email: str  # Can be either username or email
    password: str  # Password is required

class UpdateUserProfile(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    phone: str | None = None
    address: str | None = None
    city: str | None = None
    state: str | None = None
    zip_code: str | None = None
    country: str | None = None


class ChangePasswordRequest(BaseModel):
    old_password: str = Field(..., min_length=6)
    new_password: str = Field(..., min_length=6)
    confirm_password: str = Field(..., min_length=6)

