import os
from app.schemas.user_schema import UserRegisterRequest, PasswordResetRequest, UserLoginRequest, UpdateUserProfile, \
    ChangePasswordRequest
from app.core.auth import register_user, login_user
from app.schemas.user_schema import UserLoginRequest
from app.core.user_service import login_user, get_all_users
from app.utils.jwt_utils import decode_token, create_access_token, create_refresh_token
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.database import get_db
from passlib.hash import bcrypt
from app.core.user_service import get_authenticated_user
from app.models.user import User
from fastapi.security import OAuth2PasswordBearer
import jwt

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
router = APIRouter()

@router.post("/register")
def register(request: UserRegisterRequest, db: Session = Depends(get_db)):
    try:
        user = register_user(db, request)
        return {"message": "User registered successfully", "user": user.username}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/login")
def login(login_request: UserLoginRequest, db: Session = Depends(get_db)):
    # Authenticate user
    user = login_user(db=db, login_request=login_request)

    if user:
        # Generate both access and refresh tokens for the authenticated user
        access_token = create_access_token(data={"user_id": user.id})
        refresh_token = create_refresh_token(data={"user_id": user.id})

        # Return the response with both tokens
        return {
            "message": "Login successful",
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer"
        }
    else:
        raise HTTPException(status_code=400, detail="Invalid username/email or password")

@router.post("/refresh")
def refresh_token(refresh_token: str, db: Session = Depends(get_db)):
    try:
        # Decode the refresh token
        payload = jwt.decode(refresh_token, os.getenv("SECRET_KEY"), algorithms=["HS256"])
        user_id = payload.get("user_id")

        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid refresh token")

        # You can check if the user exists in the database (optional)
        user = db.query(User).filter(User.id == user_id).first()
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")

        # Create a new access token
        new_access_token = create_access_token(data={"user_id": user.id})

        # Return the new access token
        return {"access_token": new_access_token, "token_type": "bearer"}

    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid refresh token")




def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    # Assume you have a function to decode the token and retrieve user info (e.g., user_id)
    user_id = decode_token(token)  # Implement this function according to your JWT setup
    user = get_authenticated_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
@router.get("/all_users")
def get_users(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    if not user.is_admin:
        raise HTTPException(status_code=403, detail="Only admins can view all users")

    # Get all users from the database
    users = get_all_users(db)

    return {"users": users}

@router.get("/me")
def get_me(user: User = Depends(get_current_user)):
    return {
        "username": user.username,
        "email": user.email,
        "is_active": user.is_active,
        "is_admin": user.is_admin
    }

@router.patch("/update_profile")
async def update_user_profile(
    user_profile: UpdateUserProfile,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),  # Assuming you have authentication
):
    user_data = user_profile.dict(exclude_unset=True)
    db.query(User).filter(User.id == current_user.id).update(user_data)
    db.commit()
    db.refresh(current_user)
    return current_user

@router.post("/change_password")
async def change_password(
    request: ChangePasswordRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)  # Assumes user is authenticated
):
    # Verify the old password
    if not bcrypt.verify(request.old_password, current_user.hashed_password):
        raise HTTPException(status_code=400, detail="Old password is incorrect")

    # Check if new password and confirm password match
    if request.new_password != request.confirm_password:
        raise HTTPException(status_code=400, detail="New password and confirmation do not match")

    # Hash the new password and update the database
    hashed_password = bcrypt.hash(request.new_password)
    current_user.hashed_password = hashed_password
    db.commit()
    db.refresh(current_user)

    return {"message": "Password changed successfully"}