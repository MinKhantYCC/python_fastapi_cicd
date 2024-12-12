from fastapi import FastAPI, Response, status, HTTPException
import psycopg2
import time
from psycopg2.extras import RealDictCursor
from . import model, schemas
from .database import get_db, engine
from sqlalchemy.orm import Session
from fastapi import Depends

model.Base.metadata.create_all(bind=engine)

app = FastAPI()

## database
while True:
    try:
        conn = psycopg2.connect(
            host="localhost", 
            database='fastapi', 
            user='postgres', 
            password='min#25699',
            cursor_factory=RealDictCursor,
        )
        cursor = conn.cursor()
        print("Database connection was successful.")
        break
    except Exception as e:
        print(f"Cannot connect to the database. Detail: {e}")
        time.sleep(3)

## routes
@app.get("/")
def index():
    return {"message": "Hello World"}

@app.get("/posts")
def get_posts(db: Session = Depends(get_db)):
    posts = db.query(model.Post).all()
    return {"data": posts}

@app.post("/posts", status_code=status.HTTP_201_CREATED)
def create_post(payload: schemas.Post, db:Session=Depends(get_db)):
    new_post = model.Post(**payload.model_dump())
    db.add(new_post)
    db.commit()
    db.refresh(new_post)

    return {"data": new_post}

@app.get("/posts/{id}")
def get_post(id:int, db:Session=Depends(get_db)):
    post = db.query(model.Post).filter(model.Post.id==id).first()
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"Post with id: {id} was not found."
        )
    return {"post": post}

@app.put("/posts/{id}")
def update_post(id:int, post: schemas.Post, db:Session=Depends(get_db)):
    post_query = db.query(model.Post).filter(model.Post.id == id)
    if post_query.first() == None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"Post with {id} does not exist."
        )
    post_query.update(post.model_dump(), synchronize_session=False)
    db.commit()
    db.refresh(post_query.first())
    return {"data": post_query.first()}

@app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id:int, db:Session=Depends(get_db)):
    post = db.query(model.Post).filter(model.Post.id==id)

    if post.first() == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post with {id} does not exist.")

    post.delete(synchronize_session=False)
    db.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)