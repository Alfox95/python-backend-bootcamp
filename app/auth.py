from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from sqlalchemy.orm import Session
from sqlalchemy import or_
from jose import jwt, JWTError

from app.database import get_db
from app.models import Usuario
from app.security import verify_password
from app.core.config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp":expire})
    token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return token

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credential_exception = HTTPException(
        status_code=401,
        detail="No se pudo identificar al usuario",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credential_exception
    except (JWTError, KeyError, TypeError):
        raise credential_exception
    
    user = db.query(Usuario).filter(Usuario.nombre == username).first()
    if user is None:
        raise credential_exception
    return user


@router.post("/login")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)  
):
    user = db.query(Usuario).filter(
        or_(
            Usuario.username == form_data.username,
            Usuario.mail == form_data.username
        )
    ).first()

    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(status_code=401, detail="Usuario o contraseña incorrecto")
    
    token = create_access_token({"sub": user.username})
    return {"access_token": token, "token_type": "bearer"}

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credential_exception = HTTPException(
        status_code=401,
        detail="No se pudo identificar al usuario",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credential_exception
    except (JWTError, KeyError, TypeError):
        raise credential_exception

    user = db.query(Usuario).filter(Usuario.username == username).first()
    if user is None:
        raise credential_exception
    return user

def requiere_admin(current_user: Usuario = Depends(get_current_user)):
    if not current_user.es_admin:
        raise HTTPException(status_code=403, detail="Se requieren permisos de admin")
    return current_user