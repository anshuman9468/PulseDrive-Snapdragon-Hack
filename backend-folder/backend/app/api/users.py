from fastapi import APIRouter, Depends

from app.api.dependencies import get_current_user

router = APIRouter(
    prefix="/api/users",
    tags=["Users"],
)


@router.get("/me")
async def get_profile(current_user=Depends(get_current_user)):
    return {
        "id": current_user["_id"],
        "username": current_user["username"],
        "email": current_user["email"],
        "created_at": current_user["created_at"],
    }