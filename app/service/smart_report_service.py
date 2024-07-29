from app.repository.smart_report_repository import SmartReportRepository
from app.service.base_service import BaseService


class SmartReportService(BaseService):
    def __init__(self, smart_report_repository: SmartReportRepository):
        self.smart_report_repository = smart_report_repository
        super().__init__(smart_report_repository)
