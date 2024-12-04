import os
import jwt
from passlib.hash import bcrypt
from sqlalchemy.orm import Session
from app.models.user import User, UserRole, Profile
from app.schemas.user_schema import UserRegisterRequest
from datetime import datetime
from fastapi import HTTPException



"""
    Registers a new user and creates an initial profile.

    Args:
        db (Session): Database session dependency.
        user (UserRegisterRequest): The user registration request containing email, password, phone, and role.
        current_user (User, optional): The currently authenticated user, if applicable.

    Returns:
        User: The newly created user instance.

    Raises:
        ValueError: If the email is already in use.
        HTTPException: If the current user lacks permission to assign specific roles.
"""
def register_user(db: Session, user: UserRegisterRequest, current_user: User = None):
    # Check if the user already exists
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise ValueError("Email already in use.")

    # Validate role assignment permissions
    if current_user:
        # Only super_admin can create admin users
        if user.role == UserRole.ADMIN and current_user.role != UserRole.SUPER_ADMIN:
            raise HTTPException(
                status_code=403,
                detail="Only super admins can create admin users"
            )

        # Only super_admin can create other super_admin users
        if user.role == UserRole.SUPER_ADMIN and current_user.role != UserRole.SUPER_ADMIN:
            raise HTTPException(
                status_code=403,
                detail="Only super admins can create super admin users"
            )

    # Hash the password
    hashed_password = bcrypt.hash(user.password)

    # Create a new user
    new_user = User(
        email=user.email,
        hashed_password=hashed_password,
        phone=user.phone,
        role=user.role,  # Set the role from the request
        is_active=True,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Create an initial profile for the user
    initial_profile = Profile(
        user_id=new_user.id,
        first_name="",  # Empty string or None for optional fields
        last_name="",
        address="",
        city="",
        state="",
        zip_code="",
        country=""
    )

    db.add(initial_profile)
    db.commit()
    db.refresh(initial_profile)
    return new_user





"""
    Authenticates a user by verifying email and password.

    Args:
        db (Session): Database session dependency.
        email (str): The email address of the user.
        password (str): The plaintext password provided by the user.

    Returns:
        User: The authenticated user instance.

    Raises:
        ValueError: If the email is not found or the password is incorrect.
    """
def login_user(db: Session, email: str, password: str):
    # Fetch the user by email
    user = db.query(User).filter(User.email == email).first()
    if not user or not bcrypt.verify(password, user.hashed_password):
        raise ValueError("Invalid credentials.")

    return user





"""
    Verifies a JWT and extracts the user ID from its payload.

    Args:
        token (str): The JWT to be verified.

    Returns:
        str: The user ID extracted from the token's payload.

    Raises:
        HTTPException: If the token is invalid or expired.
"""
def verify_token(token: str):
    try:
        payload = jwt.decode(token, os.getenv("SECRET_KEY"), algorithms=["HS256"])
        return payload.get("user_id")  # Return the user ID from the payload
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")




