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
- 2026-10-13: 6 revisi (semua lolos testing 100%):
  1. Dashboard Internal "Ringkasan Per Hari" menampilkan histori tanggal sebelumnya + pagination 5 baris/halaman (query terpisah date_from=2000-01-01)
  2. Pembelian: Enter di Nomor Seri -> cek duplikat (endpoint /internal/pembelian/seri-check) -> pop-up "sudah pernah diinput" + kolom dikosongkan
  3. Penjualan: Enter di Nomor Seri yang sudah terjual -> pop-up "sudah terjual" + kolom dikosongkan
  4. Teks "lembar" (satuan glangse) diganti "koli" (assistant.py; UI lain sudah memakai "koli")
  5. Out & Revisi: tambah kolom search Nomor Seri, Bandul, Nomor Jadi
  6. Penjualan: autosave draft ke localStorage (key twms-jual-draft-<wh>) agar input tidak hilang saat refresh/back; draft dihapus saat Simpan/Kembali

## Catatan Bug "preview refresh sendiri"
- Tidak ditemukan kode yang memaksa reload (hanya logout yang redirect). Refresh acak di preview berasal dari Vite HMR/overlay (artefak lingkungan preview), bukan bug aplikasi. Mitigasi kehilangan data: autosave draft Penjualan (revisi #6).

## Backlog
- P1: Uji fitur Asisten AI (butuh balance Universal Key), upload foto KTP (object storage)
- P2: (opsional) endpoint server-side "N hari terakhir" untuk histori Dashboard bila data pembelian sangat besar
