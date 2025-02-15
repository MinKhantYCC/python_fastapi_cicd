from jose import JWTError, jwt
from datetime import datetime, timedelta
from . import schemas
from fastapi import HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer

oauth2_shceme = OAuth2PasswordBearer(tokenUrl="login") # the tokenUrl is the endpoint where the user will send their credentials to get a token
# SECRET_KEY
# ALGORITHM
# EXPIRATION_TIME

SECRET_KEY = "mysecretkey"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def verify_access_token(token:str, credentials_exception):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("user_id")
        if user_id is None:
            raise credentials_exception
        toeken_data = schemas.TokenData(id=user_id)
    except JWTError:
        raise credentials_exception
    return toeken_data
    
def get_current_user(token:str=Depends(oauth2_shceme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"}
    )
    return verify_access_token(token, credentials_exception)