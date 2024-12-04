import os
from app.core.permissions import get_super_admin_user, get_current_user, oauth2_scheme
from app.schemas.user_schema import UserRegisterRequest, ProfileUpdateRequest, \
    ChangePasswordRequest, ProfileResponse
from app.core.auth import register_user, login_user
from app.schemas.user_schema import UserLoginRequest
from app.core.user_service import login_user, get_all_users
from app.utils.jwt_utils import create_access_token, create_refresh_token
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.database import get_db
from passlib.hash import bcrypt
from app.models.user import User, Profile, TokenBlacklist
import jwt

router = APIRouter()





"""
    Register a new user.

    Args:
        request (UserRegisterRequest): The request payload containing user details.
        db (Session): Database session dependency.
        current_user (dict): The current authenticated super admin.

    Returns:
        dict: A response containing the newly registered user's details.

    Raises:
        HTTPException: If user registration fails due to invalid data.
"""
@router.post("/register")
def register(
    request: UserRegisterRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_super_admin_user)  # Add this dependency
):
    try:
        user = register_user(db, request)
        return {
            "message": "User registered successfully",
            "user": {
                "email": user.email,
                "role": user.role
            }
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))





"""
    Authenticate a user and provide access and refresh tokens.

    Args:
        login_request (UserLoginRequest): The login credentials provided by the user.
        db (Session): Database session dependency.

    Returns:
        dict: A response containing the authentication tokens and token type.

    Raises:
        HTTPException: If authentication fails due to invalid credentials.
"""
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





"""
    Generate a new access token using a valid refresh token.

    Args:
        refresh_token (str): The refresh token provided by the client.
        db (Session): Database session dependency.

    Returns:
        dict: A response containing the new access token and its type.

    Raises:
        HTTPException: If the refresh token is invalid, expired, or the user does not exist.
"""
@router.post("/refresh_token")
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





"""
    Retrieve a list of all registered users.

    Args:
        db (Session): Database session dependency.
        current_user (dict): Current authenticated super admin.

    Returns:
        dict: A response containing a list of all users.

    Raises:
        HTTPException: If the current user is not a super admin.
"""
@router.get("/all_users")
def get_users(db: Session = Depends(get_db), current_user: dict = Depends(get_super_admin_user)):
    # Get all users from the database
    users = get_all_users(db)
    return {"users": users}





"""
    Retrieve the current user's profile information. 
    If a profile does not exist, create a default one.

    Args:
        user (User): The currently authenticated user.
        db (Session): Database session dependency.

    Returns:
        dict: A dictionary containing user and profile information.

    Raises:
        HTTPException: If the user is not authenticated.
"""
@router.get("/me")
def get_me(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    # Fetch the user's profile using the user_id
    profile = db.query(Profile).filter(Profile.user_id == user.id).first()

    if not profile:
        # Create a profile if it doesn't exist
        profile = Profile(
            user_id=user.id,
            first_name="",
            last_name="",
            address="",
            city="",
            state="",
            zip_code="",
            country=""
        )
        db.add(profile)
        db.commit()
        db.refresh(profile)

    # Return user and profile data without password
    return {
        "email": user.email,
        "is_active": user.is_active,
        "role": user.role,
        "phone": user.phone,
        "first_name": profile.first_name or "",
        "last_name": profile.last_name or "",
        "address": profile.address or "",
        "city": profile.city or "",
        "state": profile.state or "",
        "zip_code": profile.zip_code or "",
        "country": profile.country or ""
    }





"""
    Update or create the current user's profile information.

    Args:
        profile_data (ProfileUpdateRequest): The profile update payload.
        db (Session): Database session dependency.
        current_user (User): The currently authenticated user.

    Returns:
        ProfileResponse: The updated profile information.
        
    Raises:
        HTTPException: If the user is not authenticated.
"""
@router.patch("/update_profile", response_model=ProfileResponse)
async def update_user_profile(
        profile_data: ProfileUpdateRequest,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    profile = db.query(Profile).filter(Profile.user_id == current_user.id).first()
    if not profile:
        # Create a new profile if it doesn't exist
        profile = Profile(user_id=current_user.id, **profile_data.model_dump())
        db.add(profile)
    else:
        # Update the existing profile
        for key, value in profile_data.model_dump().items():
            setattr(profile, key, value)

    db.commit()
    db.refresh(profile)

    return ProfileResponse(
        first_name=profile.first_name,
        last_name=profile.last_name,
        email=current_user.email,
        phone=current_user.phone,
        address=profile.address,
        city=profile.city,
        state=profile.state,
        zip_code=profile.zip_code,
        country=profile.country,
    )





"""
    Change the current user's password.

    Args:
        request (ChangePasswordRequest): The password change payload containing old, new, and confirm passwords.
        db (Session): Database session dependency.
        current_user (User): The currently authenticated user.
        token (str): The JWT token used for authentication.

    Returns:
        dict: A message indicating the password change was successful.

    Raises:
        HTTPException: If the old password is incorrect, the new password and confirmation do not match, or the user does not exist.
"""
@router.post("/change_password")
async def change_password(
    request: ChangePasswordRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    token: str = Depends(oauth2_scheme)  # The current JWT token
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

    # Add the current token to the blacklist
    db.add(TokenBlacklist(token=token))
    db.commit()

    return {"message": "Password changed successfully. Please log in again to continue."}
