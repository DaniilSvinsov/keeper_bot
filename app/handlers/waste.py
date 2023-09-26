from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from app.db import BotDB

variants_active = ['Добавить доход', 'Добавить расход', 'Получить выписку из банка']
waste_variants = ['Продукты', 'Одежда', 'Рестораны', 'Другое']
BotDB = BotDB('accountant.db')


class Waste(StatesGroup):
    waiting_waste_category = State()
    waiting_waste_add = State()
    waiting_waste_end = State()
    waiting_another = State()


async def chosen_category(message: types.Message, state: FSMContext):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for size in waste_variants:
        keyboard.add(size)
    await state.set_state(Waste.waiting_waste_add.state)
    await message.answer("Выберите категорию", reply_markup=keyboard)


async def add_waste(message: types.Message, state: FSMContext):
    if message.text.capitalize() not in waste_variants:
        await message.answer("Значение введено неверно")
        return
    elif message.text == "Другое":
        await message.answer("Введите название категории")
        await state.set_state(Waste.waiting_another.state)

    else:

        await state.update_data(category=message.text)
        await state.set_state(Waste.waiting_waste_end.state)
        await message.answer("Введите сумму расхода")


async def another_category(message: types.Message, state: FSMContext):
    await state.update_data(category=message.text)
    await state.set_state(Waste.waiting_waste_end.state)
    await message.answer("Введите сумму расхода")


async def waste_end(message: types.Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("Значение введено неверно")
        return
    operation = '-'
    waste_data = await state.get_data()

    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for name in variants_active:
        keyboard.add(name)

    BotDB.add_record(message.from_user.id, operation, message.text, waste_data['category'])
    await message.answer(f"Расход {message.text} ₽ в категории: {waste_data['category']}",
                         reply_markup=keyboard)
    await state.finish()


def register_handlers_waste(dp: Dispatcher):
    dp.register_message_handler(chosen_category, regexp="Добавить расход")
    dp.register_message_handler(add_waste, state=Waste.waiting_waste_add)
    dp.register_message_handler(waste_end, state=Waste.waiting_waste_end)
    dp.register_message_handler(another_category, state=Waste.waiting_another)
