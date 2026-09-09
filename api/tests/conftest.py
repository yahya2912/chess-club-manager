"""Shared pytest fixtures for API tests.

Tests run against a dedicated PostgreSQL database named chessdb_test.
The test database is dropped, recreated, and seeded once at the start
of every pytest session.

The normal development database (chessdb) is never modified.
"""

import os
from pathlib import Path

import psycopg
from psycopg import sql
import pytest
from dotenv import load_dotenv
from fastapi.testclient import TestClient


# Repository root: chess-club-manager/
ROOT = Path(__file__).resolve().parents[2]

# Load local connection settings when running outside CI.
# CI-provided environment variables take precedence.
load_dotenv(ROOT / ".env", override=False)


DEV_DB = os.environ["POSTGRES_DB"]
TEST_DB = os.environ.get("POSTGRES_TEST_DB", "chessdb_test")

# Safety: pytest must never destroy the development/system databases.
if TEST_DB in {DEV_DB, "postgres", "template0", "template1"}:
    raise RuntimeError(
        f"Unsafe test database name: {TEST_DB!r}. "
        "POSTGRES_TEST_DB must be different from POSTGRES_DB."
    )

# config.py reads these variables when app.main is imported.
os.environ["POSTGRES_DB"] = TEST_DB
os.environ["API_KEY"] = os.environ.get("TEST_API_KEY", "test-key")

from app.main import app  # noqa: E402

API_KEY = os.environ["API_KEY"]


def connection_args(dbname: str) -> dict:
    return {
        "host": os.environ.get("POSTGRES_HOST", "localhost"),
        "port": os.environ.get("POSTGRES_PORT", "5432"),
        "dbname": dbname,
        "user": os.environ["POSTGRES_USER"],
        "password": os.environ["POSTGRES_PASSWORD"],
    }


@pytest.fixture(scope="session", autouse=True)
def test_database():
    """Create a fresh, seeded database exclusively for pytest."""

    # CREATE/DROP DATABASE must run outside a transaction.
    with psycopg.connect(
        **connection_args("postgres"),
        autocommit=True,
    ) as conn:
        # Disconnect stale sessions from an earlier pytest run.
        conn.execute(
            """
            SELECT pg_terminate_backend(pid)
            FROM pg_stat_activity
            WHERE datname = %s
              AND pid <> pg_backend_pid()
            """,
            (TEST_DB,),
        )

        conn.execute(
            sql.SQL("DROP DATABASE IF EXISTS {}").format(
                sql.Identifier(TEST_DB)
            )
        )

        conn.execute(
            sql.SQL("CREATE DATABASE {}").format(
                sql.Identifier(TEST_DB)
            )
        )

    schema_sql = (ROOT / "db" / "01_schema.sql").read_text(encoding="utf-8")
    seed_sql = (ROOT / "db" / "02_seed.sql").read_text(encoding="utf-8")

    with psycopg.connect(**connection_args(TEST_DB)) as conn:
        conn.execute(schema_sql)
        conn.execute(seed_sql)
        conn.commit()

    yield


@pytest.fixture(scope="session")
def client(test_database):
    """FastAPI client using the isolated test database."""
    return TestClient(app)


@pytest.fixture(scope="session")
def auth():
    """Valid authentication header for API requests."""
    return {"X-API-Key": API_KEY}
