from app.repository.smart_report_repository import SmartReportRepository
from app.service.base_service import BaseService


class SmartReportService(BaseService):
    def __init__(self, smart_report_repository: SmartReportRepository):
        self.smart_report_repository = smart_report_repository
        super().__init__(smart_report_repository)

    def get_reports(
        self,
        user_uuid: str = None,
        business_profile_uuid: str = None,
        page=1,
        page_size=10,
    ):
        try:
            return self.smart_report_repository.read_all_reports(
                business_uuid=business_profile_uuid,
                user_uuid=user_uuid,
                page_size=page_size,
                page=page,
            )
        except Exception as e:
            raise e

    def generate_smart_report(
        self,
        date_from: str,
        date_to: str,
        asset_type_uuid: str,
        asset_uuids: list,
        report_types: list,
    ):
        try:
            return self.smart_report_repository.generate_smart_reports(
                date_from, date_to, asset_type_uuid, asset_uuids, report_types
            )
        except Exception as e:
            raise e
