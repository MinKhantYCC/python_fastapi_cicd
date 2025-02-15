from fastapi import APIRouter, Depends, HTTPException, status, Response
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from ..database import get_db
from .. import model, schemas
from ..utils import verify
from ..oauth2 import create_access_token

router = APIRouter(
    tags=["Authentication"],
)

@router.post("/login")
def login(user_credentials:OAuth2PasswordRequestForm = Depends(), db:Session=Depends(get_db)):
    # OAuth2PasswordRequestForm return two things. The username and the password.

    # get the user from the database
    user = db.query(model.User).filter(model.User.email==user_credentials.username).first()
    
    # check if the user exists
    if not user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Invalid credentials."
        )
    
    # check if the password is correct
    if not verify(user_credentials.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid credentials."
        )
    access_token = create_access_token(data={"user_id": user.id})

    # create a token
    return {"access_token": access_token, "token_type": "bearer"}

