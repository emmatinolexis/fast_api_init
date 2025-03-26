from datetime import date, datetime
from typing import List, Optional
from uuid import UUID

from fastapi import HTTPException
from pydantic import BaseModel, validator

from app.util.enums import SmartReportStatus, SmartReportType


class DateRange(BaseModel):
    start_date: str
    end_date: str

    @validator("start_date", "end_date")
    def validate_date_format(cls, value):
        try:
            datetime.strptime(value, "%d/%m/%Y")
        except ValueError:
            raise HTTPException(
                status_code=400, detail=f"Date {value} does not match format '%d/%m/%Y'"
            )
        return value


class AssetGroupPayload(BaseModel):
    asset_uuids: List


class SmartReportPayload(BaseModel):
    title: str
    start_date: date
    end_date: date
    asset_group: AssetGroupPayload
    asset_type_uuid: UUID
    user_uuid: UUID
    report_type: List[SmartReportType]


class SmartReportSharePayload(BaseModel):
    user_uuids: List[UUID]


class SmartReportInput(BaseModel):
    title: str
    start_date: str
    end_date: str
    asset_group_uuids: AssetGroupPayload
    asset_type_uuid: UUID
    user_uuid: UUID
    business_profile_uuid: Optional[UUID] = None
    report_types: List[SmartReportType]
    status: SmartReportStatus
