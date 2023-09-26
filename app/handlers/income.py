from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from app.db import BotDB

variants_active = ['Добавить доход', 'Добавить расход', 'Получить выписку из банка']
income_variants = ['Зарплата', 'Продажа', 'Шабашка', 'Другое']
BotDB = BotDB('accountant.db')


class Income(StatesGroup):
    waiting_income_category = State()
    waiting_income_add = State()
    waiting_income_end = State()
    waiting_another = State()


async def chosen_category(message: types.Message, state: FSMContext):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for size in income_variants:
        keyboard.add(size)
    await state.set_state(Income.waiting_income_add.state)
    await message.answer("Выберите категорию", reply_markup=keyboard)


async def add_income(message: types.Message, state: FSMContext):
    if message.text.capitalize() not in income_variants:
        await message.answer("Значение введено неверно")
        return
    elif message.text == 'Другое':
        await message.answer("Введите название категории")
        await state.set_state(Income.waiting_another.state)
    else:
        await state.update_data(category=message.text)
        await state.set_state(Income.waiting_income_end.state)
        await message.answer("Введите сумму дохода")


async def another_category(message: types.Message, state: FSMContext):
    await state.update_data(category=message.text)
    await state.set_state(Income.waiting_income_end.state)
    await message.answer("Введите сумму дохода")


async def income_end(message: types.Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("Значение введено неверно")
        return
    income_data = await state.get_data()
    operation = '+'

    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for name in variants_active:
        keyboard.add(name)

    await message.answer(f"Доход {message.text} ₽ в категории: {income_data['category']}",
                         reply_markup=keyboard)
    BotDB.add_record(message.from_user.id, operation, message.text, income_data['category'])
    await state.finish()


def register_handlers_income(dp: Dispatcher):
    dp.register_message_handler(chosen_category, regexp="Добавить доход")
    dp.register_message_handler(add_income, state=Income.waiting_income_add)
    dp.register_message_handler(income_end, state=Income.waiting_income_end)
    dp.register_message_handler(another_category, state=Income.waiting_another)
