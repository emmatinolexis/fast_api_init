from app.repository.activity_log_repository import ActivityLogRepository
from app.repository.user_repository import UserRepository
from app.repository.role_repository import RoleRepository
from app.service.base_service import BaseService
from typing import Optional,List
from app.transfomers.activity_log_transformer import activity_log_transformer


class ActivityLogService(BaseService):
    def __init__(self, activity_log_repository: ActivityLogRepository, user_repository: UserRepository, role_repository: RoleRepository):
        self.user_repository = user_repository
        self.role_repository = role_repository
        self.activity_log_repository = activity_log_repository
        super().__init__(activity_log_repository)

    def all_activity_logs(self, start_date: Optional[str] = None, end_date: Optional[str] = None, page: int = 1, page_size: int = 10,activity_types: List[str] = None,search_string: str = None):
        logs =  self.activity_log_repository.all_activity_logs(start_date, end_date, page, page_size,activity_types,search_string)
        return [activity_log_transformer(log,self.user_repository,self.role_repository) for log in logs]

    def business_activity_logs(self, business_id: str,start_date: Optional[str] = None, end_date: Optional[str] = None, page: int = 1, page_size: int = 10,activity_types: List[str] = None,search_string:str=None):
        logs =  self.activity_log_repository.business_activity_logs(business_id, start_date, end_date, page, page_size,activity_types,search_string)
        return [activity_log_transformer(log,self.user_repository,self.role_repository) for log in logs]

    def admin_activity_logs(self,start_date: Optional[str] = None, end_date: Optional[str] = None, page: int = 1, page_size: int = 10,activity_types: List[str] = None,search_string:str=None):
        logs =  self.activity_log_repository.admin_activity_logs(start_date, end_date, page, page_size,activity_types,search_string)
        return [activity_log_transformer(log,self.user_repository,self.role_repository) for log in logs]
    
    def count_activity_logs(self,start_date: Optional[str] = None, end_date: Optional[str] = None,activity_types: List[str] = None,search_string:str =None) -> int:
        return self.activity_log_repository.count_activity_logs(start_date,end_date,activity_types,search_string)
    
    def count_business_activity_logs(self, business_id: str, start_date: Optional[str] = None, end_date: Optional[str] = None,activity_types: List[str] = None,search_string:str=None ) -> int:
        return self.activity_log_repository.count_business_activity_logs(business_id, start_date, end_date,activity_types,search_string)
    

    def count_admin_activity_logs(self,start_date: Optional[str] = None, end_date: Optional[str] = None,activity_types: List[str] = None,search_string:str=None) -> int:
        return self.activity_log_repository.count_admin_activity_logs(start_date,end_date,activity_types,search_string)