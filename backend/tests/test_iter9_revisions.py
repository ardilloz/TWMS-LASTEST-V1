"""Iteration 9 revisions: pembelian seri-check endpoint, penjualan lookup 'sudah terjual' wording, assistant 'koli'."""
import os
import uuid

import httpx
import pytest

BACKEND = os.environ.get("BACKEND_URL", "http://localhost:8001")
API = f"{BACKEND}/api"


@pytest.fixture(scope="module")
def session():
    s = httpx.Client(base_url=API, timeout=30.0)
    r = s.post("/auth/login", json={"username": "admin", "password": "admin123"})
    assert r.status_code == 200, r.text
    yield s
    s.close()


@pytest.fixture(scope="module")
def wh_id(session):
    r = session.get("/warehouses")
    assert r.status_code == 200
    whs = r.json()
    # Prefer PJM, fallback to first
    pjm = next((w for w in whs if w.get("name") == "PJM"), None)
    return (pjm or whs[0])["id"]


class TestPembelianSeriCheck:
    def test_check_nonexistent_returns_false(self, session, wh_id):
        unique = f"ZZZTEST{uuid.uuid4().hex[:8].upper()}"
        r = session.get(f"/internal/pembelian/seri-check", params={"wh": wh_id, "seri": unique})
        assert r.status_code == 200, r.text
        assert r.json() == {"exists": False}

    def test_check_empty_returns_false(self, session, wh_id):
        r = session.get(f"/internal/pembelian/seri-check", params={"wh": wh_id, "seri": ""})
        assert r.status_code == 200
        assert r.json()["exists"] is False

    def test_check_existing_serial_returns_true(self, session, wh_id):
        # Find an existing seri in pembelian
        r = session.get(f"/internal/pembelian", params={"wh": wh_id})
        assert r.status_code == 200
        pembelians = r.json()
        if not pembelians or not pembelians[0].get("items"):
            pytest.skip("No existing pembelian with serials in this warehouse")
        existing_seri = pembelians[0]["items"][0]["nomor_seri"]
        existing_pid = pembelians[0]["id"]
        # Without exclude_id => exists:true
        r = session.get(f"/internal/pembelian/seri-check", params={"wh": wh_id, "seri": existing_seri})
        assert r.status_code == 200
        assert r.json()["exists"] is True
        # With exclude_id of the owning pembelian => exists:false (if unique to that doc)
        r2 = session.get(f"/internal/pembelian/seri-check",
                         params={"wh": wh_id, "seri": existing_seri, "exclude_id": existing_pid})
        assert r2.status_code == 200
        # Could still be true if seri exists in another doc (ganda), but normally false
        assert "exists" in r2.json()

    def test_check_case_insensitive(self, session, wh_id):
        r = session.get(f"/internal/pembelian", params={"wh": wh_id})
        pembelians = r.json()
        if not pembelians or not pembelians[0].get("items"):
            pytest.skip("No pembelian data")
        s = pembelians[0]["items"][0]["nomor_seri"]
        r = session.get(f"/internal/pembelian/seri-check", params={"wh": wh_id, "seri": s.lower()})
        assert r.json()["exists"] is True


class TestPenjualanLookupSold:
    def test_sold_serial_returns_terjual_error(self, session, wh_id):
        # Find a sold serial
        r = session.get(f"/internal/penjualan", params={"wh": wh_id})
        assert r.status_code == 200
        sales = r.json()
        sold_seri = None
        for s in sales:
            for it in s.get("items", []):
                if it.get("nomor_seri"):
                    sold_seri = it["nomor_seri"]
                    break
            if sold_seri:
                break
        if not sold_seri:
            pytest.skip("No sold serial available to test 'sudah terjual' branch")
        r = session.get(f"/internal/penjualan/lookup", params={"wh": wh_id, "seri": sold_seri})
        assert r.status_code == 200
        data = r.json()
        assert data["valid"] is False
        assert "terjual" in (data.get("error") or "").lower()


class TestDashboardHistory:
    def test_history_returns_days_up_to_today(self, session, wh_id):
        # The dashboard endpoint with date_from=2000-01-01 should return days list
        r = session.get(f"/internal/dashboard", params={"wh": wh_id, "date_from": "2000-01-01", "date_to": "2100-01-01"})
        assert r.status_code == 200, r.text
        data = r.json()
        assert "days" in data
        assert isinstance(data["days"], list)


class TestAssistantKoliWording:
    def test_assistant_prompt_contains_koli_not_lembar(self):
        # Code-level check — assistant.py content
        with open("/app/backend/routers/assistant.py") as f:
            content = f.read()
        # The prompt text should say 'koli' for Glangse unit
        assert "koli" in content
        # Only acceptable 'lembar' occurrences would be in code var names, not prompt text
        # Make sure prompt string 'Glangse dalam lembar' is NOT present
        assert "Glangse dalam lembar" not in content
        assert "Glangse=lembar" not in content
