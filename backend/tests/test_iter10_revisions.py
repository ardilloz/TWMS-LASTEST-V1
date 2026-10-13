"""Iteration 10 revisions tests:
- GET /api/internal/penjualan/jadi-check (exists true/false, exclude_id, case-insensitive)
- GET /api/meta/nav-order + PUT (admin-only)
- assistant SYSTEM_PROMPT names Dave
"""
import os
import uuid

import httpx
import pytest

BASE = os.environ.get("BACKEND_URL", "http://localhost:8001")
API = f"{BASE}/api"


@pytest.fixture(scope="module")
def admin():
    c = httpx.Client(base_url=API, timeout=30.0)
    r = c.post("/auth/login", json={"username": "admin", "password": "admin123"})
    assert r.status_code == 200, r.text
    yield c
    c.close()


@pytest.fixture(scope="module")
def WH(admin):
    r = admin.get("/warehouses")
    assert r.status_code == 200
    whs = r.json()
    pjm = next((w for w in whs if w["name"] == "PJM"), whs[0] if whs else None)
    assert pjm, "No warehouse available"
    return pjm["id"]


@pytest.fixture(scope="module")
def anon():
    with httpx.Client(base_url=API, timeout=30.0) as c:
        yield c


# ----- jadi-check -----
class TestJadiCheck:
    def test_empty_jadi_false(self, admin, WH):
        r = admin.get("/internal/penjualan/jadi-check", params={"wh": WH, "jadi": ""})
        assert r.status_code == 200
        assert r.json() == {"exists": False}

    def test_random_not_exists(self, admin, WH):
        rnd = f"J-NOPE-{uuid.uuid4().hex[:8].upper()}"
        r = admin.get("/internal/penjualan/jadi-check", params={"wh": WH, "jadi": rnd})
        assert r.status_code == 200
        assert r.json() == {"exists": False}

    def test_case_insensitive_matches_existing(self, admin, WH):
        # Find an existing nomor_jadi in penjualan or out_records
        r = admin.get("/internal/penjualan", params={"wh": WH})
        existing_jadi = None
        if r.status_code == 200:
            for p in r.json():
                for it in (p.get("items") or []):
                    if it.get("nomor_jadi"):
                        existing_jadi = it["nomor_jadi"]
                        break
                if existing_jadi:
                    break
        if not existing_jadi:
            pytest.skip("No existing nomor_jadi in PJM to test exists=true path")
        # upper/lower variants should both hit
        for variant in (existing_jadi.upper(), existing_jadi.lower()):
            r = admin.get(
                "/internal/penjualan/jadi-check",
                params={"wh": WH, "jadi": variant},
            )
            assert r.status_code == 200, r.text
            assert r.json().get("exists") is True, f"variant {variant} should exist"

    def test_requires_auth(self, anon, WH):
        r = anon.get("/internal/penjualan/jadi-check", params={"wh": WH, "jadi": "X"})
        assert r.status_code in (401, 403)


# ----- nav-order -----
class TestNavOrder:
    def test_get_anon_ok_or_auth(self, anon, admin):
        # Spec: GET returns stored global order (or null). Likely requires auth (router dep get_current_user).
        r_anon = anon.get("/meta/nav-order")
        r_admin = admin.get("/meta/nav-order")
        assert r_admin.status_code == 200
        # admin should get null or a dict/list
        v = r_admin.json()
        assert v is None or isinstance(v, (dict, list))
        # anon either 401 or 200 null — don't fail if auth required
        assert r_anon.status_code in (200, 401, 403)

    def test_put_requires_admin_anon_blocked(self, anon):
        r = anon.put("/meta/nav-order", json={"order": ["a", "b"]})
        assert r.status_code in (401, 403), r.text

    def test_admin_put_and_get_roundtrip(self, admin):
        payload = {"order": ["dashboard", "pembelian", "penjualan"], "test_marker": uuid.uuid4().hex}
        r = admin.put("/meta/nav-order", json=payload)
        assert r.status_code == 200, r.text
        assert r.json().get("ok") is True
        r2 = admin.get("/meta/nav-order")
        assert r2.status_code == 200
        got = r2.json()
        assert got == payload, got

    def test_put_non_admin_blocked(self, admin):
        # Create a disposable staff user via /auth/users-ish? Use kelola-pengguna endpoint if available.
        # Try the common endpoint; skip if we can't create.
        username = f"ztest_staff_{uuid.uuid4().hex[:6]}"
        created = None
        for path, body in [
            ("/users", {"username": username, "password": "pw123456", "role": "staff", "name": "Z Staff", "permissions": [], "warehouses": []}),
            ("/auth/users", {"username": username, "password": "pw123456", "role": "staff", "name": "Z Staff", "permissions": [], "warehouses": []}),
        ]:
            r = admin.post(path, json=body)
            if r.status_code in (200, 201):
                created = (path, r.json())
                break
        if not created:
            pytest.skip("Could not create staff user to validate non-admin PUT block")
        try:
            with httpx.Client(base_url=API, timeout=30.0) as staff:
                r = staff.post("/auth/login", json={"username": username, "password": "pw123456"})
                assert r.status_code == 200, r.text
                r2 = staff.put("/meta/nav-order", json={"order": ["x"]})
                assert r2.status_code in (401, 403), f"non-admin should be blocked, got {r2.status_code}"
        finally:
            uid = created[1].get("id")
            if uid:
                admin.delete(f"{created[0]}/{uid}")


# ----- assistant Dave -----
class TestAssistantDave:
    def test_system_prompt_names_dave(self):
        import pathlib
        p = pathlib.Path("/app/backend/routers/assistant.py").read_text()
        assert "Dave" in p
        assert "Namamu adalah Dave" in p or "sebagai Dave" in p
