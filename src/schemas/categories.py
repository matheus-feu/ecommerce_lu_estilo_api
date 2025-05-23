from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field, ConfigDict


class CategoryBaseModel(BaseModel):
    """
    Base model for category.
    """
    uid: Optional[UUID] = None
    name: str = Field(..., description="Nome da categoria")

    model_config = ConfigDict(from_attributes=True)


class CategoryCreateModel(CategoryBaseModel):
    """
    Model for creating a category.
    """
    name: str = Field(..., description="Nome da categoria")


class CategoryUpdateModel(CategoryBaseModel):
    """
    Model for updating a category.
    """
    name: str = Field(..., description="Nome da categoria")


class CategoryOutModel(BaseModel):
    """
    Model for the response of a single category.
    """
    message: str
    status: str
    data: CategoryBaseModel


class CategoriesOutModel(BaseModel):
    """
    Model for the response of multiple categories.
    """
    message: str
    status: str
    data: List[CategoryBaseModel]


class CategoryOutDeleteModel(BaseModel):
    """
    Model for the response of a deleted category.
    """
    message: str
    status: str
    data: CategoryBaseModel | None
