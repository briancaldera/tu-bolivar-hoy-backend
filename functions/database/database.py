import os
from flask import g
from peewee import PostgresqlDatabase, Database as PeeweeDatabase, SqliteDatabase


class Database:
    @staticmethod
    def get_connection() -> PeeweeDatabase:
        if "db" not in g:

            if os.getenv("APP_MODE") == "dev":

                db_file = os.getenv("DB_FILE")
                g.db = SqliteDatabase(db_file)

            else:

                db_name = os.getenv("DB_NAME")
                db_host = os.getenv("DB_HOST")
                db_port = os.getenv("DB_PORT")
                db_user = os.getenv("DB_USER")
                db_password = os.getenv("DB_PASSWORD")

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
    def close_db(_=None) -> None:
        db: PeeweeDatabase = g.pop("db", None)

        if db is not None:
            db.close()
