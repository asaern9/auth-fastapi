from fastapi import FastAPI
import auth_controller
from auth_db import Base, engine
app = FastAPI()

Base.metadata.create_all(bind=engine)

app.include_router(auth_controller.router, tags=["USERS"])


@app.get("/")
async def index():
    return "hey"
