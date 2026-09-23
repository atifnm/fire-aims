import os
import uuid
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import Optional

from app.core.database import get_db
from app.core.deps import get_current_user
from app.core.config import settings
from app.models.user import User
from app.models.asset import Asset
from app.models.records import Photo, PhotoContext

router = APIRouter(prefix="/api/photos", tags=["photos"])


@router.post("")
async def upload_photo(
    asset_id: int = Form(...),
    context: PhotoContext = Form(PhotoContext.GENERAL),
    inspection_id: Optional[int] = Form(None),
    maintenance_record_id: Optional[int] = Form(None),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if file.content_type not in settings.ALLOWED_IMAGE_TYPES:
        raise HTTPException(status_code=400, detail=f"Unsupported file type: {file.content_type}")

    contents = await file.read()
    size_mb = len(contents) / (1024 * 1024)
    if size_mb > settings.MAX_UPLOAD_SIZE_MB:
        raise HTTPException(status_code=400, detail=f"File too large (max {settings.MAX_UPLOAD_SIZE_MB}MB)")

    asset = db.query(Asset).filter(Asset.id == asset_id).first()
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")

    ext = os.path.splitext(file.filename)[1] or ".jpg"
    safe_name = f"{asset.asset_id}_{uuid.uuid4().hex[:8]}{ext}"
    filepath = os.path.join(settings.UPLOAD_DIR, safe_name)
    with open(filepath, "wb") as f:
        f.write(contents)

    photo = Photo(
        asset_id=asset_id,
        inspection_id=inspection_id,
        maintenance_record_id=maintenance_record_id,
        file_path=f"/static/uploads/{safe_name}",
        context=context,
        uploaded_by_id=current_user.id,
    )
    db.add(photo)
    db.commit()
    db.refresh(photo)
    return {"id": photo.id, "file_path": photo.file_path, "context": photo.context}
