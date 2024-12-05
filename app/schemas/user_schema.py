from pydantic import BaseModel, EmailStr, Field
from app.models.user import UserRole
from typing import Optional


class UserRegisterRequest(BaseModel):
    email: EmailStr
    phone: str
    password: str
    role: UserRole = UserRole.USER  # Default role is normal user

    class Config:
        use_enum_values = True


class UserUpdateRequest(BaseModel):
    email: EmailStr


class PasswordResetRequest(BaseModel):
    new_password: str


class UserLoginRequest(BaseModel):
    email: str  # Can be either username or email
    password: str  # Password is required


class ChangePasswordRequest(BaseModel):
    old_password: str = Field(..., min_length=6)
    new_password: str = Field(..., min_length=6)
    confirm_password: str = Field(..., min_length=6)


class ProfileUpdateRequest(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None
    country: Optional[str] = None


class ProfileResponse(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    phone: str
    address: str
    city: str
    state: str
    zip_code: str
    country: str

    class Config:
        from_attributes = True

class VerificationCodeRequest(BaseModel):
    email: EmailStr
    code: str

class LoginResponsePending(BaseModel):
    message: str
    email: str
    requires_verification: bool = True

class LoginResponseComplete(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str