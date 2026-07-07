from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any, Optional

import pandas as pd
import streamlit as st
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine


@dataclass(frozen=True)
class PgConfig:
    host: str
    port: int
    database: str
    user: str
    password: str


def _get_from_secrets(key: str) -> Optional[str]:
    try:
        v = st.secrets.get(key)
        return str(v) if v is not None else None
    except Exception:
        return None


def get_pg_config() -> Optional[PgConfig]:
    """
    Supports:
    - DATABASE_URL (postgresql://user:pass@host:port/db)
    - or PGHOST/PGPORT/PGDATABASE/PGUSER/PGPASSWORD (env or st.secrets)
    """
    database_url = os.getenv("DATABASE_URL") or _get_from_secrets("DATABASE_URL")
    if database_url:
        # Let SQLAlchemy parse the URL. Config object not needed in this path.
        return None

    host = os.getenv("PGHOST") or _get_from_secrets("PGHOST")
    port = os.getenv("PGPORT") or _get_from_secrets("PGPORT")
    database = os.getenv("PGDATABASE") or _get_from_secrets("PGDATABASE")
    user = os.getenv("PGUSER") or _get_from_secrets("PGUSER")
    password = os.getenv("PGPASSWORD") or _get_from_secrets("PGPASSWORD")

    if not all([host, port, database, user, password]):
        return None

    return PgConfig(host=str(host), port=int(port), database=str(database), user=str(user), password=str(password))


@st.cache_resource
def get_engine() -> Optional[Engine]:
    database_url = os.getenv("DATABASE_URL") or _get_from_secrets("DATABASE_URL")
    if database_url:
        return create_engine(database_url, pool_pre_ping=True)

    cfg = get_pg_config()
    if cfg is None:
        return None

    url = f"postgresql+psycopg2://{cfg.user}:{cfg.password}@{cfg.host}:{cfg.port}/{cfg.database}"
    return create_engine(url, pool_pre_ping=True)


def can_connect() -> bool:
    eng = get_engine()
    if eng is None:
        return False
    try:
        with eng.connect() as conn:
            conn.execute(text("select 1"))
        return True
    except Exception:
        return False


@st.cache_data(ttl=300)
def read_sql(query: str, params: Optional[dict[str, Any]] = None) -> pd.DataFrame:
    eng = get_engine()
    if eng is None:
        raise RuntimeError("PostgreSQL engine is not configured. Set DATABASE_URL or PG* env vars / st.secrets.")
    with eng.connect() as conn:
        return pd.read_sql(text(query), conn, params=params or {})