from sqlmodel import SQLModel, Field

class BaseModel(SQLModel):
    pass

class User(BaseModel, table=True):
    id: int = Field(default=None, nullable=False, primary_key=True)