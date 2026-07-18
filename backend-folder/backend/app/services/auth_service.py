from datetime import datetime, timedelta
from typing import Optional

from jose import JWTError, jwt
from passlib.context import CryptContext
from pymongo.collection import Collection

from app.config.database import get_database
from app.config.settings import settings
from app.models.user import UserCreate, UserLogin, UserResponse

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthService:
    def __init__(self):
        self.db = get_database()
        self.users_collection: Collection = self.db["users"]

    def hash_password(self, password: str) -> str:
        """Hash password using bcrypt."""
        return pwd_context.hash(password)

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify password against hash."""
        return pwd_context.verify(plain_password, hashed_password)

    def create_access_token(self, subject: str, expires_delta: Optional[timedelta] = None) -> str:
        """Generate JWT access token."""
        if expires_delta is None:
            expires_delta = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

        expire = datetime.utcnow() + expires_delta
        to_encode = {"sub": subject, "exp": expire}

        try:
            encoded_jwt = jwt.encode(
                to_encode,
                settings.SECRET_KEY,
                algorithm=settings.ALGORITHM
            )
            return encoded_jwt
        except Exception:
            raise ValueError("Failed to create access token")

    def create_user(self, user_data: UserCreate) -> UserResponse:
        """
        Create a new user in MongoDB.
        
        - Check if email already exists
        - Hash password
        - Store user data
        - Return UserResponse (without password)
        """
        existing_user = self.users_collection.find_one({"email": user_data.email})
        if existing_user:
            raise ValueError("Email already exists")

        hashed_password = self.hash_password(user_data.password)
        now = datetime.utcnow()

        user_doc = {
            "username": user_data.username,
            "email": user_data.email,
            "password": hashed_password,
            "created_at": now,
        }

        result = self.users_collection.insert_one(user_doc)
        user_id = str(result.inserted_id)

        return UserResponse(
            id=user_id,
            username=user_data.username,
            email=user_data.email,
            created_at=now,
        )

    def authenticate_user(self, credentials: UserLogin) -> tuple[str, UserResponse]:
        """
        Authenticate user by email and password.
        
        - Find user by email
        - Verify password
        - Generate JWT token
        - Return (access_token, UserResponse)
        """
        user_doc = self.users_collection.find_one({"email": credentials.email})
        
        if not user_doc:
            raise ValueError("Invalid email or password")

        if not self.verify_password(credentials.password, user_doc["password"]):
            raise ValueError("Invalid email or password")

        access_token = self.create_access_token(subject=credentials.email)
        user_id = str(user_doc["_id"])

        user_response = UserResponse(
            id=user_id,
            username=user_doc["username"],
            email=user_doc["email"],
            created_at=user_doc["created_at"],
        )

        return access_token, user_response
