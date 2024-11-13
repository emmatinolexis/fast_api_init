from app.repository.activity_log_repository import ActivityLogRepository
from app.service.base_service import BaseService
from typing import Optional


class ActivityLogService(BaseService):
    def __init__(self, activity_log_repository: ActivityLogRepository):
        self.activity_log_repository = activity_log_repository
        super().__init__(activity_log_repository)

    def all_activity_logs(self, start_date: Optional[str] = None, end_date: Optional[str] = None, page: int = 1, page_size: int = 10):
        return self.activity_log_repository.all_activity_logs(start_date, end_date)

    def business_activity_logs(self, business_id: str,start_date: Optional[str] = None, end_date: Optional[str] = None, page: int = 1, page_size: int = 10):
        return self.activity_log_repository.business_activity_logs(business_id, start_date, end_date, page, page_size)

    def admin_activity_logs(self,start_date: Optional[str] = None, end_date: Optional[str] = None, page: int = 1, page_size: int = 10):
        return self.activity_log_repository.admin_activity_logs(start_date, end_date, page, page_size)
    
    def count_activity_logs(self) -> int:
        return self.activity_log_repository.count_activity_logs()
    
    def count_business_activity_logs(self, business_id: str) -> int:
        return self.activity_log_repository.count_business_activity_logs(business_id)
    

    def count_admin_activity_logs(self) -> int:
        return self.activity_log_repository.count_admin_activity_logs()