from fastapi import APIRouter, Depends
from fastapi.responses import ORJSONResponse
from dependency_injector.wiring import Provide, inject
from app.core import messages
from app.core.container import Container
from app.schema.contact_sale_schema import ContactSale as ContactSaleSchema
from app.service.contact_sale_service import ContactSaleService
from app.util.utils import send_data, send_internal_server_error, send_client_side_error

router = APIRouter(
    prefix="/contact_sales",
    tags=["contact_sales"],
)

@router.post("/", response_class=ORJSONResponse)
@inject
async def create_contact_sales_handler(
    payload: ContactSaleSchema,
    service: ContactSaleService = Depends(Provide[Container.contact_sale_service]),
):
    try:
        contact_sale = service.create_contact_sale(payload)
        return send_data(contact_sale)
    except Exception as e:
        msg = messages.CREATE_FAILED + " contact sale"
        return send_internal_server_error(user_msg=msg, error=e)
