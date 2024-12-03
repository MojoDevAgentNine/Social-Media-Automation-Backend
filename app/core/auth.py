import os
import jwt
from passlib.hash import bcrypt
from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user_schema import UserRegisterRequest


def register_user(db: Session, user: UserRegisterRequest):
    # Check if the user already exists
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise ValueError("Email already in use.")

    # Hash the password
    hashed_password = bcrypt.hash(user.password)

    # Create a new user
    new_user = User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password,
        is_active=True,
        is_admin=False,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


def login_user(db: Session, email: str, password: str):
    # Fetch the user by email
    user = db.query(User).filter(User.email == email).first()
    if not user or not bcrypt.verify(password, user.hashed_password):
        raise ValueError("Invalid credentials.")

    return user



def verify_token(token: str):
    try:
        payload = jwt.decode(token, os.getenv("SECRET_KEY"), algorithms=["HS256"])
        return payload.get("user_id")
    except jwt.PyJWTError:
        return None














