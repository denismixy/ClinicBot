import aiogram.utils.markdown as md
from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ParseMode, message, user
from aiohttp import client

import database

class Appointment(StatesGroup):
    know_doctor = State()
    dont_know_doctor = State()
    set_doctor = State()
    set_date = State()
    set_time = State()


async def switch_doctor(message: types.Message, state: FSMContext):
    if message.text == 'Я знаю врача':
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.add('Выбрать врача')
        await message.answer('.', reply_markup=keyboard)
        await Appointment.know_doctor.set()
    elif message.text == 'Я не знаю врача':
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.add('Выбрать время')
        await message.answer('.', reply_markup=keyboard)
        await Appointment.dont_know_doctor.set()

async def choose_doctor(message: types.Message, state: FSMContext):
    if database.check_client_note(message.from_user.id):
        await message.answer('Вы уже записаны')
        state.finish()
        return
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = database.show_doctors()
    keyboard.add(*buttons)

    await message.answer('Выберите вашего врача', reply_markup=keyboard)
    await Appointment.set_doctor.set()

async def choose_date(message: types.Message, state: FSMContext):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = ['01.10', '02.10', '03.10', '04.10', '05.10', '06.10', '07.10']
    keyboard.add(*buttons)

    await state.update_data(client_id = message.from_user.id)
    await state.update_data(doctor = message.text)

    await message.answer('Выберите дату', reply_markup=keyboard)
    await Appointment.set_date.set()

async def choose_time(message: types.Message, state: FSMContext):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = ['00:00', '01:00', '02:00', '03:00', '04:00']
    keyboard.add(*buttons)

    await state.update_data(date = message.text)
    await message.answer('Выберите время', reply_markup=keyboard)
    await Appointment.set_time.set()

async def send_appointment(message: types.Message, state: FSMContext):
    await state.update_data(time = message.text)
    database.add_note(await state.get_data())
    await state.reset_data()
    await message.answer('Запись добавлена')

def register_handlers_appointment(dp: Dispatcher):
    dp.register_message_handler(choose_doctor, state=Appointment.know_doctor)
    dp.register_message_handler(choose_date, state=Appointment.set_doctor)
    dp.register_message_handler(choose_time, state=Appointment.set_date)
    dp.register_message_handler(send_appointment, state=Appointment.set_time)
