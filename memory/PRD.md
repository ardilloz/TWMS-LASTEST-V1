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
- 2026-10-13: 6 revisi lanjutan (semua lolos testing 100% — iteration_4.json):
  1. Penjualan: Enter nomor seri sudah dijual -> pop-up "sudah dijual" + kolom dikosongkan
  2. Penjualan: nomor jadi (manual/otomatis) sudah dipakai -> pop-up "nomor jadi sudah dijual" + dikosongkan (endpoint /internal/penjualan/jadi-check)
  3. Menu "Asisten AI" -> "Tanya Dave"; AI bernama Dave (assistant.py SYSTEM_PROMPT)
  4. Pembelian: Enter nama bandul tak terdaftar -> pop-up "nama bandul belum terdaftar"
  5. Pengaturan tampilan per-pengguna (tombol palet di samping nama): mode Terang/Gelap + 6 warna aksen, tersimpan di localStorage (lib/theme.ts, ThemeSettings.tsx)
  6. Admin utama drag-reorder menu ("Atur Urutan Menu"), urutan global berlaku semua pengguna (endpoint /meta/nav-order, lib/navOrder.ts)

- P1: Uji fitur Asisten AI (Dave) end-to-end (butuh balance Universal Key), upload foto KTP

- 2026-10-13: 2 revisi tampilan (lolos testing 100% — iteration_5.json):
  1. Simpan Tema ke Akun: preferensi mode & warna disimpan di akun pengguna (PUT /meta/theme, dikembalikan via /auth/me) — tema ikut saat login di perangkat lain (lib/theme.ts pushTheme, ThemeSettings accountTheme)
  2. Mode Gelap Penuh: blok CSS kompatibilitas dark mode di index.css memetakan util bg-white/amber/emerald/indigo/sky/red ke token tema; aksen punya varian terang & gelap (primaryDark) agar kontras baik. Terverifikasi kohesif di Dashboard, Internal, Pembelian, Penjualan, Harga, Gudang, Tanya Dave
