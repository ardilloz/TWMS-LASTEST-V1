"""iter11: verify PUT /api/meta/theme persists to user account and GET /auth/me returns it."""
import httpx
import pytest

import os
BACKEND_URL = os.environ.get("BACKEND_URL", "http://localhost:8001")
API_URL = f"{BACKEND_URL}/api"


def _login(username="admin", password="admin123"):
    c = httpx.Client(base_url=API_URL, timeout=30.0)
    r = c.post("/auth/login", json={"username": username, "password": password})
    assert r.status_code == 200, f"login failed: {r.status_code} {r.text}"
    return c


def test_put_theme_requires_auth():
    with httpx.Client(base_url=API_URL, timeout=30.0) as c:
        r = c.put("/meta/theme", json={"mode": "dark", "accent": "ocean"})
        assert r.status_code in (401, 403)


def test_put_theme_round_trip_dark_ocean():
    c = _login()
    try:
        r = c.put("/meta/theme", json={"mode": "dark", "accent": "ocean"})
        assert r.status_code == 200, r.text
        assert r.json() == {"ok": True}

        me = c.get("/auth/me")
        assert me.status_code == 200
        data = me.json()
        assert data.get("theme") == {"mode": "dark", "accent": "ocean"}
    finally:
        c.close()


def test_put_theme_update_light_emerald():
    c = _login()
    try:
        r = c.put("/meta/theme", json={"mode": "light", "accent": "emerald"})
        assert r.status_code == 200
        me = c.get("/auth/me").json()
        assert me.get("theme") == {"mode": "light", "accent": "emerald"}
    finally:
        c.close()


def test_put_theme_invalid_mode_rejected():
    c = _login()
    try:
        r = c.put("/meta/theme", json={"mode": "neon", "accent": "ocean"})
        assert r.status_code == 422
    finally:
        c.close()


def test_theme_persists_across_login_sessions():
    """Set theme in session A, log in fresh in session B, confirm /auth/me shows same theme."""
    a = _login()
    try:
        a.put("/meta/theme", json={"mode": "dark", "accent": "plum"})
    finally:
        a.close()

    b = _login()
    try:
        me = b.get("/auth/me").json()
        assert me.get("theme") == {"mode": "dark", "accent": "plum"}
    finally:
        b.close()


def test_cleanup_reset_admin_theme_to_default():
    """Reset admin's theme to a safe default so subsequent runs/users start light."""
    c = _login()
    try:
        r = c.put("/meta/theme", json={"mode": "light", "accent": "tobacco"})
        assert r.status_code == 200
        me = c.get("/auth/me").json()
        assert me.get("theme") == {"mode": "light", "accent": "tobacco"}
    finally:
        c.close()
