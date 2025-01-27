from fastapi import FastAPI
from . import model
from .database import engine
from sqlalchemy.orm import Session
from fastapi import Depends
from typing import List
from .routers import post, user

model.Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(post.router)
app.include_router(user.router)

## routes
@app.get("/")
def index():
    return {"message": "Hello World"}


