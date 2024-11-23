from sqlmodel import Session, create_engine
from contextlib import asynccontextmanager
from api import logging, APP_DB_CONFIG
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager


def get_database_url(for_async_tasks=False):
    """
    Returns the database URL based on the provided APP_DB_CONFIG.
    If for_async_tasks is True, returns an async-compatible URL.
    If for_async_tasks is False, returns a regular synchronous URL.
    """
    if not for_async_tasks:
        # Return synchronous database URL (normal behavior)
        config = APP_DB_CONFIG

        if not config:
            # logging.info("No valid database config found, defaulting to SQLite.")
            return "sqlite:///./app_db.db"  # Synchronous SQLite URL

        elif "mysql" in config:
            mysql_config = config["mysql"]
            return f"mysql+mysqlconnector://{mysql_config['user']}:{mysql_config['password']}@{mysql_config['host']}:{mysql_config['port']}/{mysql_config['database_name']}"

        elif "postgres" in config:
            postgres_config = config["postgres"]
            return f"postgresql+psycopg2://{postgres_config['user']}:{postgres_config['password']}@{postgres_config['host']}:{postgres_config['port']}/{postgres_config['database_name']}"

    else:
        # Return asynchronous database URL (for async tasks)
        config = APP_DB_CONFIG

        if not config:
            # logging.info("No valid database config found, defaulting to SQLite.")
            return "sqlite+aiosqlite:///./app_db.db"  # Asynchronous SQLite URL

        elif "mysql" in config:
            mysql_config = config["mysql"]
            return f"mysql+aiomysql://{mysql_config['user']}:{mysql_config['password']}@{mysql_config['host']}:{mysql_config['port']}/{mysql_config['database_name']}"

        elif "postgres" in config:
            postgres_config = config["postgres"]
            return f"postgresql+asyncpg://{postgres_config['user']}:{postgres_config['password']}@{postgres_config['host']}:{postgres_config['port']}/{postgres_config['database_name']}"


# Dependency to get an async session
@asynccontextmanager
async def get_session(for_async_tasks=False):
    DATABASE_URL = get_database_url(for_async_tasks=for_async_tasks)

    # Create an asynchronous engine if for_async_tasks is True, else a regular engine
    if for_async_tasks:
        engine = create_async_engine(DATABASE_URL, echo=True)
        async with AsyncSession(engine) as session:
            yield session
    else:
        engine = create_engine(DATABASE_URL, echo=True)
        with Session(engine) as session:
            yield session


@contextmanager
def get_sync_session():
    DATABASE_URL = get_database_url(for_async_tasks=False)
    sync_engine = create_engine(DATABASE_URL, echo=True)
    SyncSession = sessionmaker(bind=sync_engine, autocommit=False, autoflush=False)

    session = SyncSession()
    try:
        yield session
    finally:
        session.close()
