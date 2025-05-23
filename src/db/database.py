from sqlalchemy.exc import ProgrammingError
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession

from src.core.config import settings
from src.core.logger import logger

async_engine = create_async_engine(settings.DATABASE_URL)
async_session = async_sessionmaker(bind=async_engine, expire_on_commit=False)


async def init_db() -> None:
    try:
        import src.db.__all_models # noqa: F401
        async with async_engine.begin() as conn:
            logger.info("Criando tabelas do banco de dados...")
            await conn.run_sync(SQLModel.metadata.create_all)
    except ProgrammingError as e:
        logger.error(f"Erro ao criar tabelas: {e}")


async def get_session() -> AsyncSession:
    async with async_session() as session:
        yield session
