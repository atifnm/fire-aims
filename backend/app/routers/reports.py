import io
from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import Optional
import pandas as pd
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.models.asset import Asset, AssetStatus
from app.models.records import Defect, MaintenanceRecord
from app.models.inspection import Inspection

router = APIRouter(prefix="/api/reports", tags=["reports"])


def _asset_rows(db: Session):
    assets = db.query(Asset).all()
    return [{
        "Asset ID": a.asset_id,
        "Type": a.asset_type.value,
        "Location": a.location_path,
        "Manufacturer": a.manufacturer,
        "Model": a.model,
        "Serial Number": a.serial_number,
        "Last Inspection": a.last_inspection_date.strftime("%Y-%m-%d") if a.last_inspection_date else "",
        "Next Inspection": a.next_inspection_date.strftime("%Y-%m-%d") if a.next_inspection_date else "",
        "Status": a.status.value,
    } for a in assets]


def _defect_rows(db: Session):
    defects = db.query(Defect).all()
    return [{
        "Asset ID": d.asset.asset_id if d.asset else "",
        "Location": d.asset.location_path if d.asset else "",
        "Defect": d.description,
        "Severity": d.severity.value,
        "Date": d.created_at.strftime("%Y-%m-%d"),
        "Status": d.status.value,
        "Corrective Action": d.corrective_action or "",
    } for d in defects]


def _maintenance_rows(db: Session):
    records = db.query(MaintenanceRecord).all()
    return [{
        "Asset ID": m.asset.asset_id if m.asset else "",
        "Service Date": m.service_date.strftime("%Y-%m-%d") if m.service_date else "",
        "Service Type": m.service_type.value,
        "Technician": m.technician or "",
        "Service Provider": m.service_provider or "",
        "Next Service Date": m.next_service_date.strftime("%Y-%m-%d") if m.next_service_date else "",
        "Cost": m.cost or "",
    } for m in records]


REPORT_BUILDERS = {
    "equipment": _asset_rows,
    "defects": _defect_rows,
    "maintenance": _maintenance_rows,
}


@router.get("/{report_type}/csv")
def export_csv(report_type: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    builder = REPORT_BUILDERS.get(report_type)
    if not builder:
        return {"error": f"Unknown report type '{report_type}'"}
    df = pd.DataFrame(builder(db))
    buf = io.StringIO()
    df.to_csv(buf, index=False)
    buf.seek(0)
    return StreamingResponse(
        iter([buf.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={report_type}_report.csv"},
    )


@router.get("/{report_type}/excel")
def export_excel(report_type: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    builder = REPORT_BUILDERS.get(report_type)
    if not builder:
        return {"error": f"Unknown report type '{report_type}'"}
    df = pd.DataFrame(builder(db))
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name=report_type.title())
    buf.seek(0)
    return StreamingResponse(
        buf,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename={report_type}_report.xlsx"},
    )


@router.get("/monthly-summary/pdf")
def monthly_summary_pdf(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    total = db.query(Asset).count()
    inspected = db.query(Asset).filter(Asset.last_inspection_date.isnot(None)).count()
    overdue = db.query(Asset).filter(Asset.status == AssetStatus.OVERDUE).count()
    defective = db.query(Asset).filter(Asset.status == AssetStatus.DEFECTIVE).count()
    maintenance_req = db.query(Asset).filter(Asset.status == AssetStatus.UNDER_MAINTENANCE).count()
    passed = db.query(Inspection).filter(Inspection.overall_result == "pass").count()
    failed = db.query(Inspection).filter(Inspection.overall_result == "failed").count()

    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=letter)
    styles = getSampleStyleSheet()
    elements = [
        Paragraph("FIRE-AIMS — Monthly Inspection Report", styles["Title"]),
        Spacer(1, 12),
        Paragraph("This report summarizes current fire safety equipment inspection status. "
                  "It reflects data recorded in the system and does not itself certify regulatory compliance.",
                  styles["Normal"]),
        Spacer(1, 16),
    ]
    data = [
        ["Metric", "Value"],
        ["Total Equipment", total],
        ["Inspected (has inspection on file)", inspected],
        ["Pending / Never Inspected", total - inspected],
        ["Overdue", overdue],
        ["Passed Inspections (all-time)", passed],
        ["Failed Inspections (all-time)", failed],
        ["Currently Defective", defective],
        ["Currently Under Maintenance", maintenance_req],
    ]
    table = Table(data, colWidths=[3.5 * inch, 2 * inch])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#B91C1C")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F3F4F6")]),
        ("PADDING", (0, 0), (-1, -1), 6),
    ]))
    elements.append(table)
    doc.build(elements)
    buf.seek(0)
    return StreamingResponse(
        buf, media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=monthly_summary_report.pdf"},
    )
