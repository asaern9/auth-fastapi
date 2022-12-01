from pydantic import BaseModel


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None


class UserSchemaRequest(BaseModel):
    username: str
    email: str | None = None
    fullname: str | None = None
    password: str


class UserSchemaResponse(BaseModel):
    username: str
    email: str | None = None
    fullname: str | None = None


class UserInDB(UserSchemaResponse):
    hashed_password: str

