from .. import model, schemas
from fastapi import FastAPI, Response, status, HTTPException, APIRouter
from sqlalchemy.orm import Session
from fastapi import Depends
from ..database import get_db
from ..utils import hash_password

router = APIRouter(
    prefix="/users",
    tags=["users"]
)

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.UserOut)
def create_user(user: schemas.UserCreate, db:Session=Depends(get_db)):
    """Create a new user."""
    new_user = model.User(**user.model_dump())
    # hash the password
    hased_password = hash_password(user.password)
    new_user.password = hased_password

    try:
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
    
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail=f"An error occurred: {e}"
        )

    return new_user

@router.get("/{id}", response_model=schemas.UserOut)
def get_users(id:int, db: Session = Depends(get_db)):
    """Get all users from the database."""
    user = db.query(model.User).filter(model.User.id==id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id: {id} was not found."
        )

    return user

