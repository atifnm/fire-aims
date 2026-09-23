def test_create_extinguisher_generates_asset_id_and_codes(client, admin_headers):
    res = client.post("/api/assets", json={
        "asset_type": "extinguisher",
        "manufacturer": "Amerex",
        "serial_number": "SN-TEST-001",
        "extinguisher_detail": {"extinguisher_type": "CO2", "capacity": "6kg"},
    }, headers=admin_headers)
    assert res.status_code == 200, res.text
    data = res.json()
    assert data["asset_id"].startswith("FE-")
    assert data["qr_code_path"].endswith("_qr.png")
    assert data["barcode_path"] is not None
    assert data["extinguisher_detail"]["extinguisher_type"] == "CO2"


def test_asset_ids_increment_and_are_unique(client, admin_headers):
    ids = set()
    for _ in range(3):
        res = client.post("/api/assets", json={"asset_type": "mcp"}, headers=admin_headers)
        ids.add(res.json()["asset_id"])
    assert len(ids) == 3


def test_search_asset_by_serial_number(client, admin_headers):
    client.post("/api/assets", json={
        "asset_type": "extinguisher", "serial_number": "UNIQUE-SEARCH-123",
    }, headers=admin_headers)
    res = client.get("/api/assets", params={"search": "UNIQUE-SEARCH-123"}, headers=admin_headers)
    assert res.status_code == 200
    assert len(res.json()) == 1


def test_scan_lookup_unknown_code_returns_404(client, admin_headers):
    res = client.get("/api/assets/scan/FE-99999", headers=admin_headers)
    assert res.status_code == 404


def test_scan_lookup_known_code(client, admin_headers):
    created = client.post("/api/assets", json={"asset_type": "hose_reel"}, headers=admin_headers).json()
    res = client.get(f"/api/assets/scan/{created['asset_id']}", headers=admin_headers)
    assert res.status_code == 200
    assert res.json()["id"] == created["id"]


def test_delete_asset_requires_admin(client, inspector_headers, admin_headers):
    created = client.post("/api/assets", json={"asset_type": "branch"}, headers=admin_headers).json()
    res = client.delete(f"/api/assets/{created['asset_id']}", headers=inspector_headers)
    assert res.status_code == 403


def test_delete_asset_cascades_to_its_inspections(client, admin_headers, inspector_headers):
    asset = client.post("/api/assets", json={"asset_type": "extinguisher"}, headers=admin_headers).json()
    insp = client.post("/api/inspections", json={
        "asset_id": asset["id"], "overall_result": "pass", "items": [],
    }, headers=inspector_headers).json()

    res = client.delete(f"/api/assets/{asset['asset_id']}", headers=admin_headers)
    assert res.status_code == 200

    assert client.get(f"/api/assets/scan/{asset['asset_id']}", headers=admin_headers).status_code == 404
    assert client.get(f"/api/inspections/{insp['id']}", headers=admin_headers).status_code == 404
