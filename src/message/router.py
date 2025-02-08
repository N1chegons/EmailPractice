from typing import Dict, List
from fastapi import  APIRouter
import resend
from fastapi.params import Depends, Query
from sqlalchemy import select, update, func, delete
from conf import settings
from src.db import async_session
from src.entites.models import UsersOrm, MessageOrm, Status, Rank
from src.message.schemas import MessageCreate, MessageRead

router = APIRouter(
    prefix="/email",
    tags=["Email"]
)
resend.api_key = settings.API_KEY_RESEND


@router.get("/get_email/")
async def get_email_list():
     async with async_session() as session:
         # Подсчет элементов в MessageOrm
         count_waiting = await session.execute(select(func.count()).select_from(MessageOrm).where(MessageOrm.status == Status.waiting))
         count_sent = await session.execute(select(func.count()).select_from(MessageOrm).where(MessageOrm.status==Status.sent))
         count_w = count_waiting.scalar()
         count_s = count_sent.scalar()

         query = select(MessageOrm).order_by(-MessageOrm.id)
         result = await session.execute(query)
         mes_models = result.scalars().all()
         mes_sh = [MessageRead.model_validate(mes_model) for mes_model in mes_models]
         if mes_models:
            return {"info": f"All count Emails:{count_w+count_s}; Waiting emails:{count_w}; Sent emails:{count_s};", "emails":mes_sh}
         else:
             return {"message": "At the moment, there are no emails"}

@router.get("/get_email/{status_email}/")
async def get_email_list(status_email: Status):
     async with async_session() as session:
         # Подсчет элементов в MessageOrm
         count_waiting = await session.execute(select(func.count()).select_from(MessageOrm).where(MessageOrm.status == Status.waiting))
         count_w = count_waiting.scalar()

         query = select(MessageOrm).where(MessageOrm.status==status_email).order_by(-MessageOrm.id)
         result = await session.execute(query)
         mes_models = result.scalars().all()
         mes_sh = [MessageRead.model_validate(mes_model) for mes_model in mes_models]
         if mes_models:
            return {"info": f"All count Waiting emails:{count_w}", "emails":mes_sh}
         else:
             return {"message": "At the moment, there are no emails"}

@router.post("/create_email/")
async def create_email(mes: MessageCreate = Depends()):
     async with async_session() as session:
         mess_d = mes.model_dump()
         mess_s = MessageOrm(**mess_d)
         print(mess_d.get('subject'))
         session.add(mess_s)
         await session.flush()
         await session.commit()
         return {"status": 201, "message": "Email created"}

# noinspection PyTypeChecker,PyBroadException
@router.post("/send_email/{email_id}/{to_whom}/")
async def send_email(email_id: int, to_whom: Rank) -> Dict:
    async with async_session() as session:
        try:
            query = select(MessageOrm.subject).where(MessageOrm.id==email_id)
            query2 = select(UsersOrm.email).where(UsersOrm.rank==to_whom)
            query3 = select(MessageOrm.message).where(MessageOrm.id==email_id)
            res = await session.execute(query)
            res2 = await session.execute(query2)
            res3 = await session.execute(query3)
            mes_subj_models = res.scalars().all()
            user_models = res2.scalars().all()
            mes_mess_models = res3.scalars().all()
            subject = ""
            message = ""
            for subj in mes_subj_models:
                subject=subj
            for mess in mes_mess_models:
                message=mess


            params: List[resend.Emails.SendParams] =[
                {"from": "Ivanich@petproject.website",
                 "to": user_models,
                 "subject": subject,
                 "text": message,
                 }
            ]

            if user_models:
                email: resend.Email = resend.Batch.send(params)
                st = Status.sent
                stmt = (
                    update(MessageOrm)
                    .values(status=st)
                    .filter_by(id=email_id)
                )
                await session.execute(stmt)
                await session.commit()
                return {"status": 200, "email": email}
            else:
                return {"status": 404, "message": "There are no users"}

        except:
            return {"status": 404, "message": f"Email with id:{email_id} not found"}

@router.put("/edit_email/{email_id}/")
async def edit_email(email_id: int, new_subject: str = Query(max_length=50), new_message: str = Query()):
    async with async_session() as session:
        query = select(MessageOrm).where(MessageOrm.id == email_id)
        res = await session.execute(query)
        mes_c = res.scalars().all()
        try:
            if mes_c:
                stmt = (
                    update(MessageOrm)
                    .values(subject=new_subject, message=new_message)
                    .filter_by(id=email_id,status=Status.waiting)
                )
                await session.execute(stmt)
                await session.commit()

                return {
                    "status": 200,
                    "message": "Email edited"
                }
            else:
                return {"status": 404, "message": f"Emails with the id {email_id} were not found"}
        except:
            return {
                "status": 422,
                "Error": "Check the value of the fields, and try again"
            }

@router.delete("/delete_email/{email_id}/")
async def delete_email(email_id: int):
    async with async_session() as session:
        try:
            del_mail = await session.get(MessageOrm, email_id)
            await session.delete(del_mail)
            await session.commit()
            return {
                "status": 200,
                "message": f"Email with {email_id} deleted"
                    }
        except:
            return {
                "status": 404,
                "message": f"Email with {email_id} was not found"
            }

@router.delete("/clear_email_list/")
async def delete_all_emails():
    async with async_session() as session:
        count = await session.execute(select(func.count()).select_from(MessageOrm))
        count_cl = count.scalar()
        try:
            if count_cl > 0:
                stmt = delete(MessageOrm)
                await session.execute(stmt)
                await session.commit()
                return {"status": 200, "message": "Emails list clear"}
            else:
                return{"status": 404, "message": "The list of emails is empty"}
        except:
            return {"status": 404, "message": "Something went wrong..."}
