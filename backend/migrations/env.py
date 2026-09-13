from alembic import context
from sqlalchemy import create_engine, pool
from app.config import settings
from app.database import Base
from app import models, auth_models

target_metadata = Base.metadata


def run_migrations_online():
    connection = context.config.attributes.get("connection")
    if connection is not None:
        context.configure(connection=connection, target_metadata=target_metadata, compare_type=True)
        with context.begin_transaction():
            context.run_migrations()
        return
    engine = create_engine(settings.database_url, poolclass=pool.NullPool)
    with engine.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata, compare_type=True)
        with context.begin_transaction():
            context.run_migrations()
    engine.dispose()


if context.is_offline_mode():
    raise RuntimeError("Offline migrations are unsupported: adoption inspects the legacy schema")
run_migrations_online()
