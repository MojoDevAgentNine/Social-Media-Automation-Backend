from fastapi import HTTPException
from app.models import User
from app.core.auth import verify_token
from fastapi import Depends

# Function to check if the user has an admin role
def get_admin_user(token: str = Depends(verify_token)):
    user = User.get_by_token(token)  # Retrieve user from the token
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    if user.role != "admin":  # Admin role check
        raise HTTPException(status_code=403, detail="Admin privileges required")
    return user

# Function to check if the current user is the same as the one in the request
def check_user_ownership(user_id: int, token: str = Depends(verify_token)):
    user = User.get_by_token(token)  # Retrieve user from the token
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    if user.id != user_id:  # Check if the current user matches the user_id in the request
        raise HTTPException(status_code=403, detail="You do not have permission to access this resource")
    return user

# Function to check if the user has a specific role
def has_role(required_role: str, token: str = Depends(verify_token)):
    user = User.get_by_token(token)  # Retrieve user from the token
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    if user.role != required_role:  # Check if user has the required role
        raise HTTPException(status_code=403, detail=f"{required_role} privileges required")
    return user

# Example: Check if the current user has 'user' role
def check_user_role(token: str = Depends(verify_token)):
    user = User.get_by_token(token)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    if user.role != "user":
        raise HTTPException(status_code=403, detail="User role is required")
    return user


def get_current_user():
    return None