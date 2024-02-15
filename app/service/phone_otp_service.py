from app.service.base_service import BaseService
from app.repository.phone_otp_repository import PhoneOtpTokenRepository


class PhoneOTPService(BaseService):
    def __init__(self, phone_otp_repository: PhoneOtpTokenRepository):
        self.phone_otp_repository = phone_otp_repository
        super().__init__(phone_otp_repository)

    def create_phone_verification_token(self, user_id: str) -> str:
        return self.phone_otp_repository.create_token(user_id).token
