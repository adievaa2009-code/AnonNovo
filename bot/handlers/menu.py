import asyncio
import os
import random
import tempfile

from aiogram import Router, F, Bot
from aiogram.types import Message, LabeledPrice, PreCheckoutQuery
from pydub import AudioSegment

from bot.misc.ai import recognizeaudio
from database.manager import changestatus, take1, getusinf
from bot.message_text.text import WHAT_CAN_BOT_DO
from bot.config import config, bot
from bot.buttons.keyboard import stop_kb, start_kb, search_kb
menu_router = Router()

import soundfile as sf




@menu_router.message(F.text == "Найти собеседника")
async def menu_handler(message: Message):
    await message.answer("Идет пoисk...", reply_markup=await stop_kb())
    await changestatus(1, message.chat.id)

    freep = await take1(message.chat.id)
    freepsort = []
    for per in freep:
        if per.status == 1:
            freepsort.append(per)

    if freepsort == []:
        return None

    newapo = random.choice(freepsort).tg_id

    await message.answer(
        "Пользователь найден, иди общайся", reply_markup=await stop_kb()
    )
    await changestatus(newapo, message.chat.id)

    await bot.send_message(
        chat_id=newapo, text="Пользователь найден, иди общайся", reply_markup=await stop_kb()
    )
    await changestatus(message.chat.id, newapo)


@menu_router.message(F.text == "ВЫЙТИ В МЕНЮ")
async def menu_handler(message: Message):
    await message.answer(
        "Вы в меню", reply_markup=await search_kb()
    )
    a=0
    GU =  (await getusinf(message.chat.id)).status
    if GU!=0 and GU!=1:
        await changestatus(a,GU)
        await bot.send_message(
            chat_id=GU,
            text=" собесевашдник покинул чат :(",
            reply_markup=await search_kb()
        )

        prices = [LabeledPrice(label='Узнать кто был собеседником', amount=1)]
        await bot.send_invoice(
            chat_id=GU,
            title='Узнать кто был собеседником',
            description='Деньги не возвращаем',
            currency="XTR",
            provider_token="",
            prices=prices,
            start_parameter='stars-payment',
            payload=str(message.chat.id)
        )
        prices = [LabeledPrice(label='Узнать кто был собеседником', amount=1)]
        await bot.send_invoice(
            chat_id=message.chat.id,
            title='Узнать кто был собеседником',
            description='Деньги не возвращаем',
            currency="XTR",
            provider_token="",
            prices=prices,
            start_parameter='stars-payment',
            payload=str(GU)
        )
    await changestatus(a, message.chat.id)


@menu_router.pre_checkout_query()
async def process_pre_checkout_query(pre_checkout_query: PreCheckoutQuery, bot: Bot) -> None:
    await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)


@menu_router.message(F.successful_payment)
async def process_successful_payment(message: Message) -> None:
    payment_info = message.successful_payment
    transaction_id = payment_info.telegram_payment_charge_id
    payload=payment_info.invoice_payload
    await message.answer(
        text="Ссылка на собеседника: " + f'<a href="tg://user?id={payload}">перейти по ссылке</a>',
    parse_mode="HTML"
    )


@menu_router.message()
async def menu_handler(message: Message):
    GU= (await getusinf(message.chat.id)).status
    if GU!=0 and GU != 1:
        try:
            await message.send_copy(chat_id=GU)
        except:



            if message.voice or message.audio or message.video_note:
                if message.voice :
                    file_id=message.voice.file_id
                elif message.audio:
                    file_id=message.audio.file_id
                elif message.video_note:
                    file_id=message.video_note.file_id

                tg_file = await bot.get_file(file_id)

                # временные файлы
                os.makedirs("downloads", exist_ok=True)
                if message.voice:
                    src_suffix= ".oga"
                elif message.audio:
                    src_suffix=f".{(message.audio.mime_type or 'audio/mpeg').split('/')[-1]}"
                elif message.video_note:
                    src_suffix=".mp4"


                src_path = tempfile.mktemp(prefix="src_", suffix=src_suffix, dir="downloads")
                wav_path = tempfile.mktemp(prefix="out_", suffix=".wav", dir="downloads")

                # скачать исходник
                await bot.download_file(tg_file.file_path, src_path)



                if src_suffix == ".mp4":
                    # извлекаем аудио-дорожку из видео-заметки
                    # -vn: без видео, -ac 1: моно, -ar 16000: 16 кГц, PCM WAV по умолчанию
                    proc = await asyncio.create_subprocess_exec(
                        "ffmpeg", "-y", "-i", src_path, "-vn", "-ac", "1", "-ar", "16000", wav_path,
                        stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
                    )
                    out, err = await proc.communicate()
                    if proc.returncode != 0:
                        raise RuntimeError(f"ffmpeg failed: {err.decode(errors='ignore')}")


                # конвертация -> wav
                else:
                    data, samplerate = sf.read(src_path)
                    sf.write(wav_path, data, samplerate, format='WAV')

                res = recognizeaudio(wav_path)

                await bot.send_message(
                    chat_id=GU, text=res )

                # опционально: удалить временные файлы
                async def cleanup():
                    for p in (src_path, wav_path):
                        try:
                            os.remove(p)
                        except OSError:
                            pass
                asyncio.create_task(cleanup())

        # await bot.send_message(
        #     chat_id=GU,
        #     text=message.text,
        # )

        # Попробовать сделать пересылание фото
