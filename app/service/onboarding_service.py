import structlog

from app.core import messages
from app.core.exceptions import NotFoundError
from app.repository.asset_type_repository import AssetTypeRepository
from app.repository.business_profile_repository import BusinessProfileRepository
from app.repository.feature_repository import FeatureRepository
from app.repository.onboarding_feature_assignment_repository import (
    OnboardingFeatureAssignmentRepository,
)
from app.repository.onboarding_repository import OnboardingRepository
from app.repository.package_repository import PackageRepository
from app.repository.user_organisation_assignment_repository import (
    UserOrganisationAssignmentRepository,
)
from app.repository.user_repository import UserRepository
from app.schema.onboarding_schema import (
    BusinessOnboardingPayload,
    BusinessProfile,
    OnboardingBusinessInput,
    OnboardingFeatureAssignment,
    OnboardingIndividualInput,
    OnboardingPayload,
    UserOrganisationAssignment,
)
from app.service.base_service import BaseService
from app.util.enums import AccountType

log = structlog.get_logger()


class OnboardingService(BaseService):
    def __init__(
        self,
        asset_type_repository: AssetTypeRepository,
        onboarding_repository: OnboardingRepository,
        onboarding_feature_assignment_repository: OnboardingFeatureAssignmentRepository,
        business_profile_repository: BusinessProfileRepository,
        package_repository: PackageRepository,
        user_repository: UserRepository,
        feature_repository: FeatureRepository,
        user_organisation_assignment_repository: UserOrganisationAssignmentRepository,
    ):
        self.asset_type_repository = asset_type_repository
        self.onboarding_repository = onboarding_repository
        self.onboading_feature_assignment_repository = (
            onboarding_feature_assignment_repository
        )
        self.business_profile_repository = business_profile_repository
        self.package_repository = package_repository
        self.user_repository = user_repository
        self.feature_repository = feature_repository
        self.user_organisation_assignment_repository = (
            user_organisation_assignment_repository
        )
        super().__init__(onboarding_repository)

    def create_individual_onboarding(self, onboarding: OnboardingPayload):
        try:
            if self.user_repository.read_by_uuid(onboarding.user_uuid) is None:
                raise NotFoundError(
                    detail=messages.USER_NOT_FOUND + str(onboarding.user_uuid)
                )

            if (
                self.asset_type_repository.read_by_uuid(onboarding.asset_type_uuid)
                is None
            ):
                raise NotFoundError(
                    detail=messages.ASSET_TYPE_NOT_FOUND
                    + str(onboarding.asset_type_uuid)
                )

            if self.package_repository.read_by_uuid(onboarding.package_uuid) is None:
                raise NotFoundError(
                    detail=messages.PACKAGE_NOT_FOUND + str(onboarding.package_uuid)
                )

            for item in onboarding.features_uuid:
                if self.feature_repository.read_by_uuid(item) is None:
                    raise NotFoundError(detail=messages.FEATURE_NOT_FOUND + str(item))

            onboarding_item = OnboardingIndividualInput(
                asset_type_uuid=onboarding.asset_type_uuid,
                number_of_assets=onboarding.number_of_assets,
                number_of_months=onboarding.number_of_months,
                package_uuid=onboarding.package_uuid,
                user_uuid=onboarding.user_uuid,
                onboarding_type=AccountType.INDIVIDUAL,
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

            return create_onboarding

        except Exception as e:
            raise e

    def create_business_onboarding(self, onboarding: BusinessOnboardingPayload):
        try:
            if self.user_repository.read_by_uuid(onboarding.user_uuid) is None:
                raise NotFoundError(
                    detail=messages.USER_NOT_FOUND + str(onboarding.user_uuid)
                )

            if (
                self.asset_type_repository.read_by_uuid(onboarding.asset_type_uuid)
                is None
            ):
                raise NotFoundError(
                    detail=messages.ASSET_TYPE_NOT_FOUND
                    + str(onboarding.asset_type_uuid)
                )

            for item in onboarding.features_uuid:
                if self.feature_repository.read_by_uuid(item) is None:
                    raise NotFoundError(detail=messages.FEATURE_NOT_FOUND + str(item))

            # create onboarding
            onboarding_item = OnboardingBusinessInput(
                asset_type_uuid=onboarding.asset_type_uuid,
                number_of_assets=onboarding.number_of_assets,
                number_of_months=onboarding.number_of_months,
                user_uuid=onboarding.user_uuid,
                onboarding_type=AccountType.BUSINESS,
            )

            create_onboarding = self.onboarding_repository.create(onboarding_item)

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
            business_data = BusinessProfile(
                business_name=onboarding.business_name,
                business_email=onboarding.business_email,
                business_phone=onboarding.business_phone,
                business_logo=onboarding.business_logo,
                business_address=onboarding.business_address,
                business_location=onboarding.business_location,
            )
            create_business = self.business_profile_repository.create(business_data)

            # assign user to business
            assignment_data = UserOrganisationAssignment(
                user_uuid=onboarding.user_uuid,
                business_profile_uuid=create_business.uuid,
            )
            self.user_organisation_assignment_repository.create(assignment_data)

            return create_onboarding

        except Exception as e:
            raise e
