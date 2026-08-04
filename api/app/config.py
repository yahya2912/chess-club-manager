import os
from dotenv import load_dotenv

load_dotenv()

POSTGRES_USER = os.environ["POSTGRES_USER"]
POSTGRES_PASSWORD = os.environ["POSTGRES_PASSWORD"]
POSTGRES_DB = os.environ["POSTGRES_DB"]
POSTGRES_PORT = os.environ.get("POSTGRES_PORT", "5432")
POSTGRES_HOST = os.environ.get("POSTGRES_HOST", "localhost")

API_KEY = os.environ["API_KEY"]
