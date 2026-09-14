"""Verify the migration chain on a disposable database."""
import os
import sqlite3
import subprocess
import sys
import tempfile
from contextlib import closing
from pathlib import Path


def test_fresh_database_migrates_to_head():
    backend = Path(__file__).resolve().parents[1]
    with tempfile.TemporaryDirectory() as directory:
        database = Path(directory) / "migration.sqlite"
        env = {**os.environ, "DATABASE_URL": f"sqlite:///{database.as_posix()}",
               "APP_ENV": "testing", "SEED_DEMO": "false"}
        result = subprocess.run([sys.executable, "-m", "alembic", "-c", str(backend / "alembic.ini"),
                                 "upgrade", "head"], cwd=backend, env=env, capture_output=True, text=True)
        assert result.returncode == 0, result.stdout + result.stderr
        with closing(sqlite3.connect(database)) as db:
            assert db.execute("SELECT version_num FROM alembic_version").fetchone()[0] == "0007_revision_proposals"
            names = {row[0] for row in db.execute("SELECT name FROM sqlite_master WHERE type='table'")}
            assert {"orders", "quotations", "bom_items", "material_consumptions", "production_cost_entries", "cost_reviews", "qc_records", "revision_proposals"} <= names
