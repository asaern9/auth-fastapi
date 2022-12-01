from passlib.context import CryptContext
from sqlalchemy import Column, String, Integer
from auth_db import SessionLocal, Base
from datetime import datetime
from config import Settings
from jose import JWTError, jwt
from auth_schema import TokenData
from datetime import timedelta
from fastapi import HTTPException, status

settings = Settings()
db = SessionLocal()
try:
    db
finally:
    db.close()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserModel(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False)
    fullname = Column(String)
    email = Column(String, unique=True)
    password = Column(String, nullable=False)
    token = Column(String)

    @classmethod
    def fetch_all_user(cls):
        return db.query(UserModel).all()

    @classmethod
    def verify_password(cls, plain_password, hashed_password):
        return pwd_context.verify(plain_password, hashed_password)

    @classmethod
    def hash_password(cls, password):
        return pwd_context.hash(password)

    @classmethod
    def get_existing_user(cls, username: str):
        all_users = cls.fetch_all_user()
        existing_user_names = []
        for i in range(len(all_users)):
            existing_user_names.append(all_users[i].username)
        if username in existing_user_names:
            user = db.query(UserModel).filter(UserModel.username == username).first()
            return user

    @classmethod
    def verify_user(cls, username: str, password: str):
        all_users = cls.fetch_all_user()
        existing_user_names = []
        existing_user_passwords = []
        for i in range(len(all_users)):
            existing_user_names.append(all_users[i].username)
            existing_user_passwords.append(all_users[i].password)
        if username in existing_user_names:
            user = db.query(UserModel).filter(UserModel.username == username).first()
            if not user:
                return False
            if not cls.verify_password(password, user.password):
                return False
            return user

    @classmethod
    def generate_access_token(cls, data: dict, expires_delta: timedelta | None = None):
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=15)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        return encoded_jwt

    @classmethod
    def fetch_current_user(cls, token: str):
        credentials_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                              detail="Could not validate credentials",
                                              headers={"WWW-Authenticate": "Bearer"}, )
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            username: str = payload.get("sub")
            if username is None:
                raise credentials_exception
            token_data = TokenData(username=username)
        except JWTError:
            raise credentials_exception
        user = cls.get_existing_user(username=token_data.username)
        if user is None:
            raise credentials_exception
        return {"username": user.username, "fullname": user.fullname, "email": user.email}

    @classmethod
    def save_user(cls, form_data):
        hashed_password = cls.hash_password(form_data.password)
        form_data.password = hashed_password
        new_user = UserModel(username=form_data.username, fullname=form_data.fullname, email=form_data.email, password=hashed_password)
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return {"username": new_user.username, "fullname": new_user.fullname, "email": new_user.email}

    @classmethod
    def verify_token(cls, token):
        stored_token = db.query(UserModel.token).filter(UserModel.token == token).all()
        if token in stored_token:
            return token
        else:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token verification failed")
