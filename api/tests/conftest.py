"""Shared pytest fixtures for API tests.

These tests run against a real PostgreSQL database (the same schema and seed
data used in CI's db-schema-test job). The DB connection is configured via
environment variables, which CI sets to point at its postgres service and
which you can set locally to point at your Docker container.

Run locally (from repo root, with venv active and Postgres up):
    POSTGRES_HOST=localhost POSTGRES_USER=chess POSTGRES_PASSWORD=chess \\
    POSTGRES_DB=chessdb API_KEY=test-key pytest api/tests -v
"""
import os

import pytest
from fastapi.testclient import TestClient

# The API key the tests will authenticate with. config.py reads API_KEY from
# the environment, so we set it here before importing the app, guaranteeing
# the app and the tests agree on the same value.
os.environ.setdefault("API_KEY", "test-key")

from app.main import app  # noqa: E402  (import after env setup, intentionally)

API_KEY = os.environ["API_KEY"]


@pytest.fixture(scope="session")
def client():
    """A FastAPI TestClient bound to the real app."""
    return TestClient(app)


@pytest.fixture(scope="session")
def auth():
    """Headers carrying a valid API key, for authenticated requests."""
    return {"X-API-Key": API_KEY}
