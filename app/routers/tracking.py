from typing import List
import logging

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import models, schemas

from app.utils.auth import get_current_user

from .shared import get_db

from typing import Union
from pydantic import BaseModel

class TrackingDeviceCreate(BaseModel):
    data: Union[str, list, dict]

router = APIRouter(
    prefix="",
    tags=["tracking"],
)


@router.post("/")
async def get_tracker_details(data: Union[str, list, dict]):
    print(data)

