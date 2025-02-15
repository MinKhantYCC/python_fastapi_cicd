from .. import model, schemas
from fastapi import Response, status, HTTPException, APIRouter
from sqlalchemy.orm import Session
from fastapi import Depends
from ..database import get_db
from typing import List
from .. import oauth2

router = APIRouter(
    prefix="/posts",
    tags=["posts"]
)


@router.get("/", response_model=List[schemas.Post])
def get_posts(db: Session = Depends(get_db)):
    """Get all posts from the database."""
    posts = db.query(model.Post).all()
    return posts


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.Post)
def create_post(payload: schemas.PostBase, db:Session=Depends(get_db), get_current_user: int=Depends(oauth2.get_current_user)):
    """create a new post."""

    new_post = model.Post(**payload.model_dump())
    try:
        db.add(new_post)        # add the new post to the database
        db.commit()             # commit the transaction to update the database
        db.refresh(new_post)    # refresh the database to get the updated values
    
    # handle exceptions
    except Exception as e:
        db.rollback()           # rollback the transaction if an error occurs
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail=f"An error occurred: {e}"
        )

    return new_post


@router.get("/{id}")
def get_post(id:int, db:Session=Depends(get_db)):
    """Get a single post with ID from the database."""
    post = db.query(model.Post).filter(model.Post.id==id).first()

    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"Post with id: {id} was not found."
        )
    return post


@router.put("/{id}", response_model=schemas.Post)
def update_post(id:int, post: schemas.PostBase, db:Session=Depends(get_db)):
    """Update a post with ID."""
    post_query = db.query(model.Post).filter(model.Post.id == id)

    # check if the post exists
    if post_query.first() == None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"Post with {id} does not exist."
        )
    
    # update the post
    post_query.update(post.model_dump(), synchronize_session=False)

    # commit the transaction
    try:
        db.commit()
        db.refresh(post_query.first())
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail=f"An error occurred: {e}"
        )
    
    return post_query.first()


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id:int, db:Session=Depends(get_db)):
    """Delete a post with ID."""
    post = db.query(model.Post).filter(model.Post.id==id)

    # check if the post exists
    if post.first() == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post with {id} does not exist.")

    # delete the post
    try:
        post.delete(synchronize_session=False)
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail=f"An error occurred: {e}"
        )

    return Response(status_code=status.HTTP_204_NO_CONTENT)
