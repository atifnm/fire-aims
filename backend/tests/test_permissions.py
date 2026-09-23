def _create_building_floor_location(client, admin_headers):
    b = client.post("/api/buildings", json={"name": "Test Bldg"}, headers=admin_headers).json()
    f = client.post("/api/floors", json={"building_id": b["id"], "name": "Floor 1"}, headers=admin_headers).json()
    loc = client.post("/api/locations", json={"floor_id": f["id"], "room": "Room A"}, headers=admin_headers).json()
    return b, f, loc


def test_admin_can_edit_building_floor_location(client, admin_headers):
    b, f, loc = _create_building_floor_location(client, admin_headers)

    res = client.put(f"/api/buildings/{b['id']}", json={"name": "Renamed Bldg"}, headers=admin_headers)
    assert res.status_code == 200
    assert res.json()["name"] == "Renamed Bldg"

    res = client.put(f"/api/floors/{f['id']}", json={"name": "Renamed Floor"}, headers=admin_headers)
    assert res.status_code == 200
    assert res.json()["name"] == "Renamed Floor"

    res = client.put(f"/api/locations/{loc['id']}", json={"room": "Renamed Room"}, headers=admin_headers)
    assert res.status_code == 200
    assert res.json()["room"] == "Renamed Room"


def test_inspector_cannot_edit_or_delete_locations(client, admin_headers, inspector_headers):
    b, f, loc = _create_building_floor_location(client, admin_headers)

    assert client.put(f"/api/buildings/{b['id']}", json={"name": "x"}, headers=inspector_headers).status_code == 403
    assert client.put(f"/api/floors/{f['id']}", json={"name": "x"}, headers=inspector_headers).status_code == 403
    assert client.put(f"/api/locations/{loc['id']}", json={"room": "x"}, headers=inspector_headers).status_code == 403
    assert client.delete(f"/api/locations/{loc['id']}", headers=inspector_headers).status_code == 403
    assert client.delete(f"/api/floors/{f['id']}", headers=inspector_headers).status_code == 403
    assert client.delete(f"/api/buildings/{b['id']}", headers=inspector_headers).status_code == 403


def test_admin_can_correct_inspection_with_audit_trail(client, admin_headers, inspector_headers):
    asset = client.post("/api/assets", json={"asset_type": "extinguisher"}, headers=admin_headers).json()
    insp = client.post("/api/inspections", json={
        "asset_id": asset["id"], "overall_result": "pass", "general_remarks": "typo'd remark", "items": [],
    }, headers=inspector_headers).json()

    res = client.put(f"/api/inspections/{insp['id']}", json={
        "general_remarks": "Corrected remark", "correction_reason": "Fixed a typo reported by the inspector",
    }, headers=admin_headers)
    assert res.status_code == 200, res.text
    assert res.json()["general_remarks"] == "Corrected remark"

    logs = client.get("/api/audit-logs", params={"entity_type": "inspection"}, headers=admin_headers).json()
    assert any("corrected inspection" in l["action"].lower() for l in logs)


def test_inspector_and_supervisor_cannot_correct_inspection(client, admin_headers, inspector_headers):
    asset = client.post("/api/assets", json={"asset_type": "extinguisher"}, headers=admin_headers).json()
    insp = client.post("/api/inspections", json={
        "asset_id": asset["id"], "overall_result": "pass", "items": [],
    }, headers=inspector_headers).json()

    res = client.put(f"/api/inspections/{insp['id']}", json={
        "general_remarks": "sneaky edit", "correction_reason": "n/a",
    }, headers=inspector_headers)
    assert res.status_code == 403


def test_correction_requires_a_reason(client, admin_headers, inspector_headers):
    asset = client.post("/api/assets", json={"asset_type": "extinguisher"}, headers=admin_headers).json()
    insp = client.post("/api/inspections", json={
        "asset_id": asset["id"], "overall_result": "pass", "items": [],
    }, headers=inspector_headers).json()

    res = client.put(f"/api/inspections/{insp['id']}", json={"general_remarks": "x"}, headers=admin_headers)
    assert res.status_code == 422  # correction_reason is a required field


def test_only_admin_can_update_defect_status(client, admin_headers, inspector_headers, supervisor_headers):
    asset = client.post("/api/assets", json={"asset_type": "extinguisher"}, headers=admin_headers).json()
    defect = client.post("/api/defects", json={
        "asset_id": asset["id"], "description": "Test defect",
    }, headers=inspector_headers).json()

    res = client.put(f"/api/defects/{defect['id']}", json={"status": "resolved"}, headers=supervisor_headers)
    assert res.status_code == 403

    res = client.put(f"/api/defects/{defect['id']}", json={"status": "resolved"}, headers=admin_headers)
    assert res.status_code == 200
    assert res.json()["status"] == "resolved"
