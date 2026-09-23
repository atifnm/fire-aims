from datetime import datetime, timedelta


def _create_extinguisher(client, admin_headers):
    res = client.post("/api/assets", json={"asset_type": "extinguisher"}, headers=admin_headers)
    return res.json()


def test_submit_inspection_updates_asset_dates_and_status(client, admin_headers, inspector_headers):
    asset = _create_extinguisher(client, admin_headers)
    res = client.post("/api/inspections", json={
        "asset_id": asset["id"], "overall_result": "pass", "general_remarks": "All good", "items": [],
    }, headers=inspector_headers)
    assert res.status_code == 200, res.text
    inspection = res.json()
    assert inspection["overall_result"] == "pass"
    assert inspection["next_inspection_date"] is not None

    updated_asset = client.get(f"/api/assets/{asset['asset_id']}", headers=admin_headers).json()
    assert updated_asset["last_inspection_date"] is not None
    assert updated_asset["next_inspection_date"] is not None


def test_failed_inspection_creates_defect_and_sets_out_of_service(client, admin_headers, inspector_headers):
    asset = _create_extinguisher(client, admin_headers)
    res = client.post("/api/inspections", json={
        "asset_id": asset["id"], "overall_result": "failed",
        "defect_description": "Pressure below acceptable range",
        "corrective_action": "Remove from service", "defect_severity": "high", "items": [],
    }, headers=inspector_headers)
    assert res.status_code == 200

    updated_asset = client.get(f"/api/assets/{asset['asset_id']}", headers=admin_headers).json()
    assert updated_asset["status"] == "out_of_service"

    defects = client.get("/api/defects", params={"asset_id": asset["id"]}, headers=admin_headers).json()
    assert len(defects) == 1
    assert defects[0]["severity"] == "high"


def test_supervisor_review_approves_inspection(client, admin_headers, inspector_headers):
    asset = _create_extinguisher(client, admin_headers)
    insp = client.post("/api/inspections", json={
        "asset_id": asset["id"], "overall_result": "pass", "items": [],
    }, headers=inspector_headers).json()

    res = client.post(f"/api/inspections/{insp['id']}/review", json={"approve": True}, headers=admin_headers)
    assert res.status_code == 200
    assert res.json()["status"] == "approved"


def test_inspector_cannot_review_inspection(client, inspector_headers, admin_headers):
    asset = _create_extinguisher(client, admin_headers)
    insp = client.post("/api/inspections", json={
        "asset_id": asset["id"], "overall_result": "pass", "items": [],
    }, headers=inspector_headers).json()
    res = client.post(f"/api/inspections/{insp['id']}/review", json={"approve": True}, headers=inspector_headers)
    assert res.status_code == 403


def test_maintenance_record_does_not_overwrite_history(client, admin_headers):
    asset = _create_extinguisher(client, admin_headers)
    for i in range(2):
        res = client.post("/api/maintenance", json={
            "asset_id": asset["id"], "service_date": "2026-01-0" + str(i + 1),
            "service_type": "refilled", "work_performed": f"Refill #{i}",
        }, headers=admin_headers)
        assert res.status_code == 200
    records = client.get("/api/maintenance", params={"asset_id": asset["id"]}, headers=admin_headers).json()
    assert len(records) == 2
