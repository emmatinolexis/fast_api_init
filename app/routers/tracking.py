from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import models, schemas

from app.utils.auth import get_current_user

from .shared import get_db

router = APIRouter(
    prefix="",
    tags=["tracking"],
)


@router.post("/")
async def get_tracker_details(data: dict):
    return data

