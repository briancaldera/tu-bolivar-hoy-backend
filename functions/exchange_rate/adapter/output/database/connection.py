import os
from flask import Flask
from playhouse.flask_utils import FlaskDB
from playhouse.postgres_ext import PostgresqlExtDatabase

_db_host = os.getenv("DB_HOST")
_db_port = os.getenv("DB_PORT")
_db_user = os.getenv("DB_USER")
_db_password = os.getenv("DB_PASSWORD")
_db_name = os.getenv("DB_NAME")

_supabase_database = PostgresqlExtDatabase(
    _db_name,
    host=_db_host,
    user=_db_user,
    password=_db_password,
    port=_db_port,
)

app = Flask("tubolivarhoy")
app.config.from_object("tubolivarhoy")

db_wrapper = FlaskDB(app, _supabase_database)
