from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends
from fastapi.responses import ORJSONResponse

from app.core.container import Container
from app.schema.rnd_image_schema import RNDImageUploadRequest
from app.service.rnd_image_service import RNDImageService
from app.util.utils import (
    send_client_side_error,
    send_data_with_info,
    send_internal_server_error,
)

# from app.schema.rnd_image_schema import RNDImageChunkUploadRequest

router = APIRouter(
    prefix="/rnd_images",
    tags=["RND Images"],
)


@router.post("/upload", response_class=ORJSONResponse)
@inject
async def upload_rnd_image(
    image_request: RNDImageUploadRequest,
    image_service: RNDImageService = Depends(Provide[Container.rnd_image_service]),
):
    try:
        image_base64 = image_request.image_base64
        url = await image_service.upload_image(image_base64)
        return send_data_with_info({"url": url}, "Image uploaded successfully")
    except ValueError as e:
        return send_client_side_error(user_msg=str(e), dev_msg=str(e))
    except Exception as e:
        return send_internal_server_error(user_msg="Failed to upload image", error=e)


@router.get("/list", response_class=ORJSONResponse)
@inject
async def list_rnd_images(
    image_service: RNDImageService = Depends(Provide[Container.rnd_image_service]),
):
    try:
        urls = image_service.list_images()
        return send_data_with_info({"images": urls}, "Images fetched successfully")
    except Exception as e:
        return send_internal_server_error(user_msg="Failed to fetch images", error=e)
