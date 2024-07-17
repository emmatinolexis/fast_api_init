from app.repository.fine_report_repository import FineReportRepository
from app.service.base_service import BaseService


class FineReportService(BaseService):
    def __init__(self, fine_report_repository: FineReportRepository):
        self.fine_report_repository = fine_report_repository
        super().__init__(fine_report_repository)

    def get_fine_reports(self):
        try:
            reports = self.fine_report_repository.get_fine_reports()
            return reports
        except Exception as e:
            raise e

    def get_fine_report(self, uuid: str):
        try:
            reports = self.fine_report_repository.get_fine_report(uuid)
            return reports
        except Exception as e:
            raise e
