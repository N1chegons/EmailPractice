import datetime
from pydantic import BaseModel, ConfigDict, Field
from src.entites.models import Rank

class UsersAdd(BaseModel):
    name: str = Field(max_length=30)
    surname: str = Field(max_length=30)
    email: str
    rank: Rank

class UsersRead(UsersAdd):
    added_at: datetime.datetime
    id: int

    model_config = ConfigDict(from_attributes=True)

class UserGetEmail(BaseModel):
    email: str

    model_config = ConfigDict(from_attributes=True)

