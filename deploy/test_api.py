import urllib.request, json
BASE='http://localhost:8000/api'
def req(url,data=None,headers=None):
    headers = headers or {}
    d=json.dumps(data).encode() if data else None
    r=urllib.request.urlopen(urllib.request.Request(f'{BASE}{url}',data=d,headers={'Content-Type':'application/json',**headers}))
    return json.loads(r.read())

t=req('/auth/login',{'email':'iyan@syams.local','password':'demo123'})['access_token']
H={'Authorization':f'Bearer {t}'}

# Get orders
od=req('/orders',headers=H)
order_map={o['order_id']:o['id'] for o in od}
print(f'ORDERS: {len(od)} items')

# Test deliveries
d=req('/coo/deliveries',headers=H)
print(f'DELIVERIES: {len(d)} items', [x['status'] for x in d])

# Test order closing
oid=order_map.get('SO-001')
oc=req(f'/coo/order-closing/{oid}',headers=H)
print(f'CLOSING SO-001: {oc.get("order_close_status")}')

# Test production plans
pp=req('/coo/production-plans',headers=H)
print(f'PROD PLANS: {len(pp)} items', [x['status'] for x in pp])

# Test shipments
sh=req('/coo/shipments',headers=H)
print(f'SHIPMENTS: {len(sh)} items')
for s in sh:
    print(f"  {s['shipment_no']}: status={s['status']} fin={s['finance_gate']} ceo={s['ceo_approval']}")

# CFO gate - use APPROVE not APPROVED
t2=req('/auth/login',{'email':'lutfi@syams.local','password':'demo123'})['access_token']
H2={'Authorization':f'Bearer {t2}'}
shp1=next((s for s in sh if s['shipment_no']=='SHP-001'),None)
if shp1:
    g=req(f"/cfo/shipments/{shp1['id']}/gate",{'action':'APPROVE','reason':'Payment confirmed'},H2)
    print(f'CFO GATE SHP-001: fin_gate={g.get("finance_gate")}')

# CEO approve - use APPROVE not APPROVED
shp2=next((s for s in sh if s['shipment_no']=='SHP-002'),None)
if shp2:
    a=req(f"/ceo/shipments/{shp2['id']}/approve-shipment",{'action':'APPROVE','reason':'Approved by CEO'},H)
    print(f'CEO APPROVE SHP-002: ceo={a.get("ceo_approval")}')

# Movements
t3=req('/auth/login',{'email':'siti@syams.local','password':'demo123'})['access_token']
mv=req('/coo/movements',headers={'Authorization':f'Bearer {t3}'})
print(f'MOVEMENTS: {len(mv)} items')

# Quotations
qt=req('/cmo/quotations',headers=H)
print(f'QUOTATIONS: {len(qt)} items')

# Release to purchasing
mr=req('/coo/material-requests',headers=H)
if mr:
    mr1=next((m for m in mr if m['status']=='REQUESTED'),None)
    if mr1:
        try:
            rp=req(f"/coo/release-to-purchasing/{mr1['id']}",{},H)
            print(f'RELEASE TO PO: {rp}')
        except Exception as e:
            print(f'RELEASE TO PO ERROR: {e}')

print('\n=== ALL TESTS DONE ===')
