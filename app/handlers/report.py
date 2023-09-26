from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import Message, MediaGroup
from aiogram.types import InputMediaDocument
import re
import os
from app.db import BotDB

BotDB = BotDB('accountant.db')


def compare_date(date_1, date_2):
    date_1_split, date_2_split = date_1.split('-'), date_2.split('-')
    print(date_1_split, date_2_split)
    if int(date_2_split[0]) > int(date_1_split[0]) or (
            int(date_2_split[1]) > int(date_1_split[1]) and int(date_2_split[0]) == int(date_1_split[0])) or (
            int(date_2_split[2]) >= int(date_1_split[2]) and int(date_2_split[1]) == int(date_1_split[1]) and int(
        date_2_split[0]) == int(date_1_split[0])):
        return False
    return True


def check_structure_date(date_):
    if bool(re.search("^(0[1-9]|1[0-9]|2[0-9]|3[0-1])(.|-)(0[1-9]|1[0-2])(.|-|)20[0-9][0-9]$", date_)):
        return False
    return True


dict_transaction_data = None


class Report(StatesGroup):
    waiting_end_date = State()
    waiting_send_report = State()


async def begin_date(message: types.Message, state: FSMContext):
    await state.set_state(Report.waiting_end_date.state)
    await message.answer("Введите дату начала выписки (dd.mm.yyyy)")


async def end_date(message: types.Message, state: FSMContext):
    if check_structure_date(message.text):
        await message.answer("Значение введено неверно")
        return

    data_message = message.text.split('.')
    readble_begin_data = f"{data_message[2]}-{data_message[1]}-{data_message[0]}"
    await state.update_data(start_date=readble_begin_data)
    await state.set_state(Report.waiting_send_report.state)
    await message.answer("Введите дату конца выписки (dd.mm.yyyy)")


async def send_report(message: types.Message, state: FSMContext):
    if check_structure_date(message.text):
        await message.answer("Значение введено неверно")
        return

    data_message = message.text.split('.')
    begin_data, end_data = await state.get_data(), f"{data_message[2]}-{data_message[1]}-{data_message[0]}"
    if compare_date(begin_data['start_date'], end_data):
        await message.answer("Дата конца выписки меньше чем дата начала")
        return

    await message.answer("Ожидайте несколько секунд")
    lst_data_money = BotDB.get_records(message.from_user.id, begin_data['start_date'], end_data)
    user_info = BotDB.get_user_info(message.from_user.id)
    first_date_registration, first_part_period, second_part_period = user_info[0][1].split('-'), begin_data[
        'start_date'].split('-'), end_data.split('-')
    global dict_transaction_data
    dict_transaction_data = {'name': user_info[0][2],
                             'first_date_registration': f"{first_date_registration[2]}.{first_date_registration[1]}.{first_date_registration[0]}",
                             'first_part_period': f"{first_part_period[2]}.{first_part_period[1]}.{first_part_period[0]}",
                             'second_part_period': f"{second_part_period[2]}.{second_part_period[1]}.{second_part_period[0]}",
                             'number_agreement': '0000000001',
                             'personal_account_number': user_info[0][0],
                             'lst_data_money': lst_data_money}
    print(dict_transaction_data)
    os.system('python create_pdf\create_tinkoff_extract.py')
    media = MediaGroup()
    media.attach(InputMediaDocument(open('D:/Money_keeper_bot/app/create_pdf/result_tinkoff.pdf', 'rb')))
    await message.reply_media_group(media=media)
    await message.answer(f"Выписка c {begin_data['start_date']} до {end_data} успешна!")
    await state.finish()


def register_handlers_report(dp: Dispatcher):
    dp.register_message_handler(begin_date, regexp="Получить выписку из банка")
    dp.register_message_handler(end_date, state=Report.waiting_end_date)
    dp.register_message_handler(send_report, state=Report.waiting_send_report)
