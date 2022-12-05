from fastapi import FastAPI
import auth_controller

app = FastAPI()

# Uncomment if you don't want to use alembic
# Base.metadata.create_all(bind=engine)

app.include_router(auth_controller.router, prefix="/user", tags=["USERS"])


@app.get("/")
async def index():
    return "FastApi auth template"
