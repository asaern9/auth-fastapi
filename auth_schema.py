from pydantic import BaseModel, EmailStr


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None


class UserSchemaRequest(BaseModel):
    username: str
    email: EmailStr | None = None
    fullname: str | None = None
    password: str


class UserSchemaResponse(BaseModel):
    username: str
    email: str | None = None
    fullname: str | None = None


