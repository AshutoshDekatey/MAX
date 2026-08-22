"""Explicit local helper; requires a MAX_DATABASE_URL supplied by Max."""

import os

from project_max.persistence.postgres import bootstrap_database

if __name__ == "__main__":
    database_url = os.getenv("MAX_DATABASE_URL")
    if not database_url:
        raise SystemExit("MAX_DATABASE_URL is not set. See .env.example and docs/source-systems/postgresql.md")
    bootstrap_database(database_url)
    print("V0 PostgreSQL schemas created.")

