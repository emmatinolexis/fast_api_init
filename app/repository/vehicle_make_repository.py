from contextlib import AbstractContextManager
from typing import Callable, Optional, List

from sqlalchemy.orm import Session, joinedload

from app.model.vehicle_models import VehicleMake, AssetType
from app.repository.base_repository import BaseRepository

from datetime import datetime
import uuid
from app.schema.asset_schema import VehicleMakeInput

class VehicleMakeRepository(BaseRepository):
    def __init__(self, session_factory: Callable[..., AbstractContextManager[Session]]):
        self.session_factory = session_factory
        super().__init__(session_factory, VehicleMake)
    
    def create(self, make_input: VehicleMakeInput) -> VehicleMake:
        with self.session_factory() as session:
            new_make = self.model(
                uuid=uuid.uuid4(),
                name=make_input.name,
                asset_type=make_input.asset_type,  
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            session.add(new_make)
            session.commit()
            session.refresh(new_make)
            return new_make

    def get_vehicle_makes(self, asset_type: Optional[AssetType] = None) -> List[VehicleMake]:
        with self.session_factory() as session:
            query = session.query(self.model)
            if asset_type:
                query = query.filter_by(asset_type=asset_type)
            makes = query.all()
            return makes

    def get_vehicle_make_by_uuid(self, make_uuid) -> Optional[VehicleMake]:
        with self.session_factory() as session:
            make = session.query(self.model).options(joinedload(self.model.models)).filter_by(uuid=make_uuid).first()
            return make

    def get_vehicle_make_name(self, name: str) -> Optional[VehicleMake]:
        with self.session_factory() as session:
            make = session.query(self.model).filter_by(name=name).first()
            return make
