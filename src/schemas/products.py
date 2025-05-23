from datetime import datetime
from typing import Optional, List, ClassVar
from uuid import UUID

from pydantic import BaseModel, Field, ConfigDict, validator

from src.schemas.categories import CategoryBaseModel


class ProductBaseModel(BaseModel):
    uid: UUID
    title: str = Field(..., description="Nome do produto")
    description: str = Field(..., description="Descrição do produto")
    price: float = Field(..., description="Valor de venda")
    bar_code: str = Field(..., description="Código de barras do produto")
    section: str = Field(..., description="Seção do produto")
    date_validation: Optional[datetime] = Field(None, description="Data de validade do produto")
    stock: int = Field(..., description="Quantidade em estoque")
    brand: Optional[str] = Field(None, description="Marca do produto")
    discount_percentage: float = Field(description="Desconto aplicado ao produto")
    rating: float = Field(default=0.0, description="Avaliação do produto")
    is_published: bool = Field(default=False, description="Disponível para venda")
    images: List[str] = Field(default_factory=list, description="Imagens do produto")
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    categories: Optional[str] = Field(None, description="Categoria do produto")

    model_config = ConfigDict(from_attributes=True)

    @validator("discount_percentage", pre=True)
    def validate_discount_percentage(cls, v):
        if v < 0 or v > 100:
            raise ValueError("discount_percentage must be between 0 and 100")
        return v


class ProductCreateModel(ProductBaseModel):
    uid: UUID = Field(default_factory=UUID)
    category: ClassVar[CategoryBaseModel] = CategoryBaseModel

    model_config = ConfigDict(from_attributes=True)


class ProductUpdateModel(ProductBaseModel):
    pass

    model_config = ConfigDict(from_attributes=True)


class ProductOutModel(BaseModel):
    """
    Model for the response of a single product.
    """
    message: str
    status: str
    data: ProductBaseModel

    model_config = ConfigDict(from_attributes=True)


class ProductsOutModel(BaseModel):
    """
    Model for the response of multiple products.
    """
    message: str
    status: str
    data: List[ProductBaseModel]

    model_config = ConfigDict(from_attributes=True)


class ProductDeleteModel(ProductBaseModel):
    """
    Model for the response of a deleted product.
    """
    category: ClassVar[CategoryBaseModel] = CategoryBaseModel


class ProductOutDeleteModel(BaseModel):
    message: str
    status: str
    data: ProductDeleteModel
