import re
from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, ConfigDict, validator


class CustomerModel(BaseModel):
    """
    User model for returning user data.
    """
    uid: UUID
    username: Optional[str]
    email: Optional[EmailStr]
    first_name: Optional[str]
    last_name: Optional[str]
    cpf: Optional[str]
    is_active: bool
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    model_config = ConfigDict(from_attributes=True)


class CustomerOutModel(BaseModel):
    """
    User model for returning user data.
    """

    message: str
    status: str
    data: CustomerModel

    model_config = ConfigDict(from_attributes=True)


class CustomersOutModel(BaseModel):
    """
    User model for returning user data.
    """

    message: str
    status: str
    data: List[CustomerModel]

    model_config = ConfigDict(from_attributes=True)


class CustomerOutDeleteModel(BaseModel):
    """
    User model for returning user data.
    """

    message: str
    status: str
    data: CustomerModel | None


class CustomerCreateModel(BaseModel):
    """
    Modelo para criação de cliente.
    """

    username: str = Field(..., description="Nome de usuário do cliente")
    email: EmailStr = Field(..., description="E-mail do cliente")
    first_name: str = Field(..., description="Primeiro nome do cliente")
    last_name: str = Field(..., description="Sobrenome do cliente")
    cpf: str = Field(..., description="CPF do cliente (apenas números, 11 dígitos)")
    password: str = Field(..., description="Senha do cliente")

    model_config = ConfigDict(from_attributes=True)

    @validator("cpf")
    def validate_cpf(cls, cpf):
        if not cpf:
            raise ValueError("CPF é obrigatório")
        if not re.fullmatch(r"\d{11}", cpf):
            raise ValueError("CPF deve conter exatamente 11 dígitos numéricos")
        return cpf


class CustomerUpdateModel(CustomerCreateModel):
    pass
