from fastapi import APIRouter
from fastapi.params import Depends, Query
from pydantic import EmailStr
from sqlalchemy import select, update, func
from src.db import async_session
from src.entites.models import UsersOrm, Rank
from src.users.schemas import UsersRead, UsersAdd

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)

@router.get("/get_users/")
async def get_user_list():
    async with async_session() as session:
        count_user = await session.execute(select(func.count()).select_from(UsersOrm).where(UsersOrm.rank == Rank.user))
        count_manufacturer = await session.execute(select(func.count()).select_from(UsersOrm).where(UsersOrm.rank == Rank.manufacturer))
        support_agent = await session.execute(select(func.count()).select_from(UsersOrm).where(UsersOrm.rank == Rank.support_agent))
        admin = await session.execute(select(func.count()).select_from(UsersOrm).where(UsersOrm.rank == Rank.admin))
        count_u = count_user.scalar()
        count_m = count_manufacturer.scalar()
        count_a = support_agent.scalar()
        count_adm = admin.scalar()


        query = select(UsersOrm).order_by(UsersOrm.rank)
        result = await session.execute(query)
        user_models = result.scalars().all()
        user_sh = [UsersRead.model_validate(task_model) for task_model in user_models]
        return {"info": f"All count Users:{count_u+count_m+count_a+count_adm}",
                "More details:": {
                    "A user with a rank:User": f"{count_u};",
                    "A user with a rank:Manufacturer": f"{count_m}",
                    "A user with a rank:Support Agent":f"{count_a}",
                    "A user with a rank:Admin": f"{count_adm};",
                },
                "users":user_sh}

@router.get("/get_users/{rank_user}/")
async def get_user_list(rank_user: Rank):
    async with async_session() as session:
        count_user = await session.execute(select(func.count()).select_from(UsersOrm).where(UsersOrm.rank == rank_user))
        count_u = count_user.scalar()


        query = select(UsersOrm).filter(UsersOrm.rank==rank_user).order_by(-UsersOrm.id)
        result = await session.execute(query)
        user_models = result.scalars().all()
        user_sh = [UsersRead.model_validate(task_model) for task_model in user_models]
        if user_sh:
            return {"info": f"All count users: {count_u}", "users":user_sh}
        else:
            return {"status": 404, "message": "At the moment, there are no users"}

@router.post("/add_user/")
async def add_user(data: UsersAdd = Depends()):
    async with async_session() as session:
        user_d = data.model_dump()
        r_user = UsersOrm(**user_d)
        session.add(r_user)
        await session.flush()
        await session.commit()
        return {"status": 201, "message": f"User created"}

@router.put("/edit_user/{user_id}")
async def edit_user(user_id: int, new_username: str = Query(max_length=30), new_surname: str = Query(max_length=30), new_email: EmailStr = Query(max_length=256)):
    async with async_session() as session:
        try:
            stmt = (
                update(UsersOrm)
                .values(name=new_username, surname=new_surname, email=new_email)
                .filter_by(id=user_id)
            )
            await session.execute(stmt)
            await session.commit()

            return {
                "status": 200,
                "message": "User edited"
            }
        except:
            return {
                "status": 422,
                "Error": "Check the value of the fields, and try again"
            }

@router.delete("/delete_user/{us_id}/")
async def delete_user(user_id: int):
    async with async_session() as session:
        try:
            del_us = await session.get(UsersOrm, user_id)
            await session.delete(del_us)
            await session.commit()
            return {
                "status": 200,
                "message": f"User with {user_id} deleted"
                    }
        except:
            return {
                "status": 404,
                "message": f"User with {user_id} was not found"
            }
