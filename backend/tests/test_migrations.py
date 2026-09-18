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
            assert db.execute("SELECT version_num FROM alembic_version").fetchone()[0] == "0008_revision_status"
            names = {row[0] for row in db.execute("SELECT name FROM sqlite_master WHERE type='table'")}
            assert {"orders", "quotations", "bom_items", "material_consumptions", "production_cost_entries", "cost_reviews", "qc_records", "revision_proposals", "revision_status_events"} <= names


def test_existing_revisions_and_images_survive_status_migration():
    backend = Path(__file__).resolve().parents[1]
    with tempfile.TemporaryDirectory() as directory:
        database = Path(directory) / "existing.sqlite"
        env = {**os.environ, "DATABASE_URL": f"sqlite:///{database.as_posix()}",
               "APP_ENV": "testing", "SEED_DEMO": "false"}
        command = [sys.executable, "-m", "alembic", "-c", str(backend / "alembic.ini"), "upgrade"]
        before = subprocess.run(command + ["0007_revision_proposals"], cwd=backend, env=env,
                                capture_output=True, text=True)
        assert before.returncode == 0, before.stdout + before.stderr
        image = b"\x89PNG\r\n\x1a\nexisting-image"
        with closing(sqlite3.connect(database)) as db:
            db.execute("""INSERT INTO users (id, name, email, password_hash, role, is_active, created_at)
                       VALUES (1, 'Deby', 'deby@example.com', 'hash', 'CMO_SUPPORT', 1, '2026-09-16 00:00:00')""")
            db.execute("""INSERT INTO revision_proposals
                       (id, module_name, bug_description, expected_behavior, image_data, image_mime, reported_by_id, created_at)
                       VALUES (1, 'CMO-023 — CMO Support — Delivery', 'Bug asli', 'Hasil asli', ?, 'image/png', 1, '2026-09-16 00:00:00')""", (image,))
            db.commit()
        after = subprocess.run(command + ["head"], cwd=backend, env=env,
                               capture_output=True, text=True)
        assert after.returncode == 0, after.stdout + after.stderr
        with closing(sqlite3.connect(database)) as db:
            row = db.execute("""SELECT module_name, bug_description, expected_behavior, image_data,
                              status, owner_role FROM revision_proposals WHERE id = 1""").fetchone()
            assert row == ("CMO-023 — CMO Support — Delivery", "Bug asli", "Hasil asli",
                           image, "REVISI", "CMO_SUPPORT")
