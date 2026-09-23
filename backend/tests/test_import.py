import io


def _csv_bytes(text: str) -> io.BytesIO:
    return io.BytesIO(text.encode("utf-8"))


def test_import_creates_assets_and_auto_creates_locations(client, admin_headers):
    csv_text = (
        "asset_type,building,floor,room,area,manufacturer,serial_number,installation_date\n"
        "extinguisher,Import Test Bldg,Floor 1,Lobby,,Amerex,IMPORT-SN-1,2026-01-01\n"
        "mcp,Import Test Bldg,Floor 1,Lobby,,Apollo,IMPORT-SN-2,2026-01-01\n"
    )
    files = {"file": ("import.csv", _csv_bytes(csv_text), "text/csv")}
    res = client.post("/api/assets/import", files=files, headers=admin_headers)
    assert res.status_code == 200, res.text
    data = res.json()
    assert data["created"] == 2
    assert data["failed"] == 0
    asset_ids = [r["asset_id"] for r in data["results"]]

    # confirm the assets actually exist with the auto-created location attached
    for asset_id in asset_ids:
        got = client.get(f"/api/assets/scan/{asset_id}", headers=admin_headers)
        assert got.status_code == 200
        assert "Import Test Bldg" in got.json()["location_path"]

    # a second import naming the same building/floor/room should reuse them, not duplicate
    buildings = client.get("/api/buildings", headers=admin_headers).json()
    matching = [b for b in buildings if b["name"] == "Import Test Bldg"]
    assert len(matching) == 1


def test_import_bad_row_does_not_affect_good_rows(client, admin_headers):
    csv_text = (
        "asset_type,manufacturer,serial_number\n"
        "extinguisher,Amerex,GOOD-ROW-1\n"
        "not_a_real_type,Amerex,BAD-ROW\n"
        "extinguisher,Amerex,GOOD-ROW-2\n"
    )
    files = {"file": ("import.csv", _csv_bytes(csv_text), "text/csv")}
    res = client.post("/api/assets/import", files=files, headers=admin_headers)
    assert res.status_code == 200, res.text
    data = res.json()
    assert data["created"] == 2
    assert data["failed"] == 1
    statuses = {r["row"]: r["status"] for r in data["results"]}
    assert statuses[2] == "created"
    assert statuses[3] == "failed"
    assert statuses[4] == "created"

    # both good rows must actually be persisted despite the bad row in between
    res = client.get("/api/assets", params={"search": "GOOD-ROW-1"}, headers=admin_headers)
    assert len(res.json()) == 1
    res = client.get("/api/assets", params={"search": "GOOD-ROW-2"}, headers=admin_headers)
    assert len(res.json()) == 1


def test_import_missing_asset_type_column_rejected(client, admin_headers):
    csv_text = "manufacturer,serial_number\nAmerex,X-1\n"
    files = {"file": ("import.csv", _csv_bytes(csv_text), "text/csv")}
    res = client.post("/api/assets/import", files=files, headers=admin_headers)
    assert res.status_code == 400


def test_inspector_cannot_import_assets(client, inspector_headers):
    csv_text = "asset_type,manufacturer\nextinguisher,Amerex\n"
    files = {"file": ("import.csv", _csv_bytes(csv_text), "text/csv")}
    res = client.post("/api/assets/import", files=files, headers=inspector_headers)
    assert res.status_code == 403


def test_import_template_download(client, admin_headers):
    res = client.get("/api/assets/import/template", headers=admin_headers)
    assert res.status_code == 200
    assert "asset_type" in res.text
