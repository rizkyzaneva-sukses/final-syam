# Seed & Smoke-Test Scripts

Skrip ini mengisi data demo lewat **API publik** (bukan langsung ke database),
jadi setiap business rule di `workflow.py` ikut teruji. Semuanya **idempotent** —
aman dijalankan ulang, record yang sudah ada akan di-skip.

Selain mengisi data, skrip ini berfungsi sebagai **smoke test**: setiap respons
non-2xx dikumpulkan dan dilaporkan di akhir, tidak menghentikan eksekusi.

## Cara pakai

Jalankan berurutan:

```bash
python3 scripts/seed_demo.py        # customer, order, karyawan
python3 scripts/seed_flow.py        # business policy, quotation, sample, SPK
python3 scripts/seed_routed.py      # order dengan production_route lengkap
python3 scripts/seed_production.py  # BOM -> MR -> PO -> plan -> movement -> QC
python3 scripts/seed_finish.py      # packing -> gate -> kirim -> terima
python3 scripts/seed_closing.py     # closing CMO + CFO
```

Target server & password diatur di konstanta `BASE` dan `PASSWORD` di tiap file.

## Urutan gate yang wajib dipatuhi

Backend menolak lompatan tahap. Urutan yang benar:

```
business policy (CEO)
  -> order + artikel (production_route WAJIB diisi)
  -> quotation DRAFT -> APPROVED (CFO)
  -> invoice -> payment -> reconcile -> finance-gate APPROVE (CFO)
  -> BOM -> material request -> purchase order READY (CFO)
  -> production plan APPROVED (COO)
  -> SPK RELEASED (CMO)
  -> movement per proses -> QC final
  -> shipment: packing PACKED -> finance gate APPROVE (CFO) -> SHIPPED
  -> delivery confirmation (CMO) -> shipment otomatis DELIVERED
  -> closing: customer (CMO) + financial (CFO), terpisah
```

## Aturan yang mudah terlewat

**`production_route` tidak bisa diubah setelah order dibuat.**
Tidak ada endpoint update artikel. Order tanpa rute **tidak akan pernah** bisa
release SPK — satu-satunya jalan adalah membuat order baru. Format:
`Cutting > Sewing > QC`.

**Kuantitas berjenjang.** Material request harus ≥ (BOM qty_per_unit × qty
artikel), dan purchase order harus ≥ material request. Kalau kurang, SPK ditolak.

**Status `DELIVERED` tidak bisa di-PATCH manual.** Hanya berubah otomatis saat
delivery confirmation dibuat dengan status `CONFIRMED`.

**Closing butuh dua role berbeda.** `customer_close_status` hanya bisa diset
CMO_MANAGER, `financial_close_status` hanya CFO_MANAGER — segregation of duties.
`order_close_status` bersifat turunan, jangan dikirim manual.

**Sample Only tidak masuk produksi.** Order bertipe `SAMPLE_ONLY` ditolak di
tahap production plan.
