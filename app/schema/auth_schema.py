from typing import Union
from uuid import UUID

from pydantic import BaseModel


class EmailVerification(BaseModel):
    user_uuid: UUID
    verification_token: str
    expiry_date: str

    class ConfigDict:
        from_attributes = True


class UserEmailVerification(BaseModel):
    uuid: str

    class ConfigDict:
        from_attributes = True


class VerifyToken(BaseModel):
    Token: str

    class ConfigDict:
        from_attributes = True


class TokenData(BaseModel):
    username: Union[str, None] = None
    role: Union[str, None] = None


class Token(BaseModel):
    access_token: str
    token_type: str

    class ConfigDict:
        from_attributes = True
