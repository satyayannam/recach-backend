from logging.config import fileConfig
import os
import sys

from alembic import context

# Alembic Config object
config = context.config

# Logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Ensure backend/ is on sys.path so "app.*" imports always work
BASE_DIR = os.path.dirname(os.path.dirname(__file__))  # backend/
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

# Import Base + models so metadata is fully populated
from app.db.base import Base  # noqa: E402
import app.db.models  # noqa: F401, E402  (must import all models: users, user_profiles, etc.)

# If you want, you can also import specific ones explicitly (optional):
# from app.db.user_profile import UserProfile  # noqa: F401, E402

# Use the same engine your app uses
from app.db.session import engine  # noqa: E402

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations in offline mode (no DB connection)."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        compare_server_default=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in online mode (with DB connection)."""
    with engine.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            compare_server_default=True,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
