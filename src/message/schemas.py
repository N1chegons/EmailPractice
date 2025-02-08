import datetime
from pydantic import BaseModel, ConfigDict, Field
from src.entites.models import Status

class MessageCreate(BaseModel):
    subject: str = Field(max_length=50)
    message: str

class MessageRead(MessageCreate):
    created_at: datetime.datetime
    status: Status
    id: int

    model_config = ConfigDict(from_attributes=True)
