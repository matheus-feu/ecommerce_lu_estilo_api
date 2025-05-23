import re
from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field, validator, ConfigDict, EmailStr


class UserCreateModel(BaseModel):
    """
    Modelo para criação de novo usuário.
    """

    username: str = Field(..., description="Nome de usuário")
    email: EmailStr = Field(..., description="E-mail do usuário")
    first_name: str = Field(..., description="Primeiro nome do usuário")
    last_name: str = Field(..., description="Sobrenome do usuário")
    password: str = Field(..., description="Senha do usuário")

    model_config = {
        "json_schema_extra": {
            "example": {
                "username": "matheus feu",
                "email": "matheusfeu@gmail.com",
                "first_name": "Matheus",
                "last_name": "Feu",
                "password": "12345678"
            }
        }
    }


class UserLoginModel(BaseModel):
    """
    User login model for authentication.
    """
    email: EmailStr = Field(max_length=40)
    password: str = Field(max_length=12)

    @validator("password")
    def validate_password(cls, password):
        if not (8 <= len(password) <= 12):
            raise ValueError("A senha deve ter entre 8 e 12 caracteres")
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
            raise ValueError("A senha deve conter pelo menos um caractere especial")
        return password


class PasswordResetRequestModel(BaseModel):
    email: EmailStr


class PasswordResetConfirmModel(BaseModel):
    secret_token: str
    new_password: str
    confirm_new_password: str


class UserResponseModel(BaseModel):
    """
    User response model for returning user data.
    """

    uid: UUID
    email: EmailStr
    role: str
    created_at: datetime
    updated_at: datetime
    last_login: Optional[datetime]

    model_config = ConfigDict(from_attributes=True)


class SignupResponseModel(BaseModel):
    message: str
    success: bool
    status_code: int
    user: UserResponseModel

    model_config = ConfigDict(from_attributes=True)
