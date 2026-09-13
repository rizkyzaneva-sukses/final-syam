from app.auth_models import AuthSession
from app.config import settings
from app.models import Role


def login(client, email, password):
    return client.post("/api/auth/login", json={"email": email, "password": password})


def test_login_sessions_are_revocable_and_password_change_invalidates_all(client, users):
    email = users[Role.CMO_MANAGER].email
    first = login(client, email, "ValidPass-2026!")
    assert first.status_code == 200
    first_token = first.json()["access_token"]
    first_headers = {"Authorization": f"Bearer {first_token}"}
    assert client.get("/api/auth/me", headers=first_headers).status_code == 200

    second = login(client, email, "ValidPass-2026!")
    assert second.status_code == 200
    second_headers = {"Authorization": f"Bearer {second.json()['access_token']}"}
    changed = client.post(
        "/api/auth/change-password",
        headers=second_headers,
        json={"current_password": "ValidPass-2026!", "new_password": "ReplacementPass-2026!"},
    )
    assert changed.status_code == 204
    assert client.get("/api/auth/me", headers=first_headers).status_code == 401
    assert client.get("/api/auth/me", headers=second_headers).status_code == 401

    replacement = login(client, email, "ReplacementPass-2026!")
    assert replacement.status_code == 200
    replacement_headers = {"Authorization": f"Bearer {replacement.json()['access_token']}"}
    assert client.post("/api/auth/logout", headers=replacement_headers).status_code == 204
    assert client.get("/api/auth/me", headers=replacement_headers).status_code == 401


def test_login_rate_limit_counts_failures_by_account_without_ip_trust(client, users, monkeypatch, db):
    monkeypatch.setattr(settings, "login_max_attempts", 2)
    email = users[Role.CFO_MANAGER].email
    assert login(client, email, "wrong-password").status_code == 401
    assert login(client, email, "wrong-password").status_code == 401
    locked = login(client, email, "ValidPass-2026!")
    assert locked.status_code == 429
    assert locked.headers["retry-after"] == str(settings.login_window_seconds)
    assert db.query(AuthSession).count() == 0


def test_password_length_is_bounded_before_bcrypt(client, users):
    response = login(client, users[Role.CEO].email, "x" * 73)
    assert response.status_code == 401
