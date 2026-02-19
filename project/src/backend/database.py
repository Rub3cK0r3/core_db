from sqlmodel import create_engine
import os

"""
The Database data should always
be loaded from your execution environment.
Please, bear that in mind.
"""

db_passwd = os.environ.get("DB_PASSWORD")
db_user = os.environ.get("DB_USER")
db_host = os.environ.get("DB_HOST")
db_name = os.environ.get("DB_NAME")

DATABASE_URL = f"postgresql://{db_user}:{db_passwd}@{db_host}:5432/{db_name}"
engine = create_engine(DATABASE_URL, echo=True)
