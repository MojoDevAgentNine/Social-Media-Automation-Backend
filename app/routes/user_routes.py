from fastapi import APIRouter, Depends
from typing import List
from pydantic import BaseModel
from ..core.permissions import get_current_user, get_admin_user  # Dependency for authentication/authorization
from app.schemas.user_schema import UserRegisterRequest, PasswordResetRequest, UserUpdateRequest

router = APIRouter()

# Route to register a new user (only admin can access this)
@router.post("/register")
async def register_user(user: UserRegisterRequest, current_user: UserRegisterRequest = Depends(get_admin_user)):
    # Logic to register the user
    # Only admin is allowed to create a new user
    return {"message": "User registered successfully by admin"}

# Route to log in a user
@router.post("/login")
async def login_user(user: UserRegisterRequest):
    # Your user login logic here (return token)
    return {"message": "User logged in successfully"}

# Route to generate token
@router.post("/token")
async def generate_token(user: UserRegisterRequest):
    # Logic to generate a JWT token for the user
    return {"token": "generated_jwt_token"}

# Route to get current user's profile information
@router.get("/me")
async def get_current_user_profile(current_user: UserRegisterRequest = Depends(get_current_user)):
    # Logic to return the current user's profile info
    return {"message": "Current user profile", "user": current_user}

# Route to initiate 2FA for a user
@router.post("/2fa/initiate")
async def initiate_2fa(current_user: UserRegisterRequest = Depends(get_current_user)):
    # Logic to initiate 2FA (send 2FA code, etc.)
    return {"message": "2FA initiation successful"}

# Route to verify 2FA for a user
@router.post("/2fa/verify")
async def verify_2fa(current_user: UserRegisterRequest = Depends(get_current_user), code: str = Depends()):
    # Logic to verify the 2FA code
    return {"message": "2FA verification successful"}

# Route to reset password
@router.post("/reset-password")
async def reset_password(password_request: PasswordResetRequest, current_user: UserRegisterRequest = Depends(get_current_user)):
    # Logic to reset the current user's password
    return {"message": "Password reset successful"}

# Admin-only routes

# Route to add a user (admin only)
@router.post("/admin/add")
async def add_user(user: UserRegisterRequest, current_user: UserRegisterRequest = Depends(get_admin_user)):
    # Only admin can add a user
    return {"message": "User added successfully"}

# Route to update a user's information
@router.put("/update")
async def update_user(user_update: UserUpdateRequest, current_user: UserRegisterRequest = Depends(get_current_user)):
    # Logic to update the current user's information
    return {"message": "User information updated successfully"}

# Route to delete a user (admin only)
@router.delete("/admin/delete")
async def delete_user(user_id: int, current_user: UserRegisterRequest = Depends(get_admin_user)):
    # Only admin can delete a user
    return {"message": f"User with ID {user_id} deleted successfully"}
