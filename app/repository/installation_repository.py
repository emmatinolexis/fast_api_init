from contextlib import AbstractContextManager
from typing import Callable
from sqlalchemy.orm import Session
from app.model.installation import Installation
from app.model.order import Order
from app.schema.installation_schema import InstallationPayload
from app.repository.base_repository import BaseRepository
from datetime import datetime
from app.model.user import User
from app.util.enums import CustomerRoles

class InstallationRepository(BaseRepository):
    def __init__(self, session_factory: Callable[..., AbstractContextManager[Session]]):
        self.session_factory = session_factory
        super().__init__(session_factory, InstallationRepository)
    
    def get_installers(self):
        with self.session_factory() as session:
            return session.query(User).filter(User.user_role_uuid == CustomerRoles.INSTALLER).all()
        

    def create_installation(self, installation_payload: InstallationPayload):
        with self.session_factory() as session:
            try:
                installation = Installation(
                    installer_uuid=installation_payload.installer_uuid,
                    order_uuid=installation_payload.order_uuid,
                )
                session.add(installation)
                
                order = session.query(Order).filter_by(uuid=installation_payload.order_uuid).first()
                if order:
                    order.date_of_installation = datetime.now()
                    order.time_of_installation = datetime.now().time() 
                    
                session.commit()
                session.refresh(installation)
                return installation
            except Exception as e:
                session.rollback()
                raise e
