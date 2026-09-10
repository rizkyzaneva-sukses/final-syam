# BOS SYAMS — ALL-IN V0.2

Versi all-in MVP/developer foundation dari pembicaraan BOS Syams. **Ini aplikasi yang dapat dijalankan, bukan klaim bahwa seluruh detail bisnis sudah production-final.** Bagian yang belum ditetapkan tetap harus dikembangkan tanpa mengarang hard-coded rule.

## Stack
- React + Vite
- FastAPI + SQLAlchemy
- PostgreSQL 16
- JWT role-based login
- Docker Compose
- Nginx frontend proxy
- Caddy HTTPS untuk deployment production

## Area yang sudah disatukan
- Login multi-user / role
- Master Control
- Master Produksi / Morning Priority
- Process Movement / partial WIP
- WIP & Capacity / Forecast
- Shared Order Detail / multi-article
- CMO workspace foundation: Customer, Quotation, Sample/PPM, SPK, demand modules
- CFO foundation: Invoice, Payment, AR/AP, Purchasing, Shipment Finance Gate
- COO foundation: material request, production movement, QC, shipment
- CHRO foundation: Employee, Training, Performance, People Issue
- CEO foundation: Exception, Decision & Action Tracker
- Audit/config data models
- Separate Customer Closed / Financial Closed / Order Closed
- Mandatory backend guard: shipment with outstanding cannot be cleared without CEO approval

## Demo lokal
```bash
cp .env.example .env
docker compose up --build
```
Buka http://localhost:8080

Demo:
- iyan@syams.local / demo123
- cecep@syams.local / demo123
- deby@syams.local / demo123
- lutfi@syams.local / demo123
- siti@syams.local / demo123
- fahrul@syams.local / demo123
- iman@syams.local / demo123
- yuni@syams.local / demo123

## Menggabungkan modul satu-per-satu nanti
Semua modul berada dalam satu repository:
- model/table -> `backend/app/models.py`
- API -> `backend/app/routers/`
- screen -> `frontend/src/pages/`
- routing -> `frontend/src/main.jsx`
- menu role -> `frontend/src/components/Layout.jsx`

Kalau ada modul baru, jangan bikin aplikasi/database terpisah. Tambahkan model + API + page di folder tersebut lalu rebuild Docker.

## Production install
Lihat `INSTALL_SERVER.md`.

## Batas V0.2
Data model & endpoint utama tersedia, tetapi modul accounting double-entry penuh, payroll calculation final, bank reconciliation, tax, document PDF template final, dan formula KPI/SLA/TB yang masih CONFIGURABLE/TBD belum boleh dianggap production-final sampai aturan bisnisnya dikunci.
