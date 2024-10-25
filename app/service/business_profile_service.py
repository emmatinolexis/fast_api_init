from app.core.constants import FREE_PACKAGE, FREE_PACKAGE_ITEMS
from app.repository.business_profile_repository import BusinessProfileRepository
from app.service.base_service import BaseService
from app.service.package_item_assignments_service import PackageItemAssignmentService
from app.util.enums import SubscriptionStatus


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

    def get_businesses(
        self,
        search_parameter: str = None,
        start_date: str = None,
        end_date: str = None,
        page: int = None,
        page_size: int = None,
    ):
        try:
            businesses_data = []
            businesses = self.business_profile_repository.get_businesses(
                search_parameter, start_date, end_date, page, page_size
            )

            for business in businesses.get("businesses"):
                active_subscription = self.get_active_subscription(business)
                package_features = self.get_package_features(active_subscription)

                data = {
                    "uuid": business.uuid,
                    "customer": business.business_name,
                    "active_plan": active_subscription.plan.get("name")
                    if active_subscription and active_subscription.plan
                    else FREE_PACKAGE,
                    "active_plan_amount": active_subscription.plan.get("amount")
                    if active_subscription else None,
                    "package_features": package_features,
                    "status": "active",
                    "expiry_date": active_subscription.next_payment_date
                    if active_subscription
                    else None,
                    "email": business.business_email,
                    "phone": business.business_phone,
                    "created_at": business.created_at,
                    "subscriptions": self.get_subscription_data(business.subscriptions),
                    "payments": self.get_payment_data(business.payments),
                }

                businesses_data.append(data)

            return {
                "data": businesses_data,
                "current_page": businesses.get("current_page"),
                "page_size": businesses.get("page_size"),
                "total_records": businesses.get("total_records"),
                "total_pages": businesses.get("total_pages"),
                "total_subscriptions": businesses.get("total_subscriptions"),
                "total_active_subscriptions": businesses.get("total_active_subscriptions"),
                "total_inactive_subscriptions": businesses.get("total_inactive_subscriptions"),
            }

        except Exception as e:
            raise e
