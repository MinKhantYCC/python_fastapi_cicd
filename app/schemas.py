from pydantic import BaseModel
from datetime import datetime

## Pydantic Models
class PostBase(BaseModel):
    title: str
    content: str
    published: bool = True

class Post(PostBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True