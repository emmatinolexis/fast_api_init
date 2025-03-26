from pydantic import BaseModel


class TrackingEventBackupSchema(BaseModel):
    start_date: str
    end_date: str
    backup_url: str
