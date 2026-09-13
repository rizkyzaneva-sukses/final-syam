from datetime import date, timedelta
from app import models as m


def order(db, number="SO-001", **kwargs):
    row = m.Order(order_id=number, buyer="Buyer", order_type=m.OrderType.REPEAT_PRODUCTION, **kwargs)
    db.add(row)
    db.commit()
    return row


def test_dashboard_role_scope(client, headers):
    assert client.get("/api/dashboard/CFO").status_code == 401
    assert client.get("/api/dashboard/CFO", headers=headers("HR_SUPPORT")).status_code == 403
    assert client.get("/api/dashboard/CHRO", headers=headers("PRINTING_PIC")).status_code == 403
    assert client.get("/api/dashboard/CFO", headers=headers("CFO_MANAGER")).status_code == 200
    assert client.get("/api/dashboard/CEO", headers=headers("CMO_MANAGER")).status_code == 403


def test_forecast_unknown_and_zero_buffer_consistent(db, client, headers):
    today = date.today()
    order(db, buyer_deadline=today, projected_shipment=today, buffer_days=-99)
    order(db, "SO-002", buyer_deadline=today + timedelta(days=2))
    auth = headers("COO_MANAGER")
    rows = client.get("/api/master/forecast", headers=auth).json()
    assert rows[0]["buffer_days"] == 0
    assert rows[0]["status"] == "ON_TRACK"
    assert rows[1]["status"] == "UNKNOWN"
    stats = client.get("/api/master/summary", headers=auth).json()
    assert stats["on_track"] == 1
    assert stats["unknown_forecast"] == 1


def test_priority_uses_severity_then_due_date(db, client, headers):
    db.add_all([m.ExceptionItem(title="Yellow first", category="Test", severity="YELLOW", due_date=date.today()),
                m.ExceptionItem(title="Red first", category="Test", severity="RED", due_date=date.today() + timedelta(days=1)),
                m.ExceptionItem(title="Resolved", category="Test", severity="RED", status="RESOLVED")])
    db.commit()
    rows = client.get("/api/master/morning-priority", headers=headers("CEO")).json()
    assert [r["title"] for r in rows] == ["Red first", "Yellow first"]


def test_capacity_uses_actual_wip_and_explicit_freshness(db, client, headers):
    o = order(db)
    a = m.Article(order_fk=o.id, article_code="A", qty=100)
    db.add(a)
    db.flush()
    db.add_all([m.ProductionMovement(article_id=a.id, process="Cutting", qty_in=100, qty_done=70, qty_reject=5),
                m.CapacitySnapshot(process="Cutting", snapshot_date=date.today(), capacity=100, planned_load=150, current_wip=999),
                m.CapacitySnapshot(process="Cutting", snapshot_date=date.today() - timedelta(days=1), capacity=10, planned_load=50),
                m.CapacitySnapshot(process="Sewing", snapshot_date=date.today() - timedelta(days=1), capacity=100, planned_load=50)])
    db.commit()
    auth = headers("COO_MANAGER")
    rows = client.get("/api/master/wip-capacity", headers=auth).json()
    cutting, sewing = rows
    assert cutting["current_wip"] == 25
    assert cutting["capacity"] == 100
    assert cutting["utilization"] == 150
    assert not cutting["is_stale"]
    assert sewing["is_stale"] and sewing["utilization"] is None
    movement = client.get("/api/master/process-movement/SO-001", headers=auth).json()
    assert movement[0]["wip"] == cutting["current_wip"]


def test_projection_and_capacity_updates_require_coo_and_are_audited(db, client, headers):
    order(db, buyer_deadline=date.today() + timedelta(days=4))
    data = {"projected_shipment": (date.today() + timedelta(days=2)).isoformat()}
    url = "/api/master/forecast/SO-001"
    assert client.patch(url, json=data, headers=headers("CMO_MANAGER")).status_code == 403
    result = client.patch(url, json=data, headers=headers("COO_MANAGER"))
    assert result.status_code == 200, result.text
    assert result.json()["buffer_days"] == 2
    assert db.query(m.AuditLog).filter_by(entity="OrderForecast").count() == 1
    snapshot = {"process": "Sewing", "snapshot_date": date.today().isoformat(), "capacity": 500, "planned_load": 600}
    assert client.post("/api/master/wip-capacity", json=snapshot, headers=headers("COO_MANAGER")).status_code == 200
    assert db.query(m.AuditLog).filter_by(entity="CapacitySnapshot").count() == 1


def test_finance_dashboard_aging_and_units(db, client, headers):
    o = order(db)
    db.add_all([m.Invoice(invoice_no="I1", order_fk=o.id, amount=100, paid_amount=30, due_date=date.today()-timedelta(days=1)),
                m.Invoice(invoice_no="I2", order_fk=o.id, amount=50, paid_amount=50, due_date=date.today()-timedelta(days=1))])
    db.commit()
    result = client.get("/api/dashboard/CFO", headers=headers("CFO_MANAGER")).json()
    cards = {c["label"]: c for c in result["cards"]}
    assert cards["Outstanding"]["value"] == 70
    assert cards["AR Lewat Jatuh Tempo"]["value"] == 70
    assert cards["Outstanding"]["unit"] == "currency"
    assert result["unavailable_features"]
