from contextlib import AbstractContextManager
from typing import Callable

from sqlalchemy import exc
from sqlalchemy.orm import Session, joinedload

from app.model.package import Package
from app.model.package_item_assignment import PackageItemAssignment
from app.repository.base_repository import BaseRepository
from app.schema.package_schema import PackageItemAssignmentPayload


class PackageRepository(BaseRepository):
    def __init__(self, session_factory: Callable[..., AbstractContextManager[Session]]):
        self.session_factory = session_factory
        super().__init__(session_factory, Package)

    def get_all_packages(self):
        with self.session_factory() as session:
            return (
                session.query(self.model)
                .options(joinedload(Package.package_items))
                .all()
            )

    def assign_package_item(self, data: PackageItemAssignmentPayload):
        with self.session_factory() as session:
            try:
                for item in data.package_item_uuids:
                    db_item = (
                        session.query(PackageItemAssignment)
                        .filter(
                            PackageItemAssignment.package_item_uuid == item,
                            PackageItemAssignment.package_uuid == data.package_uuid,
                        )
                        .first()
                    )

                    if not db_item:
                        query = PackageItemAssignment(
                            package_item_uuid=item, package_uuid=data.package_uuid
                        )
                        session.add(query)
                        session.commit()
            except exc.IntegrityError as e:
                raise e
            except Exception as e:
                raise e

    def delete_package_item(self, package_uuid: str, package_item_uuid: str):
        with self.session_factory() as session:
            try:
                db_item = (
                    session.query(PackageItemAssignment)
                    .filter(
                        PackageItemAssignment.package_uuid == package_uuid,
                        PackageItemAssignment.package_item_uuid == package_item_uuid,
                    )
                    .first()
                )
                if db_item:
                    session.delete(db_item)
                    session.commit()
                return db_item
            except Exception as e:
                raise e
