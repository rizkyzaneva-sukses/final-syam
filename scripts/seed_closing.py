#!/usr/bin/env python3
"""Close the routed order with proper segregation of duties.

workflow.py:505 requires customer_close_status to be set by CMO_MANAGER and
financial_close_status by CFO_MANAGER, so closing needs two separate calls from
two different accounts. order_close_status is derived, never sent.
"""
import json
import ssl
import urllib.error
import urllib.request
from datetime import date

BASE = "https://client-bos-syam-fix.zvusml.easypanel.host"
PASSWORD = "demo123456789"
CTX = ssl.create_default_context()
CTX.check_hostname = False
CTX.verify_mode = ssl.CERT_NONE

TOKENS = {}
PROBLEMS = []
today = date.today()
ART = "ROUTED-TEE-01"


def login(account):
    if account not in TOKENS:
        body = json.dumps({"email": f"{account}@syams.local", "password": PASSWORD}).encode()
        req = urllib.request.Request(f"{BASE}/api/auth/login", data=body,
                                     headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, context=CTX) as r:
            TOKENS[account] = json.loads(r.read())["access_token"]
    return TOKENS[account]


def call(account, method, path, payload=None):
    data = json.dumps(payload).encode() if payload is not None else None
    req = urllib.request.Request(f"{BASE}/api{path}", data=data, method=method,
                                 headers={"Content-Type": "application/json",
                                          "Authorization": f"Bearer {login(account)}"})
    try:
        with urllib.request.urlopen(req, context=CTX) as r:
            raw = r.read()
            return r.status, (json.loads(raw) if raw else None)
    except urllib.error.HTTPError as e:
        raw = e.read()
        try:
            return e.code, json.loads(raw)
        except Exception:
            return e.code, raw.decode()[:300]


def step(label, account, method, path, payload=None, ok=(200, 201, 204)):
    status, body = call(account, method, path, payload)
    if status in ok:
        print(f"  + {label}")
        return body
    detail = body.get("detail") if isinstance(body, dict) else body
    print(f"  ! {label} -> HTTP {status}: {detail}")
    PROBLEMS.append((label, f"{method} {path}", status, detail))
    return None


print("=" * 64)
print("ORDER CLOSING — CMO tutup sisi customer, CFO tutup sisi finansial")
print("=" * 64)

_, orders = call("cmo.manager", "GET", "/orders")
order = next((o for o in (orders or [])
              if any(a.get("article_code") == ART for a in (o.get("articles") or []))), None)
if not order:
    raise SystemExit("Order ROUTED tidak ditemukan")
oid, order_id = order["id"], order["order_id"]
print(f"\norder {order_id} (id={oid})")

# ── 1. CMO membuat record closing + menutup sisi customer ───────────────────
print("\n1) CMO: buat closing + customer_close_status=CLOSED")
status, closing = call("cmo.manager", "GET", f"/coo/order-closing/{oid}")
if status == 200 and closing:
    print(f"  = closing sudah ada (customer={closing.get('customer_close_status')} "
          f"financial={closing.get('financial_close_status')})")
else:
    closing = step("Closing (customer CLOSED, financial OPEN)", "cmo.manager", "POST",
                   f"/coo/order-closing/{oid}",
                   {"order_fk": oid, "customer_close_status": "CLOSED",
                    "financial_close_status": "OPEN",
                    "notes": "Pengiriman dikonfirmasi customer"})

# ── 2. CFO menutup sisi finansial ───────────────────────────────────────────
print("\n2) CFO: financial_close_status=CLOSED")
status, closing = call("cfo.manager", "GET", f"/coo/order-closing/{oid}")
if status == 200 and closing and closing.get("financial_close_status") == "CLOSED":
    print("  = financial sudah CLOSED")
else:
    step("Financial CLOSED", "cfo.manager", "PATCH", f"/coo/order-closing/{oid}",
         {"financial_close_status": "CLOSED",
          "notes": "Invoice lunas dan terekonsiliasi"})

# ── 3. Hasil ────────────────────────────────────────────────────────────────
print("\n3) Hasil closing")
status, closing = call("ceo", "GET", f"/coo/order-closing/{oid}")
if status == 200 and closing:
    for k in ("customer_close_status", "financial_close_status",
              "order_close_status", "close_date", "closed_by"):
        print(f"  {k:24s}: {closing.get(k)}")
else:
    print(f"  ! HTTP {status}: {closing}")

print("\n4) Flow final")
status, flow = call("ceo", "GET", f"/orders/{order_id}/flow")
if status == 200 and isinstance(flow, dict):
    print(f"  current_step: {flow.get('current_step')}")
    for s in (flow.get("next_steps") or []):
        print(f"    [{'OK  ' if s.get('can_advance') else 'BLOK'}] {s.get('step')}: {s.get('reason') or 'siap'}")

print("\n5) Status order")
status, o = call("ceo", "GET", f"/orders/{order_id}")
if status == 200 and o:
    for k in ("overall_status", "shipment_status", "customer_close_status",
              "financial_close_status", "flow_step"):
        print(f"  {k:24s}: {o.get(k)}")

print("\n" + "=" * 64)
if PROBLEMS:
    print(f"MASALAH: {len(PROBLEMS)}")
    for label, endpoint, st, detail in PROBLEMS:
        print(f"\n  [{st}] {label}\n    {endpoint}\n    {detail}")
else:
    print("ORDER BERHASIL DITUTUP")
print("=" * 64)
