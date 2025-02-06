from contextlib import AbstractAsyncContextManager
from typing import Callable

import aiohttp
from sqlalchemy import exc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.core.settings import settings
from app.model.package import Package
from app.model.package_item_assignment import PackageItemAssignment
from app.repository.base_repository import BaseRepository
from app.schema.package_schema import PackageItemAssignmentPayload


class PackageRepository(BaseRepository):
    def __init__(
        self, session_factory: Callable[..., AbstractAsyncContextManager[AsyncSession]]
    ):
        self.session_factory = session_factory
        super().__init__(session_factory, Package)

    async def get_all_packages(self):
        async with self.session_factory() as session:
            result = await session.execute(
                session.query(self.model).options(joinedload(Package.package_items))
            )
            return result.scalars().all()

    async def create_paystack_package_plan(self, payload):
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

            async with aiohttp.ClientSession() as session:
                async with session.post(
                    settings.PAYSTACK_PLAN_URL,
                    headers=settings.PAYSTACK_HEADERS,
                    json=data,
                ) as response:
                    if response.status == 201:
                        plan = await response.json()
                        plan_data = plan.get("data")
                        package = {
                            "package_plan_code": plan_data.get("plan_code"),
                            "package_name": plan_data.get("name"),
                            "package_price": plan_data.get("amount"),
                            "package_description": plan_data.get("description"),
                        }
                        return package

        except Exception as e:
            await session.rollback()
            raise e

    async def get_all_paystack_plans(self):
        async with self.session_factory() as session:
            try:
                async with aiohttp.ClientSession() as http_session:
                    async with http_session.get(
                        settings.PAYSTACK_PLAN_URL, headers=settings.PAYSTACK_HEADERS
                    ) as response:
                        plans = await response.json()
                        new_plan = plans["data"]
                        filtered_plans = [
                            plan for plan in new_plan if not plan["is_deleted"]
                        ]
                        packages = []
                        if response.status == 200:
                            for plan in filtered_plans:
                                result = await session.execute(
                                    session.query(PackageItemAssignment)
                                    .filter(
                                        PackageItemAssignment.paystack_plan_code
                                        == plan["plan_code"]
                                    )
                                    .options(
                                        joinedload(PackageItemAssignment.package_item)
                                    )
                                )
                                package_items = result.scalars().all()
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
                await session.rollback()
                raise e

    async def read_by_plan_code(self, package_plan_code: str):
        async with self.session_factory() as session:
            try:
                async with aiohttp.ClientSession() as http_session:
                    async with http_session.get(
                        settings.PAYSTACK_PLAN_URL + f"/{package_plan_code}",
                        headers=settings.PAYSTACK_HEADERS,
                    ) as response:
                        if response.status == 200:
                            plan = await response.json()
                            plan_data = plan["data"]
                            result = await session.execute(
                                session.query(PackageItemAssignment)
                                .filter(
                                    PackageItemAssignment.paystack_plan_code
                                    == plan_data["plan_code"]
                                )
                                .options(joinedload(PackageItemAssignment.package_item))
                            )
                            package_items = result.scalars().all()
                            package = {
                                "package_plan_code": plan_data["plan_code"],
                                "package_name": plan_data["name"],
                                "package_price": plan_data["amount"],
                                "package_description": plan_data["description"],
                                "is_deleted": plan_data["is_deleted"],
                                "package_items": [
                                    item.package_item for item in package_items
                                ],
                            }
                            return package
                        return None
            except Exception as e:
                await session.rollback()
                raise e

    async def update_paystack_plan(self, plan_code, payload):
        try:
            data = {
                "name": payload.name,
                "amount": payload.amount,
                "description": payload.description,
            }

            get_plan = await PackageRepository(self.session_factory).read_by_plan_code(
                plan_code
            )
            if get_plan:
                if get_plan["is_deleted"] is True:
                    raise Exception("Package deleted, update cannot be done.")

                get_plan_code = get_plan["package_plan_code"]

                async with aiohttp.ClientSession() as session:
                    async with session.put(
                        settings.PAYSTACK_PLAN_URL + f"/{get_plan_code}",
                        headers=settings.PAYSTACK_HEADERS,
                        json=data,
                    ) as response:
                        return await response.json()
            return None
        except Exception as e:
            await session.rollback()
            raise e

    async def assign_package_item(self, data: PackageItemAssignmentPayload):
        async with self.session_factory() as session:
            try:
                for item in data.package_item_uuids:
                    result = await session.execute(
                        session.query(PackageItemAssignment).filter(
                            PackageItemAssignment.package_item_uuid == item,
                            PackageItemAssignment.paystack_plan_code
                            == data.package_plan_code,
                        )
                    )
                    db_item = result.scalar()

                    if not db_item:
                        query = PackageItemAssignment(
                            package_item_uuid=item,
                            paystack_plan_code=data.package_plan_code,
                        )
                        session.add(query)
                        await session.commit()
            except exc.IntegrityError as e:
                await session.rollback()
                raise e
            except Exception as e:
                await session.rollback()
                raise e

    async def delete_package_item(self, plan_code: str, package_item_uuid: str):
        async with self.session_factory() as session:
            try:
                result = await session.execute(
                    session.query(PackageItemAssignment).filter(
                        PackageItemAssignment.paystack_plan_code == plan_code,
                        PackageItemAssignment.package_item_uuid == package_item_uuid,
                    )
                )
                db_item = result.scalar()
                if db_item:
                    await session.delete(db_item)
                    await session.commit()
                return db_item
            except Exception as e:
                await session.rollback()
                raise e
