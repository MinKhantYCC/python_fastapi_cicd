from pydantic import BaseModel

## Pydantic Models
class Post(BaseModel):
    title: str
    content: str
    published: bool = True