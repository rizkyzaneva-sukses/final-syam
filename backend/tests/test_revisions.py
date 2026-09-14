"""Revision proposals are shared across roles and screenshots stay authenticated."""
import base64


PNG = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAusB9Y9vWAAAAABJRU5ErkJggg=="
)


def test_all_users_can_submit_and_read_with_reporter_attribution(client, headers, users):
    first = client.post("/api/revisions", headers=headers("HR_SUPPORT"), data={
        "module_name": "  Training  ", "bug_description": "  Tombol simpan gagal  ",
        "expected_behavior": "  Data tersimpan  ", "reported_by_id": str(users[next(iter(users))].id),
    })
    assert first.status_code == 201, first.text
    assert first.json()["reported_by_name"] == "HR_SUPPORT"
    assert first.json()["module_name"] == "Training"
    assert first.json()["has_image"] is False

    second = client.post("/api/revisions", headers=headers("PRODUCTION_PIC"), data={
        "module_name": "Production Queue", "bug_description": "Gambar hilang",
        "expected_behavior": "Gambar tampil",
    }, files={"image": ("screenshot.png", PNG, "image/png")})
    assert second.status_code == 201, second.text
    assert second.json()["has_image"] is True

    listed = client.get("/api/revisions", headers=headers("CEO"))
    assert listed.status_code == 200
    assert [item["module_name"] for item in listed.json()] == ["Production Queue", "Training"]
    assert [item["reported_by_name"] for item in listed.json()] == ["PRODUCTION_PIC", "HR_SUPPORT"]
    image = client.get(f"/api/revisions/{second.json()['id']}/image", headers=headers("CMO_SUPPORT"))
    assert image.status_code == 200
    assert image.headers["content-type"] == "image/png"
    assert image.content == PNG


def test_revision_requires_login_and_rejects_invalid_inputs(client, headers):
    payload = {"module_name": "QC", "bug_description": "Gagal", "expected_behavior": "Berhasil"}
    assert client.get("/api/revisions").status_code == 401
    assert client.post("/api/revisions", data=payload).status_code == 401
    assert client.post("/api/revisions", headers=headers("CEO"), data={**payload, "bug_description": "   "}).status_code == 422
    bad_image = client.post("/api/revisions", headers=headers("CEO"), data=payload,
                            files={"image": ("fake.png", b"not an image", "image/png")})
    assert bad_image.status_code == 415
    too_large = client.post("/api/revisions", headers=headers("CEO"), data=payload,
                            files={"image": ("large.png", PNG + b"x" * (5 * 1024 * 1024), "image/png")})
    assert too_large.status_code == 413
    assert client.get("/api/revisions", headers=headers("CEO")).json() == []
