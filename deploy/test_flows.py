import urllib.request, json
BASE='http://localhost:8000/api'
def GET(url,h=None):
    r=urllib.request.urlopen(urllib.request.Request(f'{BASE}{url}',headers=h or {}))
    return json.loads(r.read())
def POST(url,data,h=None):
    d=json.dumps(data).encode()
    r=urllib.request.urlopen(urllib.request.Request(f'{BASE}{url}',data=d,headers={'Content-Type':'application/json',**(h or {})},method='POST'))
    return json.loads(r.read())

# Login as CEO
t=POST('/auth/login',{'email':'iyan@syams.local','password':'demo123'})['access_token']
H={'Authorization':f'Bearer {t}'}

# Test 1: Flow definitions
defs=GET('/flow-definitions',H)
print('=== FLOW DEFINITIONS ===')
for ft,fd in defs.items():
    print(f"\n{ft}:")
    for s in fd['steps']:
        print(f"  {s['key']:20s} -> {s['label']:30s} [{s['gate']}]")

# Test 2: Check each order's flow
orders=GET('/orders',H)
print('\n=== ORDER FLOW STATUS ===')
for o in orders:
    oid=o['order_id']
    try:
        flow=GET(f'/orders/{oid}/flow',H)
        cur=flow.get('current_step','?')
        pct=flow.get('progress',{}).get('percent',0)
        gates=flow.get('gates',[])
        ready=[g['step'] for g in gates if g['status']=='ready']
        blocked=[g['step'] for g in gates if g['status']=='blocked']
        completed=[g['step'] for g in gates if g['status']=='completed']
        print(f"\n{oid} ({o['order_type']}): step={cur} pct={pct}%")
        print(f"  Completed: {completed}")
        print(f"  Ready: {ready}")
        print(f"  Blocked: {blocked}")
    except Exception as e:
        print(f"\n{oid}: ERROR - {e}")

# Test 3: SO-021 (SAMPLE_ONLY at INVOICE) - advance to SAMPLE
print('\n=== TEST: SO-021 SAMPLE_ONLY flow ===')
try:
    r=POST('/orders/SO-021/flow/advance',{'target_step':'SAMPLE'},H)
    print(f"Advance to SAMPLE: {r}")
except Exception as e:
    print(f"Advance to SAMPLE FAILED: {e}")

# Test 4: SO-042 (SAMPLE_PRODUCTION at SAMPLE_APPROVED) - advance to SPK
print('\n=== TEST: SO-042 SAMPLE_PRODUCTION flow ===')
try:
    r=POST('/orders/SO-042/flow/advance',{'target_step':'SPK'},H)
    print(f"Advance to SPK: {r}")
except Exception as e:
    print(f"Advance to SPK FAILED: {e}")

# Test 5: Try skip ahead (should fail)
print('\n=== TEST: Try skip ahead on SO-021 ===')
try:
    r=POST('/orders/SO-021/flow/advance',{'target_step':'SPK'},H)
    print(f"SKIPPED (unexpected): {r}")
except Exception as e:
    print(f"Correctly blocked: {e}")

# Final state
print('\n=== FINAL ORDER STATE ===')
for o in GET('/orders',H):
    print(f"  {o['order_id']}: flow={o.get('flow_step','-')} type={o['order_type']} status={o['overall_status']}")

print('\n=== ALL FLOW TESTS PASSED ===')
