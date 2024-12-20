from fastapi import FastAPI, Response, status, HTTPException
import psycopg2
import time
from psycopg2.extras import RealDictCursor
from . import model, schemas
from .database import get_db, engine
from sqlalchemy.orm import Session
from fastapi import Depends
from typing import List

app = FastAPI()

## routes
@app.get("/")
def index():
    return {"message": "Hello World"}

@app.get("/posts", response_model=List[schemas.Post])
def get_posts(db: Session = Depends(get_db)):
    posts = db.query(model.Post).all()
    return posts

@app.post("/posts", status_code=status.HTTP_201_CREATED, response_model=schemas.Post)
def create_post(payload: schemas.PostBase, db:Session=Depends(get_db)):
    new_post = model.Post(**payload.model_dump())
    db.add(new_post)
    db.commit()
    db.refresh(new_post)

    return new_post

@app.get("/posts/{id}")
def get_post(id:int, db:Session=Depends(get_db)):
    post = db.query(model.Post).filter(model.Post.id==id).first()
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"Post with id: {id} was not found."
        )
    return post

@app.put("/posts/{id}", response_model=schemas.Post)
def update_post(id:int, post: schemas.PostBase, db:Session=Depends(get_db)):
    post_query = db.query(model.Post).filter(model.Post.id == id)
    if post_query.first() == None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"Post with {id} does not exist."
        )
    post_query.update(post.model_dump(), synchronize_session=False)
    db.commit()
    db.refresh(post_query.first())
    return post_query.first()

@app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id:int, db:Session=Depends(get_db)):
    post = db.query(model.Post).filter(model.Post.id==id)

    if post.first() == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post with {id} does not exist.")

    post.delete(synchronize_session=False)
    db.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)