from datetime import datetime, timedelta
from typing import List

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, Query, Request
from fastapi.responses import ORJSONResponse
from pydantic import EmailStr

from app.core import messages
from app.core.container import Container
from app.core.dependencies import get_current_user
from app.core.exceptions import (
    ExpiredVerificationCodeError,
    NotFoundError,
    UnAuthorizedError,
)
from app.core.security import extract_user_data, verify_password
from app.core.settings import settings
from app.model.user import User
from app.schema.invitation_schema import (
    InvitationCreatePayload,
    InvitationCreatePayloadSingle,
)
from app.schema.user_schema import (
    AccountDeactivationPayload,
    ResetPasswordPayload,
    UpdateAdminTeamMemberPayload,
    UpdatePhoneNumber,
    UpdateUserAvatar,
    UpdateUserPayload,
    UserPayload,
    UserPhoneVerificationToken,
    UserProfileUdatePayload,
    UserUpdatePassword,
)
from app.service.business_profile_service import BusinessProfileService
from app.service.invitation_service import InvitationService
from app.service.phone_otp_service import PhoneOTPService
from app.service.reset_password_service import ResetPassword
from app.service.role_service import RoleService
from app.service.user_service import UserService
from app.util.email import (
    send_email_invitation,
    send_email_verification,
    send_otp_email,
    send_password_change_email,
)
from app.util.enums import (
    AccountType,
    ActiveStatus,
    EmailPurpose,
    InvitationStatus,
    RoleType,
)
from app.util.utils import (
    allow_admins_only,
    resolve_data_from_request,
    send_client_side_error,
    send_data,
    send_info,
    send_internal_server_error,
    serialize_datetime,
)

router = APIRouter(
    prefix="/users",
    tags=["users"],
)
msg_prefix = "user"


@router.post("/", response_class=ORJSONResponse)
@inject
async def create_user_handler(
    payload: UserPayload,
    service: UserService = Depends(Provide[Container.user_service]),
):
    try:
        found_user = service.get_user_by_email_address(payload.email_address)
        if found_user:
            return send_client_side_error(
                user_msg=f"User already exists : {payload.email_address}",
            )

        # check if business already exist if account type is business
        if payload.account_type == AccountType.BUSINESS:
            found_business = service.check_business_exists(
                payload.business_name, payload.business_email, payload.business_phone
            )
            if found_business:
                return send_client_side_error(
                    user_msg="Business already exists with the same name, email or phone"
                )

        user = service.create_user(payload)
        return send_data(user)
    except Exception as e:
        msg = messages.CREATE_FAILED + msg_prefix
        return send_internal_server_error(user_msg=msg, error=e)


@router.get("/", dependencies=[allow_admins_only], response_class=ORJSONResponse)
@inject
async def get_users(
    service: UserService = Depends(Provide[Container.user_service]),
    current_user: User = Depends(get_current_user),
):
    try:
        users = service.get_list()
        users_info = [extract_user_data(user) for user in users]
        return send_data(users_info)
    except Exception as e:
        msg = messages.GET_FAILED + f"{msg_prefix}s"
        return send_internal_server_error(user_msg=msg, error=e)


@router.get(
    "/admin/accounts", dependencies=[allow_admins_only], response_class=ORJSONResponse
)
@inject
async def get_all_accounts(
    service: UserService = Depends(Provide[Container.user_service]),
    role_uuid: str = None,
    email_address: str = None,
    start_date: str = Query(
        None, description="Start date should be in the format dd/mm/yyyy"
    ),
    end_date: str = Query(
        None, description="End date should be in the format dd/mm/yyyy"
    ),
    page: int = Query(1, ge=1, description="Page number, default is set to 1"),
    page_size: int = Query(
        10, ge=1, le=1000, description="Items per page, default is 10"
    ),
    current_user: User = Depends(get_current_user),
):
    try:
        users = service.get_all_accounts(
            page, page_size, email_address, role_uuid, start_date, end_date
        )
        return send_data(users)
    except Exception as e:
        msg = messages.GET_FAILED + f"{msg_prefix}s"
        return send_internal_server_error(user_msg=msg, error=e)


@router.get(
    "/admin/customers", dependencies=[allow_admins_only], response_class=ORJSONResponse
)
@inject
async def get_all_customers(
    search_parameter: str = None,
    start_date: str = Query(
        None, description="Start date should be in the format dd/mm/yyyy"
    ),
    end_date: str = Query(
        None, description="End date should be in the format dd/mm/yyyy"
    ),
    page: int = Query(1, ge=1, description="Page number, default is set to 1"),
    page_size: int = Query(
        10, ge=1, le=1000, description="Items per page, default is 10"
    ),
    business_service: BusinessProfileService = Depends(
        Provide[Container.business_profile_service]
    ),
    current_user: User = Depends(get_current_user),
):
    try:
        businesses = business_service.get_businesses(
            search_parameter, start_date, end_date, page, page_size
        )

        return send_data(businesses)
    except Exception as e:
        msg = messages.GET_FAILED + f"{msg_prefix}s"
        return send_internal_server_error(user_msg=msg, error=e)


@router.put("/phone", response_class=ORJSONResponse)
@inject
async def update_phone_handler(
    payload: UpdatePhoneNumber,
    service: UserService = Depends(Provide[Container.user_service]),
    phone_otp_service: PhoneOTPService = Depends(Provide[Container.phone_otp_service]),
    current_user: User = Depends(get_current_user),
):
    user = service.get_by_uuid(current_user.uuid)

    if user is None:
        return send_client_side_error(
            user_msg=messages.USER_NOT_FOUND + current_user.uuid,
        )

    user_with_phone_number = service.get_user_by_phone_number(payload.phone_number)

    # check if the given phone number is already associated with another user
    if user_with_phone_number and not (user_with_phone_number.uuid == user.uuid):
        return send_client_side_error(
            user_msg=messages.PHONE_NUMBER_EXISTS + payload.phone_number
        )

    try:
        service.patch_by_uuid(current_user.uuid, payload)
        token = phone_otp_service.create_phone_verification_token(user.uuid)
        await send_otp_email(
            recipient_name=user.first_name,
            email=user.email_address,
            otp=token,
        )
        msg = "Phone number update pending verification"
        return send_info(f"{msg}")
    except Exception as e:
        msg = messages.CREATE_FAILED + f"token for user {current_user.uuid}"
        return send_internal_server_error(user_msg=msg, error=str(e))


@router.put("/{uuid}", response_class=ORJSONResponse)
@inject
async def update_user(
    uuid: str,
    payload: UpdateUserPayload,
    service: UserService = Depends(Provide[Container.user_service]),
    current_user: User = Depends(get_current_user),
):
    try:
        user = service.get_by_uuid(uuid)
        if user is None:
            return send_client_side_error(
                user_msg=messages.USER_NOT_FOUND_MSG,
            )

        user_by_phone = service.get_user_by_phone_number(payload.phone_number)

        if user_by_phone is not None:
            if user.email_address != user_by_phone.get("email_address"):
                return send_client_side_error(
                    user_msg=messages.PHONE_NUMBER_EXISTS,
                )

        service.update_user_by_uuid(uuid, payload)

        return send_info("User updated successfully")
    except UnAuthorizedError as e:
        return send_client_side_error(user_msg=e.detail)
    except Exception as e:
        msg = messages.GET_FAILED + msg_prefix
        return send_internal_server_error(user_msg=msg, error=e)


@router.patch("/{uuid}", response_class=ORJSONResponse)
@inject
async def user_profile_update(
    uuid: str,
    payload: UserProfileUdatePayload,
    service: UserService = Depends(Provide[Container.user_service]),
    current_user: User = Depends(get_current_user),
):
    try:
        user = service.patch_user_by_uuid(uuid, payload)
        if user is None:
            return send_client_side_error(
                user_msg=messages.USER_NOT_FOUND + uuid,
            )
        return send_data(user)
    except Exception as e:
        msg = messages.GET_FAILED + msg_prefix
        return send_internal_server_error(user_msg=msg, error=e)


@router.put("/toggle_status/{uuid}", response_class=ORJSONResponse)
@inject
async def update_user_status(
    uuid: str,
    service: UserService = Depends(Provide[Container.user_service]),
    current_user: User = Depends(get_current_user),
):
    try:
        user = service.update_user_status(uuid)
        if user is None:
            return send_client_side_error(
                user_msg=messages.USER_NOT_FOUND + uuid,
            )
        status_message = f"User status updated to: {user.status}"
        return send_info(status_message)
    except Exception as e:
        msg = messages.GET_FAILED + msg_prefix
        return send_internal_server_error(user_msg=msg, error=e)


@router.get("/{email_address}", response_class=ORJSONResponse)
@inject
async def get_user_by_email(
    email_address: EmailStr,
    service: UserService = Depends(Provide[Container.user_service]),
):
    try:
        user = service.get_user_by_email_address(email_address)
        if user is None:
            return send_client_side_error(
                user_msg=messages.USER_NOT_FOUND + email_address
            )
        return send_data(extract_user_data(user))
    except Exception as e:
        msg = messages.GET_FAILED + msg_prefix
        return send_internal_server_error(user_msg=msg, error=e)


@router.get("/check_user_by_email/{email_address}", response_class=ORJSONResponse)
@inject
async def check_user_exist_by_email(
    email_address: EmailStr,
    service: UserService = Depends(Provide[Container.user_service]),
):
    try:
        user = service.get_user_by_email_address(email_address)
        if user is None:
            return send_data("false")
        return send_data("true")
    except Exception as e:
        msg = messages.GET_FAILED + msg_prefix
        return send_internal_server_error(user_msg=msg, error=e)


@router.get("/{user_uuid}/user", response_class=ORJSONResponse)
@inject
async def get_user_by_uuid_handler(
    user_uuid: str,
    service: UserService = Depends(Provide[Container.user_service]),
    current_user: User = Depends(get_current_user),
):
    try:
        user = service.get_user_by_uuid(user_uuid)
        if user is None:
            return send_client_side_error(user_msg=messages.USER_NOT_FOUND + user_uuid)
        return send_data(user)
    except Exception as e:
        msg = messages.GET_FAILED + msg_prefix
        return send_internal_server_error(user_msg=msg, error=e)


@router.get("/accounts/{business_uuid}", response_class=ORJSONResponse)
@inject
async def user_account(
    business_uuid: str,
    role_uuids: List[str] = Query(None, description="List of role UUIDs"),
    service: UserService = Depends(Provide[Container.user_service]),
    business_service: BusinessProfileService = Depends(
        Provide[Container.business_profile_service]
    ),
    page: int = Query(1, ge=1, description="Page number, default is set to 1"),
    page_size: int = Query(
        10, ge=1, le=1000, description="Items per page, default is 10"
    ),
    search: str = Query(None, description="Email or Name"),
    status: ActiveStatus = Query(None, description="Account Status"),
    current_user: User = Depends(get_current_user),
):
    try:
        business = business_service.get_by_uuid(business_uuid)
        if business is None:
            msg = f"{messages.BUSINESS_PROFILE_NOT_FOUND}{business_uuid}"
            return send_internal_server_error(user_msg=msg, error=msg)
        return send_data(
            service.get_account_users(
                business_uuid, page, page_size, search, role_uuids, status
            )
        )
    except Exception as e:
        msg = messages.GET_FAILED + msg_prefix
        return send_internal_server_error(user_msg=msg, error=e)


@router.put("/password/{user_uuid}", response_class=ORJSONResponse)
@inject
async def change_password_handler(
    user_uuid: str,
    payload: UserUpdatePassword,
    request: Request,
    service: UserService = Depends(Provide[Container.user_service]),
    current_user: User = Depends(get_current_user),
):
    try:
        user_to_update = service.get_by_uuid(user_uuid)
        if user_to_update is None:
            return send_client_side_error(
                user_msg=messages.USER_NOT_FOUND,
            )
        if not payload.new_password == payload.password_confirmation:
            user_msg = "Passwords do not match"
            return send_client_side_error(user_msg=user_msg)

        if not verify_password(payload.old_password, user_to_update.password):
            user_msg = "You have provided an invalid current password"
            return send_client_side_error(
                user_msg=user_msg,
            )

        if verify_password(payload.new_password, user_to_update.password):
            user_msg = "New password and old password cannot be the same"
            return send_client_side_error(
                user_msg=user_msg,
            )

        user = service.change_password(user_uuid, payload.new_password)

        data = resolve_data_from_request(request=request)

        now = datetime.now()

        await send_password_change_email(
            recipient_name=user.get("first_name"),
            email=user.get("email_address"),
            ip_address=data.get("ip_address", "Unknown"),
            user_agent=data.get("user_agent", "Unknown"),
            time_stamp=data.get("timestamp", now.strftime("%B %d, %Y %I:%M %p")),
        )

        return send_info("Password updated successfully")

    except Exception as e:
        msg = messages.GET_FAILED + msg_prefix
        return send_internal_server_error(user_msg=msg, error=e)


@router.post("/password/{email_address}", response_class=ORJSONResponse)
@inject
async def send_password_link_handler(
    email_address: str,
    service: ResetPassword = Depends(Provide[Container.reset_password_service]),
    user_service: UserService = Depends(Provide[Container.user_service]),
):
    try:
        found_user = user_service.get_user_by_email_address(email_address)
        if not found_user:
            return send_client_side_error(
                user_msg=f"Email address : {email_address} does not exist",
            )
        reset_password_token = service.reset_password(found_user.uuid)

        if reset_password_token:
            try:
                # send verification email
                await send_email_verification(
                    recipient_name=found_user.first_name,
                    email=email_address,
                    message=settings.PASSWORD_RESET_MAIL_VERIFICATION_MESSAGE,
                    url=settings.RESET_PASSWORD_URL,
                    btn=settings.RESET_BTN,
                    token=reset_password_token,
                    email_purpose=EmailPurpose.PASSWORD_RESET,
                )
            except Exception as e:
                return send_internal_server_error(
                    user_msg="Could not send password reset email", error=e
                )
            reset_message = f"Password reset link sent to: {email_address}"
            return send_info(reset_message)
        else:
            return send_internal_server_error(
                user_msg="Invalid Token", error="Error sending password reset link"
            )
    except Exception as e:
        msg = messages.GET_FAILED + msg_prefix
        return send_internal_server_error(user_msg=msg, error=e)


@router.post("/password", response_class=ORJSONResponse)
@inject
async def update_password_handler(
    payload: ResetPasswordPayload,
    service: ResetPassword = Depends(Provide[Container.reset_password_service]),
):
    try:
        password_update = service.update_password(
            payload.token, payload.new_password, payload.password_confirmation
        )
        return send_data(password_update)
    except Exception as e:
        msg = messages.GET_FAILED + msg_prefix
        return send_internal_server_error(user_msg=msg, error=e)


@router.put("/avatar/{uuid}", response_class=ORJSONResponse)
@inject
async def update_user_avatar_handler(
    uuid: str,
    payload: UpdateUserAvatar,
    service: UserService = Depends(Provide[Container.user_service]),
):
    try:
        user = service.update_user_avatar(user_id=uuid, avatar_url=payload.avatar_url)
        return send_data(UpdateUserAvatar(avatar_url=user.avatar_url))
    except Exception as e:
        msg = messages.GET_FAILED + msg_prefix
        return send_internal_server_error(user_msg=msg, error=e)


@router.put("/deactivate_account/{uuid}", response_class=ORJSONResponse)
@inject
async def deactivate_account_handler(
    uuid: str,
    payload: AccountDeactivationPayload,
    service: UserService = Depends(Provide[Container.user_service]),
    current_user: User = Depends(get_current_user),
):
    try:
        user = service.deactivate_user_account(uuid, payload)

        if user is None:
            return send_client_side_error(
                user_msg=messages.USER_NOT_FOUND + uuid,
            )
        status_message = "User account deactivated"
        return send_info(status_message)
    except Exception as e:
        msg = messages.GET_FAILED + msg_prefix
        return send_internal_server_error(user_msg=msg, error=e)


@router.post("/businesses/invitations/{user_uuid}", response_class=ORJSONResponse)
@inject
async def create_team_member_invitation(
    user_uuid: str,
    payload: InvitationCreatePayload,
    service: UserService = Depends(Provide[Container.user_service]),
    invitation_service: InvitationService = Depends(
        Provide[Container.invitation_service]
    ),
    role_service: RoleService = Depends(Provide[Container.role_service]),
    current_user: User = Depends(get_current_user),
):
    try:
        for invitation in payload.invitations:
            existing_user = service.get_user_by_email_address(invitation.email)
            if existing_user:
                msg = "User already exist, "
                raise NotFoundError(detail=msg + f" email: {invitation.email}")

            invitation_exists = invitation_service.get_invitation_by_email(
                invitation.email
            )
            if invitation_exists:
                return send_client_side_error(
                    user_msg=f"Invitation already exists for : {invitation.email}",
                )

            user = service.get_by_uuid(user_uuid)
            if not user:
                raise NotFoundError(
                    detail=messages.USER_NOT_FOUND + f" uuid: {str(user_uuid)}"
                )

            invitation_payload = InvitationCreatePayloadSingle(
                email=invitation.email, role_uuid=invitation.role_uuid
            )

            role = role_service.get_by_uuid(str(invitation.role_uuid))
            if role is None:
                return send_client_side_error(
                    user_msg=messages.ROLE_NOT_FOUND,
                )

            created_invite = service.create_team_member_invitation(
                user_uuid, invitation_payload, user
            )

            # send email invite
            await send_email_invitation(
                recipient_name="",
                email=invitation.email,
                invitee_name=f"{user.first_name} {user.last_name}",
                business_profile_uuid=str(user.business_profile_uuid),
                role=str(invitation.role_uuid),
                expiry_date=serialize_datetime(created_invite.expired_at),
                role_type=RoleType.CUSTOMER,
            )
        msg = "Invitations sent successfully"
        return send_info(msg)
    except NotFoundError as e:
        return send_client_side_error(e.detail)
    except Exception as e:
        msg = messages.CREATE_FAILED + "invitation"
        return send_internal_server_error(user_msg=msg, error=str(e))


@router.get("/businesses/invitations/{business_uuid}", response_class=ORJSONResponse)
@inject
async def get_all_user_invitations_by_business_handler(
    business_uuid: str,
    invitation_service: InvitationService = Depends(
        Provide[Container.invitation_service]
    ),
    page: int = Query(1, ge=1, description="Page number, default is set to 1"),
    page_size: int = Query(
        10, ge=1, le=1000, description="Items per page, default is 10"
    ),
    search: str = Query(None, description="Email or Name"),
    role_uuids: List[str] = Query(None, description="Role UUIDs"),
    status: InvitationStatus = Query(None, description="Invitation Status"),
    current_user: User = Depends(get_current_user),
):
    try:
        invitations = invitation_service.get_all_user_invites(
            business_uuid, page, page_size, search, role_uuids, status
        )
        return send_data(invitations)
    except Exception as e:
        msg = messages.GET_FAILED + msg_prefix
        return send_internal_server_error(user_msg=msg, error=e)


@router.post("/phone_verification/{user_uuid}", response_class=ORJSONResponse)
@inject
async def phone_token_verification_handler(
    user_uuid: str,
    payload: UserPhoneVerificationToken,
    service: UserService = Depends(Provide[Container.user_service]),
    phone_otp_service: PhoneOTPService = Depends(Provide[Container.phone_otp_service]),
    current_user: User = Depends(Provide[get_current_user]),
):
    user = service.get_by_uuid(user_uuid)
    if not user:
        return send_client_side_error(
            user_msg=messages.USER_NOT_FOUND + user_uuid,
        )

    try:
        phone_otp_service.verify_token(payload.token)
        msg = msg_prefix + " phone number updated successfully"
        return send_info(info=msg)
    except NotFoundError:
        return send_client_side_error(user_msg=messages.PHONE_OTP_INVALID)
    except ExpiredVerificationCodeError:
        return send_client_side_error(user_msg=messages.PHONE_OTP_EXPIRED)
    except Exception as e:
        msg = messages.PHONE_OTP_FAILED
        return send_client_side_error(user_msg=msg, dev_msg=str(e))


@router.post(
    "/business/invitations/resend/{invitation_uuid}", response_class=ORJSONResponse
)
@inject
async def resend_invitation_handler(
    invitation_uuid: str,
    invitation_service: InvitationService = Depends(
        Provide[Container.invitation_service]
    ),
    current_user: User = Depends(get_current_user),
):
    try:
        invitation = invitation_service.get_by_uuid(invitation_uuid)
        if not invitation:
            return send_client_side_error(
                user_msg=messages.INVITATION_NOT_FOUND + invitation_uuid,
            )

        # make sure the one who is resending the invitation is the inviter
        if invitation.business_profile_uuid != current_user.business_profile_uuid:
            return send_client_side_error(
                user_msg=messages.ACTION_NOT_ALLOWED,
            )

        updated_invite = invitation_service.update_invitation_expiry(
            invitation_uuid, datetime.now() + timedelta(days=3)
        )

        # send email invite
        await send_email_invitation(
            recipient_name="",
            email=invitation.email,
            invitee_name=f"{current_user.first_name} {current_user.last_name}",
            business_profile_uuid=str(invitation.business_profile_uuid),
            role=str(invitation.role_uuid),
            role_type=RoleType.CUSTOMER,
            expiry_date=serialize_datetime(updated_invite.expired_at),
        )

        msg = "Invitation resent successfully"
        return send_info(msg)
    except Exception as e:
        msg = messages.CREATE_FAILED + "invitation"
        return send_internal_server_error(user_msg=msg, error=str(e))


@router.post(
    "/admin/invitations",
    dependencies=[allow_admins_only],
    response_class=ORJSONResponse,
)
@inject
async def create_admin_user_invitation(
    payload: InvitationCreatePayload,
    service: UserService = Depends(Provide[Container.user_service]),
    invitation_service: InvitationService = Depends(
        Provide[Container.invitation_service]
    ),
    role_service: RoleService = Depends(Provide[Container.role_service]),
    current_user: User = Depends(get_current_user),
):
    try:
        for invitation in payload.invitations:
            existing_user = service.get_user_by_email_address(invitation.email)
            if existing_user:
                msg = "User already exist, "
                raise NotFoundError(detail=msg + f" email: {invitation.email}")

            invitation_exists = invitation_service.get_invitation_by_email(
                invitation.email
            )
            if invitation_exists:
                return send_client_side_error(
                    user_msg=f"Invitation already exists for : {invitation.email}",
                )

            role = role_service.get_by_uuid(str(invitation.role_uuid))
            if role is None:
                return send_client_side_error(
                    user_msg=messages.ROLE_NOT_FOUND,
                )

            invitation_payload = InvitationCreatePayloadSingle(
                email=invitation.email, role_uuid=invitation.role_uuid
            )

            created_invite = service.create_admin_user_invitation(invitation_payload)

            # send email invite
            await send_email_invitation(
                recipient_name="",
                email=invitation.email,
                invitee_name=f"{current_user.first_name} {current_user.last_name}",
                role=str(invitation.role_uuid),
                role_type=RoleType.ADMIN,
                expiry_date=serialize_datetime(created_invite.expired_at),
            )
        msg = "Invitations sent successfully"
        return send_info(msg)
    except NotFoundError as e:
        return send_client_side_error(e.detail)
    except Exception as e:
        msg = messages.CREATE_FAILED + "invitation"
        return send_internal_server_error(user_msg=msg, error=str(e))


@router.get(
    "/admin/invitations/",
    dependencies=[allow_admins_only],
    response_class=ORJSONResponse,
)
@inject
async def get_all_user_invitations_handler(
    email: str = None,
    role_uuids: List[str] = Query(None, description="List of role UUIDs"),
    invitation_service: InvitationService = Depends(
        Provide[Container.invitation_service]
    ),
    page: int = Query(1, ge=1, description="Page number, default is set to 1"),
    page_size: int = Query(
        10, ge=1, le=1000, description="Items per page, default is 10"
    ),
    current_user: User = Depends(get_current_user),
):
    try:
        invitations = invitation_service.get_all_admin_invites(
            page, page_size, email, role_uuids
        )
        return send_data(invitations)
    except Exception as e:
        msg = messages.GET_FAILED + msg_prefix
        return send_internal_server_error(user_msg=msg, error=e)


@router.delete(
    "/admin/invitations/{invite_uuid}",
    dependencies=[allow_admins_only],
    response_class=ORJSONResponse,
)
@inject
async def delete_admin_invite_handler(
    invite_uuid: str,
    invitation_service: InvitationService = Depends(
        Provide[Container.invitation_service]
    ),
    current_user: User = Depends(get_current_user),
):
    try:
        invitation_service.remove_by_uuid(invite_uuid)
        return send_info(messages.DELETE_SUCCESS)
    except Exception as e:
        msg = messages.GET_FAILED + msg_prefix
        return send_internal_server_error(user_msg=msg, error=e)


@router.get(
    "/admin/invitations/resend/{invitation_uuid}",
    dependencies=[allow_admins_only],
    response_class=ORJSONResponse,
)
@inject
async def resend_admin_invitation_handler(
    invitation_uuid: str,
    invitation_service: InvitationService = Depends(
        Provide[Container.invitation_service]
    ),
    current_user: User = Depends(get_current_user),
):
    try:
        invitation = invitation_service.get_by_uuid(invitation_uuid)
        if not invitation:
            return send_client_side_error(
                user_msg=messages.INVITATION_NOT_FOUND + invitation_uuid,
            )

        updated_invite = invitation_service.update_invitation_expiry(
            invitation_uuid, datetime.now() + timedelta(days=3)
        )

        # send email invite
        await send_email_invitation(
            recipient_name="",
            email=updated_invite.email,
            invitee_name=f"{current_user.first_name} {current_user.last_name}",
            role=str(updated_invite.role_uuid),
            role_type=RoleType.ADMIN,
            expiry_date=serialize_datetime(updated_invite.expired_at),
        )

        msg = "Invitation resent successfully"
        return send_info(msg)
    except Exception as e:
        msg = messages.CREATE_FAILED + "invitation"
        return send_internal_server_error(user_msg=msg, error=str(e))


@router.get(
    "/admin/team_members",
    dependencies=[allow_admins_only],
    response_class=ORJSONResponse,
)
@inject
async def get_all_admin_team_members_handler(
    email: str = None,
    role_uuid: str = None,
    user_service: UserService = Depends(Provide[Container.user_service]),
    page: int = Query(1, ge=1, description="Page number, default is set to 1"),
    page_size: int = Query(
        10, ge=1, le=1000, description="Items per page, default is 10"
    ),
    current_user: User = Depends(get_current_user),
):
    try:
        team_members = user_service.get_all_admin_team_members(
            page=page, page_size=page_size, email=email, role_uuid=role_uuid
        )
        return send_data(team_members)
    except Exception as e:
        msg = messages.GET_FAILED + msg_prefix
        return send_internal_server_error(user_msg=msg, error=e)


@router.get(
    "/admin/team_members/{team_member_uuid}",
    dependencies=[allow_admins_only],
    response_class=ORJSONResponse,
)
@inject
async def get_team_member_handler(
    team_member_uuid: str,
    user_service: UserService = Depends(Provide[Container.user_service]),
    current_user: User = Depends(get_current_user),
):
    try:
        team_member = user_service.get_admin_team_member(team_member_uuid)
        return send_data(team_member)
    except Exception as e:
        msg = messages.GET_FAILED + msg_prefix
        return send_internal_server_error(user_msg=msg, error=e)


@router.patch(
    "/admin/team_members/{team_member_uuid}",
    response_class=ORJSONResponse,
)
@inject
async def update_team_member_handler(
    team_member_uuid: str,
    payload: UpdateAdminTeamMemberPayload,
    user_service: UserService = Depends(Provide[Container.user_service]),
    current_user: User = Depends(get_current_user),
):
    try:
        user_service.patch_by_uuid(team_member_uuid, payload)
        return send_info(messages.UPDATE_SUCCESS)
    except Exception as e:
        msg = messages.GET_FAILED + msg_prefix
        return send_internal_server_error(user_msg=msg, error=e)
