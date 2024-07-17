from app.repository.theft_report_repository import TheftReportRepository
from app.service.base_service import BaseService


class TheftReportService(BaseService):
    def __init__(self, theft_report_repository: TheftReportRepository):
        self.theft_report_repository = theft_report_repository
        super().__init__(theft_report_repository)
