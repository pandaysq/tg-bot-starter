from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker, create_async_engine

from app.database.models import Base


@dataclass(slots=True)
class Database:
    engine: AsyncEngine
    session_factory: async_sessionmaker

    async def create_schema(self) -> None:
        async with self.engine.begin() as connection:
            await connection.run_sync(Base.metadata.create_all)

    async def dispose(self) -> None:
        await self.engine.dispose()


def create_database(database_url: str) -> Database:
    engine = create_async_engine(database_url, pool_pre_ping=True)
    return Database(
        engine=engine,
        session_factory=async_sessionmaker(engine, expire_on_commit=False),
    )