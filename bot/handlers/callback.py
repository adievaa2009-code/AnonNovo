import random

from aiogram import Router
from aiogram.types import CallbackQuery

from bot.buttons.keyboard import stop_kb
from bot.config import bot
from database.manager import changestatus, take1

callback_router = Router()


@callback_router.callback_query(lambda q: "choise" in q.data)
async def check_query(query: CallbackQuery):
    data = int(query.data[-1]) # "choise|1"
    message = query.message

    await message.answer(
        "Идет пoисk...", reply_markup=await stop_kb()
    )
    await message.delete()
    a = data
    await changestatus(a, message.chat.id)
    freepsort = []
    freep = await take1(message.chat.id)
    if len(freep) > 0:
        #создать список только тех кто подходят по дате если в дате 2 то надо тех у кого 3 фильтр для newapo
        if a==2:
            for per in freep:
                if  per.status==3:
                    freepsort.append(per)

        if a==3:
            for per in freep:
                if per.status==2:
                    freepsort.append(per)

        if a==1:
            for per in freep:
                if per.status==1:
                    freepsort.append(per)
        if freepsort==[]:
            return None
        newapo = random.choice(freepsort).tg_id


        await message.answer(
            "Пользователь найден, иди общайся", reply_markup=await stop_kb()
        )
        a = newapo
        await changestatus(a, message.chat.id)

        await bot.send_message(
            chat_id=newapo, text="Пользователь найден, иди общайся", reply_markup=await stop_kb()
        )
        a = message.chat.id
        await changestatus(a, newapo)