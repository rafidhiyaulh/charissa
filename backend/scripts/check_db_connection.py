import sqlalchemy
from dotenv import load_dotenv
import os

load_dotenv()

from charissa.data.postgres_source import _with_psycopg_driver

engine = sqlalchemy.create_engine(_with_psycopg_driver(os.environ["DATABASE_URL"]))
with engine.connect() as conn:
    conn.execute(sqlalchemy.text("SELECT 1"))
    print("connected ok")
engine.dispose()
