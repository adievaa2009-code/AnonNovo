from aiogram.types import KeyboardButton, ReplyKeyboardMarkup


async def start_kb():
    start_buttons = [
        [
            KeyboardButton(text="Что умеет этот бот? 🤔")
        ]
    ]

    start_buttons_markup = ReplyKeyboardMarkup(
        keyboard=start_buttons, resize_keyboard=True
    )
    return start_buttons_markup
async def search_kb():
    search_buttons = [
        [
            KeyboardButton(text="Найти собеседника")
        ]
    ]

    start_buttons_markup = ReplyKeyboardMarkup(
        keyboard=search_buttons, resize_keyboard=True
    )
    return start_buttons_markup
async def stop_kb():
    stop_buttons = [
        [
            KeyboardButton(text="ВЫЙТИ В МЕНЮ")
        ]
    ]

    start_buttons_markup = ReplyKeyboardMarkup(
        keyboard=stop_buttons, resize_keyboard=True
    )
    return start_buttons_markup
