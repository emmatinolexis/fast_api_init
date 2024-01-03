from app.core import messages
from app.core.exceptions import NotFoundError
from app.repository.asset_type_repository import AssetTypeRepository
from app.repository.feature_repository import FeatureRepository
from app.repository.onboarding_asset_type_assignment_repository import (
    OnboardingAssetTypeAssignmentRepository,
)
from app.repository.onboarding_feature_assignment_repository import (
    OnboardingFeatureAssignmentRepository,
)
from app.repository.onboarding_repository import OnboardingRepository
from app.repository.package_repository import PackageRepository
from app.repository.user_repository import UserRepository
from app.schema.onboarding_schema import (
    BusinessOnboardingPayload,
    OnboardingAssetTypeAssignment,
    OnboardingBusinessInput,
    OnboardingFeatureAssignment,
    OnboardingIndividualInput,
    OnboardingPayload,
)
from app.service.base_service import BaseService
from app.util.enums import AccountType


class OnboardingService(BaseService):
    def __init__(
        self,
        asset_type_repository: AssetTypeRepository,
        onboarding_repository: OnboardingRepository,
        onboarding_feature_assignment_repository: OnboardingFeatureAssignmentRepository,
        onboarding_asset_type_assignment_repository: OnboardingAssetTypeAssignmentRepository,
        package_repository: PackageRepository,
        user_repository: UserRepository,
        feature_repository: FeatureRepository,
    ):
        self.asset_type_repository = asset_type_repository
        self.onboarding_repository = onboarding_repository
        self.onboading_feature_assignment_repository = (
            onboarding_feature_assignment_repository
        )
        self.onboarding_asset_type_assignment_repository = (
            onboarding_asset_type_assignment_repository
        )
        self.package_repository = package_repository
        self.user_repository = user_repository
        self.feature_repository = feature_repository
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

            for item in onboarding.features_uuid:
                if self.feature_repository.read_by_uuid(item) is None:
                    raise NotFoundError(detail=messages.FEATURE_NOT_FOUND + str(item))

            for item in onboarding.asset_types_uuid:
                if self.asset_type_repository.read_by_uuid(item) is None:
                    raise NotFoundError(detail=messages.ASSET_NOT_FOUND + str(item))

            # create onboarding
            onboarding_item = OnboardingBusinessInput(
                number_of_assets=onboarding.number_of_assets,
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

            # assign asset_type to onboarding
            for item in onboarding.asset_types_uuid:
                asset_type = {
                    "onboarding_uuid": create_onboarding.uuid,
                    "asset_type_uuid": item,
                }
                self.onboarding_asset_type_assignment_repository.create(
                    OnboardingAssetTypeAssignment(**asset_type)
                )

            # update user onboarding status
            self.user_repository.update_user_onboard_status(onboarding.user_uuid)

            return create_onboarding

        except Exception as e:
            raise e
