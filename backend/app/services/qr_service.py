"""
QR code and barcode generation for assets.

Each asset's QR code encodes a URL fragment like /assets/scan/FE-00001 that the
frontend PWA resolves by looking up the asset_id, then opens the mobile asset page.
"""
import os
import qrcode
from barcode import Code128
from barcode.writer import ImageWriter
from app.core.config import settings


def generate_qr_code(asset_id: str, base_scan_url: str = "fireaims://scan") -> str:
    """Generates a QR code PNG for the given asset_id and returns its relative static path."""
    payload = f"{base_scan_url}/{asset_id}"
    img = qrcode.make(payload)
    filename = f"{asset_id}_qr.png"
    filepath = os.path.join(settings.QR_DIR, filename)
    img.save(filepath)
    return f"/static/qr/{filename}"


def generate_barcode(asset_id: str) -> str:
    """Generates a Code128 barcode PNG for the given asset_id and returns its relative static path."""
    filename_base = f"{asset_id}_barcode"
    filepath_base = os.path.join(settings.QR_DIR, filename_base)
    writer = ImageWriter()
    writer.dpi = 200
    code = Code128(asset_id, writer=writer)
    saved_path = code.save(filepath_base)  # library appends the correct extension
    saved_filename = os.path.basename(saved_path)
    return f"/static/qr/{saved_filename}"
