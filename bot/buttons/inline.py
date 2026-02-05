from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
async def choise():
    buttons = [
        [
            InlineKeyboardButton(text="Просто пообщаться", callback_data="choise|1")
        ],
        [
            InlineKeyboardButton(text="Познакомиться, я девушка", callback_data="choise|2")
        ],
        [
            InlineKeyboardButton(text="Познакомиться, я мальчик", callback_data="choise|3")
        ]
    ]

    start_buttons_markup = InlineKeyboardMarkup(
        inline_keyboard=buttons
    )
    return start_buttons_markup
