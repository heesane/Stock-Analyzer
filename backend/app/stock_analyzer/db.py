from __future__ import annotations

import os

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL")
if DATABASE_URL:
    database_url = DATABASE_URL
else:
    sqlite_path = os.getenv("SQLITE_PATH", "./stock.db")
    database_url = f"sqlite:///{sqlite_path}"

engine = create_engine(database_url, future=True, echo=False)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
Base = declarative_base()
