from datetime import datetime

from fastapi import HTTPException
from pydantic import BaseModel, validator


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
