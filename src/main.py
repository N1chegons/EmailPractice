# noinspection PyUnresolvedReferences
from sqladmin import Admin as Admins
from fastapi import FastAPI
from src.users.router import router as users_router
from src.message.router import router as mes_router
from src.db import async_engine
from src.sqladmin.config import UsersOrmBase, MessageOrmBase

app = FastAPI()
# SQLAdmin
admin = Admins(app, async_engine)

@app.get("/", tags=["Home"])
async def get_home_page():
    return {"status":200, "message": "Welcome!!"}
# SQLAdmin Views
admin.add_view(UsersOrmBase)
admin.add_view(MessageOrmBase)

# Routers
app.include_router(users_router)
app.include_router(mes_router)
