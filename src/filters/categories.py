from typing import Optional

from fastapi_filter.contrib.sqlalchemy import Filter

from src.models.category import Category


class CategoryFilter(Filter):
    class Constants(Filter.Constants):
        model = Category

    uid: Optional[str] = None
    name: Optional[str] = None
