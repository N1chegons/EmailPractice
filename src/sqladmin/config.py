from sqladmin import ModelView
from src.entites.models import UsersOrm, MessageOrm, Rank


class UsersOrmBase(ModelView, model=UsersOrm):
    name = "User"
    name_plural = "Users"
    icon = "fa-solid fa-user"
    category = "Users List"

    column_list = [UsersOrm.name, UsersOrm.surname]

class MessageOrmBase(ModelView, model=MessageOrm):
    name = "Message"
    name_plural = "Massages"
    icon = "fa-solid fa-message"
    category = "Message List"

    column_list = [MessageOrm.id, MessageOrm.subject]
