"""
Seed FIRE-AIMS with realistic demo data:
- 3 buildings, several floors/rooms
- 10 fire extinguishers, 5 hose cabinets (with reel/branch/MCP components),
  5 standalone hose reels, 5 MCPs, 5 branches
- Admin / Supervisor / Inspector demo accounts
- Default checklist templates matching the spec's checklists
- A spread of statuses: compliant, due soon, overdue, defective, under maintenance
- Sample inspections, maintenance records and defects

Run with:  python -m app.seed
"""
import random
from datetime import datetime, timedelta, date

from app.core.database import Base, engine, SessionLocal
from app import models
from app.core.security import hash_password
from app.models.user import User, UserRole
from app.models.location import Building, Floor, Location
from app.models.asset import Asset, AssetType, AssetStatus
from app.models.asset_details import ExtinguisherDetail, HoseCabinetDetail, HoseReelDetail, BranchDetail, McpDetail
from app.models.checklist import ChecklistTemplate, ChecklistTemplateItem
from app.models.inspection import Inspection, InspectionItem, InspectionResult, InspectionStatus, ItemResult
from app.models.records import (
    MaintenanceRecord, MaintenanceType, Defect, DefectSeverity, DefectStatus, AppSetting,
)
from app.services.qr_service import generate_qr_code, generate_barcode
from app.services.status_service import recalculate_asset_status

Base.metadata.create_all(bind=engine)
db = SessionLocal()


def reset():
    print("Dropping and recreating all tables...")
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


def seed_users():
    users = [
        User(employee_code="ADM-001", full_name="Rahim Admin", email="admin@fireaims.demo",
             phone="+60-12-0000001", role=UserRole.ADMIN, hashed_password=hash_password("Admin@123")),
        User(employee_code="SUP-001", full_name="Sarah Supervisor", email="supervisor@fireaims.demo",
             phone="+60-12-0000002", role=UserRole.SUPERVISOR, hashed_password=hash_password("Supervisor@123")),
        User(employee_code="INS-009", full_name="Ali Inspector", email="inspector1@fireaims.demo",
             phone="+60-12-0000003", role=UserRole.INSPECTOR, hashed_password=hash_password("Inspector@123")),
        User(employee_code="INS-014", full_name="Mei Inspector", email="inspector2@fireaims.demo",
             phone="+60-12-0000004", role=UserRole.INSPECTOR, hashed_password=hash_password("Inspector@123")),
    ]
    db.add_all(users)
    db.commit()
    return {u.employee_code: u for u in users}


def seed_locations():
    buildings_data = {
        "Fire Station HQ": ["Ground Floor", "Floor 1", "Floor 2"],
        "Building A - Admin Block": ["Ground Floor", "Floor 1", "Floor 2", "Floor 3"],
        "Building B - Warehouse": ["Ground Floor", "Mezzanine"],
    }
    locations = []
    for b_name, floor_names in buildings_data.items():
        building = Building(name=b_name, code=b_name.split()[0][:3].upper() + str(random.randint(10, 99)),
                             address=f"{b_name}, Demo Fire District")
        db.add(building)
        db.commit()
        for f_name in floor_names:
            floor = Floor(building_id=building.id, name=f_name)
            db.add(floor)
            db.commit()
            rooms = ["Corridor", "Electrical Room", "Main Entrance", "Store Room", "Office Area"]
            for room in random.sample(rooms, k=min(3, len(rooms))):
                loc = Location(floor_id=floor.id, department="Facilities", room=room,
                                area=random.choice(["Near Emergency Exit", "Near Stairwell", "Wall Mounted",
                                                     "Central Area"]),
                                description=f"{room} - {b_name}")
                db.add(loc)
                db.commit()
                locations.append(loc)
    return locations


def seed_checklists():
    templates = {}

    fe = ChecklistTemplate(name="Fire Extinguisher - Standard", asset_type=AssetType.EXTINGUISHER.value)
    db.add(fe)
    db.commit()
    fe_items = [
        ("Physical condition", "Cylinder/body free from visible damage"),
        ("Physical condition", "No excessive corrosion"),
        ("Physical condition", "No leakage"),
        ("Physical condition", "Pressure gauge condition satisfactory"),
        ("Physical condition", "Pressure within acceptable range"),
        ("Physical condition", "Safety pin installed"),
        ("Physical condition", "Tamper seal intact"),
        ("Physical condition", "Handle/lever in good condition"),
        ("Physical condition", "Hose in good condition"),
        ("Physical condition", "Nozzle in good condition"),
        ("Physical condition", "Label readable"),
        ("Physical condition", "Operating instructions visible"),
        ("Mounting & access", "Extinguisher properly mounted"),
        ("Mounting & access", "Mounting bracket secure"),
        ("Mounting & access", "Extinguisher accessible"),
        ("Mounting & access", "No obstruction"),
        ("Mounting & access", "Correct location"),
        ("Mounting & access", "Signage available/visible"),
    ]
    for i, (section, label) in enumerate(fe_items):
        db.add(ChecklistTemplateItem(template_id=fe.id, section=section, label=label, sort_order=i))
    templates["extinguisher"] = fe

    hc = ChecklistTemplate(name="Hose Cabinet - Standard", asset_type=AssetType.HOSE_CABINET.value)
    db.add(hc)
    db.commit()
    hc_items = [
        ("Cabinet", "Cabinet accessible"), ("Cabinet", "Cabinet clearly identified"),
        ("Cabinet", "Cabinet door condition satisfactory"), ("Cabinet", "Glass/panel condition satisfactory"),
        ("Cabinet", "Cabinet lock/latch condition satisfactory"), ("Cabinet", "No obstruction"),
        ("Cabinet", "Internal condition satisfactory"), ("Cabinet", "Signage visible"),
        ("Cabinet", "Cabinet mounting secure"),
        ("Hose Reel", "Hose reel present"), ("Hose Reel", "Reel securely mounted"),
        ("Hose Reel", "Reel rotates freely"), ("Hose Reel", "Hose correctly wound"),
        ("Hose Reel", "Hose free from cracks/damage"), ("Hose Reel", "Hose connection secure"),
        ("Hose Reel", "Hose length/condition satisfactory"), ("Hose Reel", "Valve operates correctly"),
        ("Hose Reel", "Water supply available"), ("Hose Reel", "No visible leakage"),
        ("Branch/Nozzle", "Branch/nozzle present"), ("Branch/Nozzle", "Branch/nozzle accessible"),
        ("Branch/Nozzle", "Nozzle free from damage"), ("Branch/Nozzle", "Connection secure"),
        ("Branch/Nozzle", "Valve/nozzle operates correctly"), ("Branch/Nozzle", "No obstruction"),
        ("Water Supply", "Water supply available"), ("Water Supply", "Pressure satisfactory"),
        ("Water Supply", "No visible leakage"), ("Water Supply", "Valve accessible"),
        ("Water Supply", "Pipework condition satisfactory"),
        ("MCP", "MCP present"), ("MCP", "MCP clearly visible"), ("MCP", "MCP accessible"),
        ("MCP", "MCP physically undamaged"), ("MCP", "Protective cover intact where applicable"),
        ("MCP", "Indicator/status normal"), ("MCP", "Functional test performed"),
        ("MCP", "Signal received by fire alarm panel"), ("MCP", "MCP reset successfully"),
        ("MCP", "No fault indication"),
    ]
    for i, (section, label) in enumerate(hc_items):
        db.add(ChecklistTemplateItem(template_id=hc.id, section=section, label=label, sort_order=i))
    templates["hose_cabinet"] = hc

    mcp = ChecklistTemplate(name="MCP - Standalone", asset_type=AssetType.MCP.value)
    db.add(mcp)
    db.commit()
    for i, label in enumerate(["MCP present", "MCP clearly visible", "MCP accessible", "MCP physically undamaged",
                                "Protective cover intact where applicable", "Indicator/status normal",
                                "Functional test performed", "Signal received by fire alarm panel",
                                "MCP reset successfully", "No fault indication"]):
        db.add(ChecklistTemplateItem(template_id=mcp.id, section="MCP", label=label, sort_order=i))
    templates["mcp"] = mcp

    hr = ChecklistTemplate(name="Hose Reel - Standalone", asset_type=AssetType.HOSE_REEL.value)
    db.add(hr)
    db.commit()
    for i, label in enumerate(["Reel securely mounted", "Reel rotates freely", "Hose correctly wound",
                                "Hose free from cracks/damage", "Hose connection secure", "Valve operates correctly",
                                "Water supply available", "No visible leakage"]):
        db.add(ChecklistTemplateItem(template_id=hr.id, section="Hose Reel", label=label, sort_order=i))
    templates["hose_reel"] = hr

    br = ChecklistTemplate(name="Branch/Nozzle - Standalone", asset_type=AssetType.BRANCH.value)
    db.add(br)
    db.commit()
    for i, label in enumerate(["Branch/nozzle present", "Branch/nozzle accessible", "Nozzle free from damage",
                                "Connection secure", "Valve/nozzle operates correctly", "No obstruction"]):
        db.add(ChecklistTemplateItem(template_id=br.id, section="Branch/Nozzle", label=label, sort_order=i))
    templates["branch"] = br

    db.commit()
    return templates


def seed_settings():
    from app.routers.settings import DEFAULT_SETTINGS
    for key, value, desc in DEFAULT_SETTINGS:
        db.add(AppSetting(key=key, value=value, description=desc))
    db.commit()


def make_asset(asset_type, location, num, **kwargs):
    prefix = {"extinguisher": "FE", "hose_cabinet": "HC", "hose_reel": "HR", "branch": "BR", "mcp": "MCP"}[asset_type]
    asset_id = f"{prefix}-{num:05d}"
    asset = Asset(
        asset_id=asset_id,
        asset_type=asset_type,
        location_id=location.id if location else None,
        manufacturer=kwargs.get("manufacturer", "Amerex"),
        model=kwargs.get("model", "Standard"),
        serial_number=kwargs.get("serial_number", f"SN-{random.randint(100000, 999999)}"),
        installation_date=kwargs.get("installation_date", date(2023, 1, 15)),
        assigned_department="Facilities",
        status=AssetStatus.COMPLIANT,
    )
    db.add(asset)
    db.commit()
    db.refresh(asset)
    asset.qr_code_path = generate_qr_code(asset.asset_id)
    asset.barcode_path = generate_barcode(asset.asset_id)
    db.commit()
    return asset


def seed_assets(locations, users):
    now = datetime.utcnow()
    extinguisher_types = ["ABC Dry Chemical", "CO2", "Foam", "Water", "Wet Chemical"]
    assets = {"extinguisher": [], "hose_cabinet": [], "hose_reel": [], "branch": [], "mcp": []}

    # 10 extinguishers with a spread of statuses
    status_plan = (
        [(30, AssetStatus.COMPLIANT)] * 4 +
        [(15, AssetStatus.DUE_SOON)] * 2 +
        [(-5, AssetStatus.OVERDUE)] * 2 +
        [(20, AssetStatus.DEFECTIVE)] * 1 +
        [(20, AssetStatus.UNDER_MAINTENANCE)] * 1
    )
    for i in range(1, 11):
        loc = random.choice(locations)
        a = make_asset("extinguisher", loc, i, manufacturer=random.choice(["Amerex", "Kidde", "Ceasefire"]))
        db.add(ExtinguisherDetail(
            asset_id=a.id, extinguisher_type=random.choice(extinguisher_types),
            capacity=random.choice(["6kg", "9kg", "4.5kg"]),
            manufacture_date=date(2022, 6, 1), expiry_date=date(2027, 6, 1),
        ))
        days_offset, forced_status = status_plan[i - 1]
        a.last_inspection_date = now - timedelta(days=30 - days_offset if days_offset > 0 else 35)
        a.next_inspection_date = now + timedelta(days=days_offset)
        a.last_service_date = now - timedelta(days=100)
        a.next_service_date = now + timedelta(days=265)
        db.commit()
        recalculate_asset_status(db, a)
        if forced_status in (AssetStatus.UNDER_MAINTENANCE, AssetStatus.DEFECTIVE):
            a.status = forced_status
            db.commit()
        assets["extinguisher"].append(a)

    # 5 hose cabinets, each with a reel + branch + MCP as components
    for i in range(1, 6):
        loc = random.choice(locations)
        cabinet = make_asset("hose_cabinet", loc, i, manufacturer="FireGuard")
        db.add(HoseCabinetDetail(asset_id=cabinet.id, cabinet_material="Steel", has_glass_panel="yes"))
        cabinet.last_inspection_date = now - timedelta(days=20)
        cabinet.next_inspection_date = now + timedelta(days=70 if i != 5 else -3)
        db.commit()

        reel = make_asset("hose_reel", loc, i, manufacturer="FireGuard")
        db.add(HoseReelDetail(asset_id=reel.id, hose_length_m=30, hose_diameter_mm=25))
        reel.parent_asset_id = cabinet.id
        db.commit()

        branch = make_asset("branch", loc, i, manufacturer="FireGuard")
        db.add(BranchDetail(asset_id=branch.id, nozzle_type="Adjustable jet/spray", condition="Good"))
        branch.parent_asset_id = cabinet.id
        db.commit()

        mcp = make_asset("mcp", loc, i, manufacturer="Apollo")
        db.add(McpDetail(asset_id=mcp.id, connected_panel="Main Fire Alarm Panel", zone_address=f"Z{i}",
                          last_functional_test=date(2026, 6, 1), next_test_date=date(2026, 12, 1)))
        mcp.parent_asset_id = cabinet.id
        db.commit()

        for a in (cabinet, reel, branch, mcp):
            recalculate_asset_status(db, a)
        assets["hose_cabinet"].append(cabinet)
        assets["hose_reel"].append(reel)
        assets["branch"].append(branch)
        assets["mcp"].append(mcp)

    return assets


def seed_inspections_and_history(assets, users, templates):
    inspector = users["INS-014"]
    inspector2 = users["INS-009"]

    # A clean pass on one extinguisher
    fe1 = assets["extinguisher"][0]
    insp = Inspection(
        asset_id=fe1.id, inspector_id=inspector.id, checklist_template_id=templates["extinguisher"].id,
        inspected_at=datetime.utcnow() - timedelta(days=5), overall_result=InspectionResult.PASS,
        general_remarks="All checks satisfactory.", status=InspectionStatus.APPROVED,
        reviewed_by_id=users["SUP-001"].id, reviewed_at=datetime.utcnow() - timedelta(days=4),
        next_inspection_date=datetime.utcnow() + timedelta(days=25),
    )
    db.add(insp)
    db.commit()
    for label in ["Cylinder/body free from visible damage", "Pressure within acceptable range", "Tamper seal intact"]:
        db.add(InspectionItem(inspection_id=insp.id, section="Physical condition", label=label, result=ItemResult.PASS))
    db.commit()

    # A defective extinguisher with a HIGH severity defect + corrective action
    fe_defective = next(a for a in assets["extinguisher"] if a.status == AssetStatus.DEFECTIVE)
    insp2 = Inspection(
        asset_id=fe_defective.id, inspector_id=inspector2.id, checklist_template_id=templates["extinguisher"].id,
        inspected_at=datetime.utcnow() - timedelta(days=2), overall_result=InspectionResult.REQUIRES_MAINTENANCE,
        general_remarks="Pressure gauge reading in red zone.",
        defect_description="Pressure below acceptable range", corrective_action="Remove from service and send for refill",
        status=InspectionStatus.SUBMITTED, next_inspection_date=datetime.utcnow() + timedelta(days=28),
    )
    db.add(insp2)
    db.commit()
    db.add(InspectionItem(inspection_id=insp2.id, section="Physical condition",
                           label="Pressure within acceptable range", result=ItemResult.FAIL,
                           remarks="Gauge in red zone"))
    db.commit()
    defect = Defect(
        asset_id=fe_defective.id, inspection_id=insp2.id,
        description="Pressure below acceptable range", severity=DefectSeverity.HIGH,
        status=DefectStatus.ASSIGNED, assigned_to="Maintenance Team",
        due_date=date.today() + timedelta(days=5),
        corrective_action="Remove from service and send for maintenance",
    )
    db.add(defect)
    db.commit()
    recalculate_asset_status(db, fe_defective)

    # A completed maintenance/refill record
    fe_serviced = assets["extinguisher"][1]
    db.add(MaintenanceRecord(
        asset_id=fe_serviced.id, service_date=date.today() - timedelta(days=90),
        service_type=MaintenanceType.REFILLED, work_performed="Full refill and pressure test",
        agent_used="ABC Dry Chemical", quantity="9kg", service_provider="SafeGuard Fire Services",
        technician="T. Lee", cost=85.00, next_service_date=date.today() + timedelta(days=275),
        recorded_by_id=users["ADM-001"].id,
    ))
    db.commit()


def main():
    reset()
    print("Seeding users...")
    users = seed_users()
    print("Seeding settings...")
    seed_settings()
    print("Seeding locations...")
    locations = seed_locations()
    print("Seeding checklist templates...")
    templates = seed_checklists()
    print("Seeding assets...")
    assets = seed_assets(locations, users)
    print("Seeding inspection/maintenance/defect history...")
    seed_inspections_and_history(assets, users, templates)
    print("\nDone. Demo credentials:")
    print("  Admin:      admin@fireaims.demo      / Admin@123")
    print("  Supervisor: supervisor@fireaims.demo  / Supervisor@123")
    print("  Inspector:  inspector1@fireaims.demo  / Inspector@123  (Ali, INS-009)")
    print("  Inspector:  inspector2@fireaims.demo  / Inspector@123  (Mei, INS-014)")


if __name__ == "__main__":
    main()
