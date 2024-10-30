from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, Query
from fastapi.responses import ORJSONResponse

from app.core import messages
from app.core.container import Container
from app.core.dependencies import get_current_user

from app.model.user import User

from app.service.payment_service import PaymentService
from app.util.utils import (
    send_data,
    send_internal_server_error,
)

router = APIRouter(
    prefix="/payments",
    tags=["payments"],
)
msg_prefix = "payment"


@router.get("/", response_class=ORJSONResponse)
@inject
async def get_all_payments_handler(
    search_parameter: str = None,
    start_date: str = Query(
        None, description="Start date should be in the format dd/mm/yyyy"
    ),
    end_date: str = Query(
        None, description="End date should be in the format dd/mm/yyyy"
    ),
    page: int = Query(1, ge=1, description="Page number, default is set to 1"),
    page_size: int = Query(
        10, ge=1, le=1000, description="Items per page, default is 10"
    ),
    service: PaymentService = Depends(Provide[Container.payment_service]),
    current_user: User = Depends(get_current_user),
):
    try:
        return send_data(
            service.get_payments(
                search_parameter, start_date, end_date, page, page_size
            )
        )
    except Exception as e:
        msg = f"{messages.GET_FAILED} {msg_prefix}s"
        return send_internal_server_error(user_msg=msg, error=e)
