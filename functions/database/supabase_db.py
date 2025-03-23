import os
from flask import g
from peewee import PostgresqlDatabase


class SupabaseDB:

    @staticmethod
    def get_connection() -> PostgresqlDatabase:
        if "db" not in g:
            db_host = os.getenv("DB_HOST")
            db_port = os.getenv("DB_PORT")
            db_user = os.getenv("DB_USER")
            db_password = os.getenv("DB_PASSWORD")
            db_name = os.getenv("DB_NAME")

            g.db = PostgresqlDatabase(
                db_name,
                host=db_host,
                user=db_user,
                password=db_password,
                port=db_port,
            )

        conn = g.db
        assert conn.connect(reuse_if_open=True)
        return conn

    @staticmethod
    def close_db(e=None) -> None:
        db: PostgresqlDatabase = g.pop("db", None)

        if db is not None:
            db.close()
