from sqlmodel import create_engine
from dotenv import load_dotenv
from urllib.parse import quote_plus
import os

"""
The Database data should always
be loaded from your execution environment.
Please, bear that in mind.
"""

# I load the .env used in the docker compose deployment..
load_dotenv(dotenv_path='../../db/.env')

db_user = os.environ.get("POSTGRES_USER", "postgres")
db_passwd = quote_plus(os.environ.get("POSTGRES_PASSWORD", ""))
db_host = os.environ.get("DB_HOST", "127.0.0.1")
db_name = os.environ.get("POSTGRES_DB", "postgres")

DATABASE_URL = f"postgresql://{db_user}:{db_passwd}@{db_host}:5432/{db_name}"
engine = create_engine(DATABASE_URL, echo=True)
