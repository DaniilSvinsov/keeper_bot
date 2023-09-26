from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from app.db import BotDB

variants_active = ['Добавить доход', 'Добавить расход', 'Получить выписку из банка']
BotDB = BotDB('accountant.db')


async def start(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    user_name = message.from_user.first_name if message.from_user.first_name else '' + message.from_user.last_name if message.from_user.last_name else ''
    if not BotDB.user_exists(user_id):
        BotDB.add_user(user_id, user_name)
    await state.finish()
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for name in variants_active:
        keyboard.add(name)
    await message.bot.send_message(message.from_user.id,
                                   "Добро пожаловать!",
                                   reply_markup=keyboard
                                   )


def register_handlers_base(dp: Dispatcher):
    dp.register_message_handler(start, commands="start", state="*")
