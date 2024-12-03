from sqlalchemy.orm import Session
from app.models.user import User
from passlib.context import CryptContext
from app.schemas.user_schema import UserLoginRequest

# Create an instance of CryptContext for password hashing verification
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def login_user(db: Session, login_request: UserLoginRequest):
    # Check if the provided username_or_email is an email or username
    user = db.query(User).filter(
        (User.username == login_request.username_or_email) |
        (User.email == login_request.username_or_email)
    ).first()

    if user and verify_password(login_request.password, user.hashed_password):
        return user  # User authenticated successfully, return user object
    return None  # Authentication failed

def get_all_users(db: Session):
    # Query all users, only return necessary fields like username, email, and is_active
    return db.query(User.id, User.username, User.email, User.is_active).all()

def get_authenticated_user(db: Session, user_id: int):
    # Query the user based on their ID
    return db.query(User).filter(User.id == user_id).first()