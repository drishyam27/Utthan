import httpx

base = "http://127.0.0.1:8000"

print("--- STEP 7: HEALTH ---")
r_health = httpx.get(f"{base}/api/health")
print("Health:", r_health.status_code, r_health.json())
assert r_health.status_code == 200

r_db = httpx.get(f"{base}/api/health/db")
print("DB Health:", r_db.status_code, r_db.json())
assert r_db.status_code == 200

print("\n--- STEP 8: LOCATIONS ---")
r_states = httpx.get(f"{base}/api/locations/states")
states = r_states.json()
print("States status:", r_states.status_code, "Count:", len(states))
assert len(states) == 36

for code in ["UP", "WB", "JH", "KA"]:
    r_dist = httpx.get(f"{base}/api/locations/states/{code}/districts")
    data = r_dist.json()
    print(f"State {code} ({data['state']['name']}): status={r_dist.status_code}, count={data['total_districts']}, sample={data['districts'][0]['name']}")

total_districts = 0
for s in states:
    r_d = httpx.get(f"{base}/api/locations/states/{s['code']}/districts")
    total_districts += len(r_d.json()["districts"])
print(f"Total districts across all 36 states via API: {total_districts}")
assert total_districts == 784

print("\n--- STEP 9: OPPORTUNITIES ---")
r_opps = httpx.get(f"{base}/api/opportunities")
opps = r_opps.json()
print("Opportunities status:", r_opps.status_code, "Count:", opps["total"])
assert opps["total"] == 7

first_opp_id = opps["opportunities"][0]["id"]
r_detail = httpx.get(f"{base}/api/opportunities/{first_opp_id}")
detail = r_detail.json()
print(f"Opportunity Detail ({first_opp_id}): status={r_detail.status_code}, title={detail['title']}, skills_count={len(detail['skills'])}")
assert r_detail.status_code == 200
assert len(detail["skills"]) > 0

print("\n--- STEP 10: NEGATIVE TESTS ---")
r_neg_state = httpx.get(f"{base}/api/locations/states/INVALID_STATE/districts")
print("Invalid State (INVALID_STATE):", r_neg_state.status_code, r_neg_state.json())
assert r_neg_state.status_code == 404

r_neg_opp = httpx.get(f"{base}/api/opportunities/invalid-opportunity-id")
print("Invalid Opportunity (invalid-opportunity-id):", r_neg_opp.status_code, r_neg_opp.json())
assert r_neg_opp.status_code == 404

# Verify no secrets in response
for resp in [r_neg_state, r_neg_opp]:
    text = resp.text.lower()
    assert "service_role" not in text
    assert "token" not in text
    assert "password" not in text
    assert "traceback" not in text

print("\n--- STEP 11: DOCUMENTATION ---")
r_docs = httpx.get(f"{base}/docs")
print("/docs status:", r_docs.status_code)
assert r_docs.status_code == 200

r_redoc = httpx.get(f"{base}/redoc")
print("/redoc status:", r_redoc.status_code)
assert r_redoc.status_code == 200

r_openapi = httpx.get(f"{base}/openapi.json")
openapi = r_openapi.json()
print("OpenAPI paths registered:", list(openapi.get("paths", {}).keys()))
assert "/api/health" in openapi["paths"]
assert "/api/locations/states" in openapi["paths"]
assert "/api/locations/resolve" in openapi["paths"]
assert "/api/opportunities" in openapi["paths"]

print("\n--- STEP 12: LOCATION RESOLUTION CONTRACT ---")
r_invalid_resolve = httpx.post(
    f"{base}/api/locations/resolve",
    json={"latitude": 91, "longitude": 0},
)
print("Invalid location payload:", r_invalid_resolve.status_code, r_invalid_resolve.json())
assert r_invalid_resolve.status_code == 422
assert "service_role" not in r_invalid_resolve.text.lower()
assert "traceback" not in r_invalid_resolve.text.lower()

print("\n[SUCCESS] ALL LIVE VERIFICATION CHECKS PASSED WITH 100% SUCCESS!")
