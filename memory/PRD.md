# TWMS — Tobacco Warehouse Management System (Stok Gudang Tembakau)

## Original Problem Statement
Workspace baru: import project dari GitHub repository https://github.com/ardilloz/TWMS-pindah (branch main), setup dan install semua dependencies.

## Arsitektur
- Backend: FastAPI (port 8001), Motor/MongoDB, session-cookie auth (bcrypt), routers: auth, users, master, transactions, report, admin, assistant (AI via EMERGENT_LLM_KEY), internal
- Frontend: Vite + React 19 + TypeScript + Tailwind 4 (port 3000, proxy /api → 8001)
- Storage: Emergent object storage (foto KTP) via EMERGENT_LLM_KEY
- DB: MongoDB lokal, DB_NAME=test_database

## Yang Sudah Diimplementasikan
- 2026-10-13: Import repo TWMS-pindah@main ke /app (rsync, .git & .emergent platform dipertahankan)
- 2026-10-13: pip install backend requirements, yarn install frontend
- 2026-10-13: backend/.env berisi MONGO_URL, DB_NAME, CORS_ORIGINS, EMERGENT_LLM_KEY
- 2026-10-13: Seed admin (admin/admin123), supervisor backend+frontend RUNNING, login & dashboard terverifikasi end-to-end via browser

## Backlog
- P0: —
- P1: Uji fitur Asisten AI (butuh balance Universal Key), uji upload foto (object storage)
- P2: Uji ekspor Excel/PDF laporan, fitur internal (pembelian/penjualan/busai)
