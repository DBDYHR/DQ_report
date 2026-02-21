from fastapi import APIRouter, Depends, File, UploadFile

from ...config import Settings, get_settings
from ...models.files import UploadedFileInfo
from ...services.file_parser import save_and_parse_upload


router = APIRouter()


@router.post(
    "/upload",
    response_model=UploadedFileInfo,
    summary="Upload a file and extract plain text",
)
async def upload_file(
    file: UploadFile = File(...),
    settings: Settings = Depends(get_settings),
) -> UploadedFileInfo:
    return await save_and_parse_upload(file, uploads_dir=settings.data_dir / "uploads")

