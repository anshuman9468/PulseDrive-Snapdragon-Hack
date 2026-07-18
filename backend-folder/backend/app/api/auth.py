from fastapi import APIRouter, HTTPException, status

from app.models.user import AuthResponse, UserCreate, UserLogin
from app.services.auth_service import AuthService

router = APIRouter(tags=["auth"])
auth_service = AuthService()


@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def register(user: UserCreate) -> AuthResponse:
    """
    Register a new user.
    
    - Email must be unique
    - Password is hashed with bcrypt
    - Returns JWT access token and user info
    """
    try:
        user_response = auth_service.create_user(user)
        access_token = auth_service.create_access_token(subject=user.email)
        
        return AuthResponse(
            access_token=access_token,
            token_type="bearer",
            user=user_response
        )
    except ValueError as e:
        if "Email already exists" in str(e):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already exists"
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed"
        )


@router.post("/login", response_model=AuthResponse)
async def login(credentials: UserLogin) -> AuthResponse:
    """
    Login user with email and password.
    
    - Validates credentials against MongoDB
    - Generates JWT access token
    - Returns token and user info
    """
    try:
        access_token, user_response = auth_service.authenticate_user(credentials)
        
        return AuthResponse(
            access_token=access_token,
            token_type="bearer",
            user=user_response
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed"
        )
