import base64
import uuid

from fastapi import APIRouter, Depends
from fastapi.responses import ORJSONResponse

from app.core import messages
from app.core.dependencies import get_current_user
from app.model.user import User
from app.schema.upload_schema import FileUploadPayload
from app.util.utils import get_content_type, send_data_with_info, send_internal_server_error, upload_to_s3

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
        content_type = get_content_type(payload.file_format)

        file_content = base64.b64decode(payload.encoded_file)

        url = await upload_to_s3(
            file_name=uuid.uuid4().hex + "." + payload.file_format,
            file_content=file_content,
            content_type=content_type,
        )

        return send_data_with_info(
            data={"url": url},
            info=messages.UPLOAD_SUCCESS,
        )

    except Exception as e:
        return send_internal_server_error(
            user_msg=messages.UPLOAD_FAILED,
            error=str(e)
        )



