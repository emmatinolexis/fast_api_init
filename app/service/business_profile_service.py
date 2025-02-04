from typing import Dict, Optional

from app.core.constants import FREE_PACKAGE, FREE_PACKAGE_ITEMS
from app.repository.business_profile_repository import BusinessProfileRepository
from app.service.base_service import BaseService
from app.service.package_item_assignments_service import PackageItemAssignmentService
from app.util.enums import ActiveStatus, SubscriptionStatus
from app.util.utils import calculate_percentage_change


class BusinessProfileService(BaseService):
    def __init__(
        self,
        business_profile_repository: BusinessProfileRepository,
        package_item_assignments_service: PackageItemAssignmentService,
    ):
        self.business_profile_repository = business_profile_repository
        self.package_item_assignments_service = package_item_assignments_service
        super().__init__(business_profile_repository)

    def get_active_subscription(self, business):
        """Return the active subscription for a business."""
        return next(
            (
                sub
                for sub in business.subscriptions
                if sub.status == SubscriptionStatus.ACTIVE
            ),
            None,
        )

    def get_package_features(self, active_subscription):
        """Return package features based on the active subscription."""
        if active_subscription and active_subscription.plan:
            features = self.package_item_assignments_service.get_package_items(
                active_subscription.plan.get("plan_code")
            )
            return [{"feature_name": fp.package_item.item_name} for fp in features]
        else:
            # Use FREE_PACKAGE_ITEMS if no active subscription
            return [
                {"feature_name": fp.get("package_item").get("item_name")}
                for fp in FREE_PACKAGE_ITEMS
            ]

    def get_subscription_data(self, subscriptions):
        """Return a list of subscription details."""
        if not subscriptions:
            return None
        return [
            {
                "name": sub.plan.get("name") if sub.plan else None,
                "amount": sub.plan.get("amount") if sub.plan else None,
                "status": sub.status,
                "created_at": sub.created_at,
                "expired_on": sub.next_payment_date,
            }
            for sub in subscriptions
        ]

    def get_payment_data(self, payments):
        """Return a list of payment details."""
        if not payments:
            return []
        return [
            {
                "amount": py.amount,
                "status": py.status,
                "payment_ref": py.reference_no,
                "created_at": py.created_at,
                "payment_method": py.channel,
            }
            for py in payments
        ]

    async def get_businesses(
        self,
        search_parameter: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        page: int = 1,
        page_size: int = 10,
        status: Optional[ActiveStatus] = None,
    ) -> Dict:
        try:
            businesses_result = await self.business_profile_repository.get_businesses(
                search_parameter, start_date, end_date, page, page_size, status
            )

            total_subscriptions = businesses_result.get("total_subscriptions", 0)
            total_active_subscriptions = businesses_result.get(
                "total_active_subscriptions", 0
            )
            total_inactive_subscriptions = businesses_result.get(
                "total_inactive_subscriptions", 0
            )

            previous_total_subscriptions = businesses_result.get(
                "previous_total_subscriptions", 0
            )
            previous_total_active_subscriptions = businesses_result.get(
                "previous_total_active_subscriptions", 0
            )
            previous_total_inactive_subscriptions = businesses_result.get(
                "previous_total_inactive_subscriptions", 0
            )

            percentage_change_total_subscriptions = calculate_percentage_change(
                total_subscriptions, previous_total_subscriptions
            )

            percentage_change_active_subscriptions = calculate_percentage_change(
                total_active_subscriptions, previous_total_active_subscriptions
            )

            percentage_change_inactive_subscriptions = calculate_percentage_change(
                total_inactive_subscriptions, previous_total_inactive_subscriptions
            )

            businesses_result["percentage_change"] = {
                "total_subscriptions": percentage_change_total_subscriptions,
                "total_active_subscriptions": percentage_change_active_subscriptions,
                "total_inactive_subscriptions": percentage_change_inactive_subscriptions,
            }

            businesses_data = []
            for business in businesses_result.get("businesses", []):
                active_subscription = self.get_active_subscription(business)
                package_features = self.get_package_features(active_subscription)

                data = {
                    "uuid": business.uuid,
                    "customer": business.business_name,
                    "active_plan": (
                        active_subscription.plan.get("name")
                        if active_subscription and active_subscription.plan
                        else FREE_PACKAGE
                    ),
                    "active_plan_amount": (
                        active_subscription.plan.get("amount")
                        if active_subscription
                        else None
                    ),
                    "package_features": package_features,
                    "status": "active",
                    "expiry_date": (
                        active_subscription.next_payment_date
                        if active_subscription
                        else None
                    ),
                    "email": business.business_email,
                    "phone": business.business_phone,
                    "created_at": business.created_at,
                    "subscriptions": self.get_subscription_data(business.subscriptions),
                    "payments": self.get_payment_data(business.payments),
                }

                businesses_data.append(data)

            businesses_result["data"] = businesses_data

            del businesses_result["businesses"]

            return businesses_result

        except Exception as e:
            raise e

    async def get_business_by_uuid(self, business_uuid: str):
        try:
            devices = await self.business_profile_repository.get_by_uuid(business_uuid)
            return devices
        except Exception as e:
            raise e
