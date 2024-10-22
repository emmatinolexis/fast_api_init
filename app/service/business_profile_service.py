from app.repository.business_profile_repository import BusinessProfileRepository
from app.service.base_service import BaseService
from app.util.enums import SubscriptionStatus


class BusinessProfileService(BaseService):
    def __init__(self, business_profile_repository: BusinessProfileRepository):
        self.business_profile_repository = business_profile_repository
        super().__init__(business_profile_repository)

    def get_businesses(self):
        try:
            businesses_data = []
            businesses = self.business_profile_repository.get_businesses()
            for business in businesses:
                active_subscription = next((sub for sub in business.subscriptions if sub.status == SubscriptionStatus.ACTIVE), None)
                data = {
                    "uuid": business.uuid,
                    "customer": business.business_name,
                    "active_plan": active_subscription.plan.name if active_subscription else None,
                    # "package_features": business.package.package_features,
                    "status": "active",
                    "expiry_date": active_subscription.next_payment_date if active_subscription else None,
                    "email": business.business_email,
                    "phone": business.business_phone,
                    "created_at": business.created_at,
                    "subscriptions": [
                        {
                            "name": sub.plan.get("name") if sub.plan else None,
                            "amount": sub.plan.get("amount") if sub.plan else None,
                            "status": sub.status,
                            "created_at": sub.created_at,
                            "expired_on": sub.next_payment_date
                        }
                        for sub in business.subscriptions
                    ] if business.subscriptions else None ,
                    "payments": [
                        {
                            "amount": py.amount,
                            "status": py.status,
                            "payment_ref": py.reference_no,
                            "created_at": py.created_at,
                            "payment_method": py.channel
                        }
                        for py in business.payments
                    ]

                }
                businesses_data.append(data)
            return businesses_data
        except Exception as e:
            raise e
