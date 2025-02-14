from datetime import datetime, timedelta
from typing import Callable

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import generate_reset_token, hash_user_password
from app.core.settings import setting
from app.model.password_reset import PasswordReset
from app.model.user import User
from app.repository.base_repository import BaseRepository
from sqlalchemy.future import select


class PasswordResetRepository(BaseRepository):
    def __init__(self, session_factory: Callable[..., AsyncSession]):
        self.session_factory = session_factory
        super().__init__(session_factory, PasswordReset)

    async def reset_password(self, user_uuid: str):
        """Asynchronously resets the user's password by generating a new reset token."""
        async with self.session_factory() as session:  # Ensure async session
            current_date = datetime.now()
            password_token = generate_reset_token()

            # Query for existing password reset request
            result = await session.execute(
                select(self.model).filter(self.model.user_uuid == user_uuid)
            )
            reset_token = result.scalars().first()

            if reset_token:
                # Check if the token has expired
                if reset_token.expiry_date < current_date:
                    # Delete old token and create a new one
                    await session.delete(reset_token)
                    await session.commit()

                    new_reset_data = self.model(
                        user_uuid=user_uuid,
                        password_token=password_token,
                        expiry_date=current_date
                        + timedelta(days=setting.PASSWORD_RESET_TOKEN_EXPIRE_DAYS),
                    )
                    session.add(new_reset_data)
                    await session.commit()
                    return password_token
                else:
                    return (
                        reset_token.password_token
                    )  # Return existing token if not expired
            else:
                # Create new password reset entry
                new_reset_data = self.model(
                    user_uuid=user_uuid,
                    password_token=password_token,
                    expiry_date=current_date
                    + timedelta(days=setting.PASSWORD_RESET_TOKEN_EXPIRE_DAYS),
                )
                session.add(new_reset_data)
                await session.commit()
                return password_token

    # def update_password(
    #     self, token: str, new_password: str, password_confirmation: str
    # ):
    #     with self.session_factory() as session:
    #         current_date = datetime.now()

    #         # check if new password and confirm password match
    #         if not new_password == password_confirmation:
    #             raise Exception("New password and confirm password does not match")

    #         # check if token exist
    #         reset_token = (
    #             session.query(self.model)
    #             .filter(self.model.password_token == token)
    #             .first()
    #         )

    #         if not reset_token:
    #             raise Exception("Invalid token provided")

    #         if reset_token.expiry_date < current_date:
    #             raise Exception("Token has expired")

    #         user = (
    #             session.query(User).filter(User.uuid == reset_token.user_uuid).first()
    #         )

    #         if not user:
    #             raise Exception("User not found")

    #         # Update the password with the new hashed password
    #         user.password = hash_user_password(new_password)
    #         session.commit()
    #         session.refresh(user)

    #         return user

    async def update_password(
        self, token: str, new_password: str, password_confirmation: str
    ):
        """Asynchronously updates the user's password after verifying the reset token."""
        async with self.session_factory() as session:
            current_date = datetime.now()

            # Check if new password and confirm password match
            if new_password != password_confirmation:
                raise Exception("New password and confirm password do not match")

            # Check if the reset token exists
            result = await session.execute(
                select(self.model).filter(self.model.password_token == token)
            )
            reset_token = result.scalars().first()

            if not reset_token:
                raise Exception("Invalid token provided")

            # Check if token has expired
            if reset_token.expiry_date < current_date:
                raise Exception("Token has expired")

            # Retrieve the user associated with the reset token
            user_result = await session.execute(
                select(User).filter(User.uuid == reset_token.user_uuid)
            )
            user = user_result.scalars().first()

            if not user:
                raise Exception("User not found")

            # Update the user's password
            user.password = hash_user_password(new_password)

            session.add(user)  # Ensure the user is tracked by the session
            await session.commit()
            await session.refresh(user)

            return user
