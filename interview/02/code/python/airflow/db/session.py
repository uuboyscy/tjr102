from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from .settings import (
    LOAD_DB_HOST,
    LOAD_DB_PORT,
    LOAD_DB_USER,
    LOAD_DB_PASS,
    LOAD_DB_DATABASE,
    ADMIN_DB_USER,
    ADMIN_DB_PASS,
)


def get_engine(host, user, password, port, database):
    engine = create_engine(
        f"postgresql://{user}:{password}@{host}:{port}/{database}",
        connect_args={"connect_timeout": 10},
        pool_pre_ping=True,
        echo=True,
    )
    return engine


engine = get_engine(
    LOAD_DB_HOST, LOAD_DB_USER, LOAD_DB_PASS, LOAD_DB_PORT, LOAD_DB_DATABASE
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
