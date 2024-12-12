from typing import Optional
from fastapi import FastAPI, Response, status, HTTPException
import psycopg2
import time
from psycopg2.extras import RealDictCursor
from pydantic import BaseModel
import model
from database import engine, SessionLocal

model.Base.metadata.create_all(bind=engine)

app = FastAPI()

## Models
class Post(BaseModel):
    title: str
    content: str
    published: bool = False

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
def get_posts():
    cursor.execute("""SELECT * FROM posts""")
    posts = cursor.fetchall()
    return {"data": posts}

@app.post("/posts", status_code=status.HTTP_201_CREATED)
def create_post(payload: Post):
    cursor.execute(
        """INSERT INTO posts (title, content, published) VALUES (%s, %s, %s) RETURNING *""",
        (payload.title, payload.content, payload.published)
    )
    new_post = cursor.fetchone()
    conn.commit()
    return {"data": new_post}

@app.get("/posts/{id}")
def get_post(id:int, response: Response):
    # post = find_post(id)
    cursor.execute(
        """SELECT * FROM posts WHERE id = %s""",
        (id,)
    )
    post = cursor.fetchone()
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"Post with id: {id} was not found."
        )
    return {"post": post}

@app.put("/posts/{id}")
def update_post(id:int, post: Post):
    cursor.execute(
        """UPDATE posts SET title=%s, content=%s, published=%s WHERE id=%s RETURNING *""",
        (post.title, post.content, post.published, id)
    )
    updated_post = cursor.fetchone()
    conn.commit()

    if updated_post == None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"Post with {id} does not exist."
        )
    return {"data": updated_post}

@app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id:int):
    cursor.execute(
        """DELETE FROM posts WHERE id = %s RETURNING *""",
        (str(id),)
    )
    post = cursor.fetchone()
    conn.commit()

    if post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post with {id} does not exist.")

    return Response(status_code=status.HTTP_204_NO_CONTENT)