import os
from flask import Flask
from playhouse.flask_utils import FlaskDB
from playhouse.postgres_ext import PostgresqlExtDatabase

db_host = os.getenv("DB_HOST")
db_port = os.getenv("DB_PORT")
db_user = os.getenv("DB_USER")
db_password = os.getenv("DB_PASSWORD")
db_name = os.getenv("DB_NAME")

supabase_database = PostgresqlExtDatabase(
    db_name,
    host=db_host,
    user=db_user,
    password=db_password,
    port=db_port,
)

app = Flask("tubolivarhoy")
app.config.from_object("tubolivarhoy")

db_wrapper = FlaskDB(app, supabase_database)
