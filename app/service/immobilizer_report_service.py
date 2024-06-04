from app.repository.immobilizer_report_repository import \
    ImmobilizerReportRepository
from app.service.base_service import BaseService


class ImmobilizerReportService(BaseService):
    def __init__(self, immobilizer_report_repository: ImmobilizerReportRepository):
        self.immobilizer_report_repository = immobilizer_report_repository
        super().__init__(immobilizer_report_repository)
