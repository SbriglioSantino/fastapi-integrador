from typing import Any
from fastapi import FastAPI
from pydantic import BaseModel, EmailStr

app = FastAPI()


# 1. Base común para evitar repetición (DRY - Don't Repeat Yourself)
class UserBase(BaseModel):
    username: str
    email: EmailStr
    full_name: str | None = None


# 2. Modelo para creación (hereda la base + password)
class UserCreate(UserBase):
    password: str


# 3. Modelo para respuesta (hereda la base, no añade nada pero es un contrato claro)
class UserPublic(UserBase):
    pass


@app.post("/users/", response_model=UserPublic, status_code=201)
async def create_user(user: UserCreate) -> UserPublic:
    # 1. Aquí iría la lógica de base de datos (guardar el usuario)
    # user_db = db.save(user)

    # 2. Transformamos/Convertimos el objeto al modelo de salida
    return UserPublic(**user.model_dump())
