from contextlib import AbstractContextManager
from typing import Callable

import requests
from sqlalchemy import exc
from sqlalchemy.orm import Session, joinedload

from app.core.settings import settings
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

    def create_paystack_package_plan(self, payload):
        try:
            data = {
                "name": payload.name,
                "amount": payload.amount,
                "description": payload.description,
                "interval": "monthly",
                "send_invoices": True,
                "send_sms": True,
                "currency": "GHS",
                "invoice_limit": 1,
            }

            post_plan = requests.post(
                settings.PAYSTACK_PLAN_URL,
                headers=settings.PAYSTACK_HEADERS,
                json=data,
            )

            if post_plan.status_code == 201:
                # Retrieve the plan data from the response
                plan = post_plan.json().get("data")
                package = {
                    "package_plan_code": plan.get("plan_code"),
                    "package_name": plan.get("name"),
                    "package_price": plan.get("amount"),
                    "package_description": plan.get("description"),
                }
                return package

        except Exception as e:
            raise e

    def get_all_paystack_plans(self):
        with self.session_factory() as session:
            try:
                plans = requests.get(
                    settings.PAYSTACK_PLAN_URL, headers=settings.PAYSTACK_HEADERS
                )
                new_plan = plans.json()["data"]
                filtered_plans = [plan for plan in new_plan if not plan["is_deleted"]]
                packages = []
                if plans.status_code == 200:
                    for plan in filtered_plans:
                        package_items = (
                            session.query(PackageItemAssignment)
                            .filter(
                                PackageItemAssignment.paystack_plan_code
                                == plan["plan_code"]
                            )
                            .options(joinedload(PackageItemAssignment.package_item))
                            .all()
                        )
                        package = {
                            "package_plan_code": plan["plan_code"],
                            "package_name": plan["name"],
                            "package_price": plan["amount"],
                            "package_description": plan["description"],
                            "is_deleted": plan["is_deleted"],
                            "package_items": [
                                item.package_item for item in package_items
                            ],
                        }
                        packages.append(package)
                    return packages
            except Exception as e:
                raise e

    def read_by_plan_code(self, package_plan_code: str):
        with self.session_factory() as session:
            try:
                plan = requests.get(
                    settings.PAYSTACK_PLAN_URL + f"/{package_plan_code}",
                    headers=settings.PAYSTACK_HEADERS,
                )
                if plan.status_code == 200:
                    plan = plan.json()["data"]
                    package_items = (
                        session.query(PackageItemAssignment)
                        .filter(
                            PackageItemAssignment.paystack_plan_code
                            == plan["plan_code"]
                        )
                        .options(joinedload(PackageItemAssignment.package_item))
                        .all()
                    )
                    package = {
                        "package_plan_code": plan["plan_code"],
                        "package_name": plan["name"],
                        "package_price": plan["amount"],
                        "package_description": plan["description"],
                        "is_deleted": plan["is_deleted"],
                        "package_items": [item.package_item for item in package_items],
                    }
                    return package
                return None
            except Exception as e:
                raise e

    def update_paystack_plan(self, plan_code, payload):
        try:
            data = {
                "name": payload.name,
                "amount": payload.amount,
                "description": payload.description,
            }

            get_plan = PackageRepository(self.session_factory).read_by_plan_code(
                plan_code
            )
            # return get_plan
            if get_plan:
                if get_plan["is_deleted"] is True:
                    raise Exception("Package deleted, update cannot be done.")

                get_plan_code = get_plan["package_plan_code"]

                plan = requests.put(
                    settings.PAYSTACK_PLAN_URL + f"/{get_plan_code}",
                    headers=settings.PAYSTACK_HEADERS,
                    json=data,
                )

                return plan.json()
            return None
        except Exception as e:
            raise e

    def assign_package_item(self, data: PackageItemAssignmentPayload):
        with self.session_factory() as session:
            try:
                for item in data.package_item_uuids:
                    db_item = (
                        session.query(PackageItemAssignment)
                        .filter(
                            PackageItemAssignment.package_item_uuid == item,
                            PackageItemAssignment.paystack_plan_code
                            == data.package_plan_code,
                        )
                        .first()
                    )

                    if not db_item:
                        query = PackageItemAssignment(
                            package_item_uuid=item,
                            paystack_plan_code=data.package_plan_code,
                        )
                        session.add(query)
                        session.commit()
            except exc.IntegrityError as e:
                raise e
            except Exception as e:
                raise e

    def delete_package_item(self, plan_code: str, package_item_uuid: str):
        with self.session_factory() as session:
            try:
                db_item = (
                    session.query(PackageItemAssignment)
                    .filter(
                        PackageItemAssignment.paystack_plan_code == plan_code,
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
