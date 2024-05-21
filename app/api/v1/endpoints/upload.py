import base64
import uuid

from fastapi import APIRouter, Depends
from fastapi.responses import ORJSONResponse

from app.core.dependencies import get_current_user
from app.model.user import User
from app.schema.upload_schema import FileUploadPayload
from app.util.utils import upload_to_s3

router = APIRouter(
    prefix="/uploads",
    tags=["file uploads"],
)
msg_prefix = "uploads"


@router.post("/", response_class=ORJSONResponse)
async def file_upload_handler(
    payload: FileUploadPayload,
    current_user: User = Depends(get_current_user),
):
    try:
        content_types = {
            "jpg": "image/jpeg",
            "jpeg": "image/jpeg",
            "png": "image/png",
            "pdf": "application/pdf",
        }

        content_type = content_types.get(payload.file_format)

        file_content = base64.b64decode(payload.encoded_file)

        url = await upload_to_s3(
            file_name=uuid.uuid4().hex + "." + payload.file_format,
            file_content=file_content,
            content_type=content_type,
        )

        return {
            "message": f"{msg_prefix}:file_upload_handler:success",
            "data": {
                "url": url,
            },
        }

    except Exception as e:
        return {
            "message": f"{msg_prefix}:file_upload_handler:failed",
            "error": str(e),
        }
