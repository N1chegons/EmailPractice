import datetime
import enum
from sqlalchemy import text
from sqlalchemy.orm import Mapped, mapped_column
from src.db import Base

class Rank(str, enum.Enum):
    user = "user"
    manufacturer = "manufacturer"
    support_agent = "support"
    admin = "website admin"

class UsersOrm(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, )
    name: Mapped[str]
    surname: Mapped[str]
    email: Mapped[str]
    rank: Mapped[Rank]
    added_at: Mapped[datetime.datetime] = mapped_column(server_default=text(
        "TIMEZONE('utc', now())"))

class Status(enum.Enum):
    sent = "sent"
    waiting = "waiting"

class MessageOrm(Base):
    __tablename__ = "message"

    id: Mapped[int] = mapped_column(primary_key=True)
    subject: Mapped[str]
    message: Mapped[str]
    status: Mapped[Status] = mapped_column(default=Status.waiting)
    created_at: Mapped[datetime.datetime] = mapped_column(server_default=text(
        "TIMEZONE('utc', now())"))
