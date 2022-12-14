from fastapi.security import OAuth2PasswordBearer
from auth_model import UserModel
from datetime import timedelta
from auth_schema import UserSchemaResponse, Token, UserSchemaRequest
from fastapi import Depends, APIRouter, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from config import Settings
from functools import lru_cache

router = APIRouter()

settings = Settings()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="user/login")


@lru_cache()
def get_settings():
    return Settings()


@router.post("/create/", response_model=UserSchemaResponse)
async def sign_up(form_data: UserSchemaRequest):
    return UserModel.save_user(form_data)


@router.post("/login", response_model=Token)
async def sign_in(form_data: OAuth2PasswordRequestForm = Depends()):
    user = UserModel.verify_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password",
                            headers={"WWW-Authenticate": "Bearer"}, )
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = UserModel.generate_access_token(data={"sub": user.username}, expires_delta=access_token_expires)
    UserModel.save_token(access_token, form_data.username)
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/profile/", response_model=UserSchemaResponse)
async def view_profile(user_token: str = Depends(oauth2_scheme)):
    token = UserModel.verify_token(user_token)
    return UserModel.fetch_current_user(token)


@router.post("/logout")
async def logout(token: str = Depends(oauth2_scheme)):
    user = UserModel.fetch_current_user(token)
    username = user["username"]
    return UserModel.delete_token(username)
