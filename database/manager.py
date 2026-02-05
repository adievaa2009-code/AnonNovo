from sqlalchemy import select, update

from database.session import BaseDatabase
from database.models import Users, Base  # ваша модель

basedatabase = BaseDatabase()

async def adduser(chat_id: int, username: str):
    async with basedatabase.db() as session:
        user = Users(tg_id=chat_id, username=username, status=0)
        session.add(user)
        await session.commit()


async def changestatus(a: int, chat_id: int):
    async with basedatabase.db() as session:
        await session.execute(
            update(Users)
            .where(Users.tg_id == chat_id)
            .values(status=a)
        )
        await session.commit()


async def take1(chat_id: int):
    async with basedatabase.db() as session:
        result = await session.execute(
            select(Users).where(Users.status > 0, Users.tg_id != chat_id)
        )
        return result.scalars().all()


async def getusinf(chat_id: int):
    async with basedatabase.db() as session:
        result = await session.execute(
            select(Users).where(Users.tg_id == chat_id)
        )
        return result.scalars().first()


