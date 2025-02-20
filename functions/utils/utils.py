import os

import google.auth
from firebase_functions.options import SupportedRegion
from flask import g
from google.auth.transport.requests import AuthorizedSession
from peewee import PostgresqlDatabase


def get_function_url(name: str, location: str = SupportedRegion.US_CENTRAL1) -> str:
    """Get the URL of a given v2 cloud function.

    Params:
        name: the function's name
        location: the function's location

    Returns: The URL of the function
    """
    credentials, project_id = google.auth.default(
        scopes=["https://www.googleapis.com/auth/cloud-platform"]
    )
    authed_session = AuthorizedSession(credentials)
    url = (
        "https://cloudfunctions.googleapis.com/v2beta/"
        + f"projects/{project_id}/locations/{location}/functions/{name}"
    )
    response = authed_session.get(url)
    data = response.json()
    function_url = data["serviceConfig"]["uri"]
    return function_url


def get_db() -> PostgresqlDatabase:
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

    return g.db


def close_db(e=None) -> None:
    db = g.pop("db", None)

    if db is not None:
        db.close()
