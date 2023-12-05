from app.repository.business_profile_repository import BusinessProfileRepository
from app.repository.onboarding_feature_assignment_repository import (
    OnboardingFeatureAssignmentRepository,
)
from app.repository.onboarding_repository import OnboardingRepository
from app.repository.user_organisation_assignment_repository import (
    UserOrganisationAssignmentRepository,
)
from app.schema.onboarding_schema import (
    BusinessOnboarding,
    BusinessProfile,
    Onboarding,
    OnboardingFeatureAssignment,
    OnboardingInput,
    UserOrganisationAssignment,
)
from app.service.base_service import BaseService
from app.util.enums import AccountType


class OnboardingService(BaseService):
    def __init__(
        self,
        onboarding_repository: OnboardingRepository,
        onboarding_feature_assignment_repository: OnboardingFeatureAssignmentRepository,
        business_profile_repository: BusinessProfileRepository,
        user_organisation_assignment_repository: UserOrganisationAssignmentRepository,
    ):
        self.onboarding_repository = onboarding_repository
        self.onboading_feature_assignment_repository = (
            onboarding_feature_assignment_repository
        )
        self.business_profile_repository = business_profile_repository
        self.user_organisation_assignment_repository = (
            user_organisation_assignment_repository
        )
        super().__init__(onboarding_repository)

    def create_individual_onboarding(self, onboarding: Onboarding):
        try:
            onboarding_item = OnboardingInput(
                {
                    "asset_type_uuid": onboarding.asset_type_uuid,
                    "number_of_assets": onboarding.number_of_assets,
                    "number_of_months": onboarding.number_of_months,
                    "package_uuid": onboarding.package_uuid,
                    "user_uuid": onboarding.user_uuid,
                    "onboarding_type": AccountType.INDIVIDUAL,
                }
            )

            create_onboarding = self.onboarding_repository.create(onboarding_item)

            for item in onboarding.features_uuid:
                feature = {
                    "onboarding_uuid": create_onboarding.uuid,
                    "feature_uuid": item,
                }

                self.onboading_feature_assignment_repository.create(
                    OnboardingFeatureAssignment(**feature)
                )

            return onboarding_item

        except Exception as e:
            raise e

    def create_business_onboarding(self, onboarding: BusinessOnboarding):
        try:
            # create onboarding
            onboarding_data = OnboardingInput(
                {
                    "asset_type_uuid": onboarding.asset_type_uuid,
                    "number_of_assets": onboarding.number_of_assets,
                    "user_uuid": onboarding.user_uuid,
                    "onboarding_type": AccountType.ORGANISATION,
                }
            )

            create_onboarding = self.onboarding_repository(onboarding_data)

            # assign features to onboarding
            for item in onboarding.features_uuid:
                feature = {
                    "onboarding_uuid": create_onboarding.uuid,
                    "feature_uuid": item,
                }
                self.onboading_feature_assignment_repository.create(
                    OnboardingFeatureAssignment(**feature)
                )

            # create business
            business_data = BusinessProfile(**onboarding.dict())
            create_business = self.business_profile_repository.create(business_data)

            # assign user to business
            assignment_data = UserOrganisationAssignment(
                {
                    "user_uuid": onboarding.user_uuid,
                    "business_profile_uuid": create_business.uuid,
                }
            )
            self.user_organisation_assignment_repository.create(assignment_data)

            return onboarding

        except Exception as e:
            raise e
