from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional


## Pydantic Models
class PostBase(BaseModel):
    title: str
    content: str
    published: bool = False


class Post(PostBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class UserCreate(BaseModel):
    email: EmailStr
    password: str

## We don't inherit from UserCreate because we don't want to return the password
## Instead, we will create a new model that inherits from BaseModel
class UserOut(BaseModel):
    id: int
    created_at: datetime
    email: EmailStr

    class Config:
        orm_mode = True


class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    id: Optional[str] = None