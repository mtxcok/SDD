from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.services.auth_service import AuthService
from app.schemas.token import Token
from app.schemas.user import UserCreate, User

router = APIRouter()

@router.post("/login", response_model=Token)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: Annotated[AsyncSession, Depends(get_db)]
):
    auth_service = AuthService(session)
    # Create a dummy user login object since OAuth2PasswordRequestForm has username/password
    from app.schemas.user import UserLogin
    user = await auth_service.authenticate_user(UserLogin(username=form_data.username, password=form_data.password))
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = auth_service.create_token(user)
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/register", response_model=User)
async def register_user(
    user_in: UserCreate,
    session: Annotated[AsyncSession, Depends(get_db)]
):
    # Simple registration for demo purposes
    auth_service = AuthService(session)
    # Check if user exists... (omitted for brevity, repo handles unique constraint error usually)
    return await auth_service.create_user(user_in)
