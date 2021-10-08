"""
Copyright "PARTY ON BAAAAAD"
Donate please, NOT LESS 300$
FUCKING SLAVES
STICK UR FINGER IN MY ASS
"""

import re
import database
import properties
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.utils import executor

KEY_BACK = "Назад"
KEY_CANCEL = "Отмена"
storage = None
bot = None
dp = None
property_file = properties.Properties("config.txt")


def init_bot():
    global bot, dp, storage
    bot = Bot(property_file.get_property("bot_token"))
    storage = MemoryStorage()
    dp = Dispatcher(bot, storage=storage)


init_bot()


# =============================КЛАССЫ FSM=================================================
class Menu(StatesGroup):
    start_menu = State()
    keyboard_menu = State()
    sign_up = State()
    show_appointment = State()

    choose_doctor = State()


class Appointment(StatesGroup):
    know_doctor = State()
    dont_know_doctor = State()
    set_doctor = State()
    set_date = State()
    set_time = State()
    add_appointment = State()


class ClientInfo(StatesGroup):
    name = State()
    birthday = State()
    tel_num = State()
    other_info = State()


# =============================ОБЩАЯ КЛАВИАТУРА=================================================
def cancel_keyboard():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    buttons = [KEY_BACK, KEY_CANCEL]
    keyboard.add(*buttons)
    return keyboard


@dp.message_handler(lambda msg: msg.text == "Отмена", state="*")
async def cancel(message: types.Message, state: FSMContext):
    await state.finish()
    database.del_appointment(message.from_user.id)
    await Menu.start_menu.set()
    await start_menu(message)


# =============================МЕНЮ=================================================

@dp.message_handler(commands="start", state="*")
async def cmd_start(message: types.Message):
    await message.answer("Добро пожаловать в нашу клинику")
    await Menu.start_menu.set()
    await start_menu(message)


@dp.message_handler(state=Menu.start_menu)
async def start_menu(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = ["Хочу записаться", "Посмотреть запись"]
    keyboard.add(*buttons)
    await Menu.keyboard_menu.set()
    await message.answer("Выберите действие", reply_markup=keyboard)


@dp.message_handler(state=Menu.keyboard_menu)
async def keyboard_menu(message: types.Message, state: FSMContext):
    if message.text == "Хочу записаться":
        await Menu.sign_up.set()
        await sign_up(message)
    elif message.text == "Посмотреть запись":
        await Menu.show_appointment.set()
        await show_appointment(message)


async def sign_up(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = ["Я знаю врача", "Я не знаю врача"]
    keyboard.add(*buttons)
    keyboard.add(KEY_CANCEL, KEY_BACK)
    await message.answer("Выберите", reply_markup=keyboard)
    await Menu.choose_doctor.set()


async def show_appointment(message: types.Message):
    if not database.check_client_appointment(message.from_user.id):
        await message.answer("Вы не записывались в клинику")
        await start_menu(message)
        return
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    buttons = [KEY_CANCEL, "Удалить запись"]
    keyboard.add(*buttons)
    await message.answer(database.show_client_appointment(message.from_user.id), reply_markup=keyboard)


@dp.message_handler(state=Menu.show_appointment)
async def del_appointment(message: types.Message):
    database.del_appointment(message.from_user.id)
    await message.answer("Запись успешно удалена")
    await start_menu(message)


# ==========================ЗАПИСЬ В ТАБЛИЦУ ЗАПИСЕЙ====================================================
@dp.message_handler(state=Menu.choose_doctor)
async def switch_doctor(message: types.Message, state: FSMContext):
    if message.text == "Я знаю врача":
        await Appointment.know_doctor.set()
        await choose_doctor(message)
    elif message.text == "Я не знаю врача":
        await Appointment.dont_know_doctor.set()


async def choose_doctor(message: types.Message):
    if database.check_client_appointment(message.from_user.id):
        await message.answer("Вы уже записаны")
        await start_menu(message)
        return
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = database.show_doctors()
    keyboard.add(*buttons)
    keyboard.add(KEY_CANCEL, KEY_BACK)
    await message.answer("Выберите вашего врача", reply_markup=keyboard)
    await Appointment.set_doctor.set()


@dp.message_handler(state=Appointment.set_doctor)
async def choose_date(message: types.Message, state: FSMContext):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = ["01.10", "02.10", "03.10", "04.10", "05.10", "06.10", "07.10"]
    keyboard.add(*buttons)
    keyboard.add(KEY_CANCEL, KEY_BACK)
    await state.update_data(client_id=message.from_user.id)
    await state.update_data(doctor=message.text)
    await message.answer("Выберите дату", reply_markup=keyboard)
    await Appointment.set_date.set()


@dp.message_handler(state=Appointment.set_date)
async def choose_time(message: types.Message, state: FSMContext):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    buttons = ["00:00", "01:00", "02:00", "03:00", "04:00"]
    keyboard.add(*buttons)
    keyboard.add(KEY_CANCEL, KEY_BACK)
    await state.update_data(date=message.text)
    await message.answer("Выберите время", reply_markup=keyboard)
    await Appointment.set_time.set()


@dp.message_handler(state=Appointment.set_time)
async def send_appointment(message: types.Message, state: FSMContext):
    await state.update_data(time=message.text)
    database.add_appointment(await state.get_data())
    await state.reset_data()
    await Appointment.add_appointment.set()
    await message.answer("Запись добавлена")
    await input_name(message)


# =================================ЗАПИСЬ ДАННЫХ ЮЗЕРОВ=============================================
async def input_name(message: types.Message):
    if database.check_client_info(message.from_user.id):
        await message.answer("Вы уже вводили свои данные")
        await message.answer(database.show_client_info(message.from_user.id))
        await start_menu(message)
        return
    await message.answer("Введите свое ФИО", reply_markup=cancel_keyboard())
    await ClientInfo.name.set()


@dp.message_handler(state=ClientInfo.name)
async def input_birthday(message: types.Message, state: FSMContext):
    if re.match(r'^[а-яА-Я]+(-[а-яА-Я]+)*$', message.text) is None:
        await message.answer("Некорректный ввод ФИО\nВведите ФИО повторно")
        return
    await message.answer("Введите свой др", reply_markup=cancel_keyboard())
    await state.update_data(client_id=message.from_user.id)
    await state.update_data(name=message.text)
    await ClientInfo.birthday.set()


@dp.message_handler(state=ClientInfo.birthday)
async def input_tel_num(message: types.Message, state: FSMContext):
    if re.match(r'^(\d{2}|\d).(\d{2}|\d).(\d{4})$', message.text) is None:
        await message.answer("Некорректный ввод даты\nВведите дату повторно\nПример: дд.мм.гггг")
        return
    await message.answer("Введите свой телефон", reply_markup=cancel_keyboard())
    await state.update_data(birthday=message.text)
    await ClientInfo.tel_num.set()


@dp.message_handler(state=ClientInfo.tel_num)
async def input_other_info(message: types.Message, state: FSMContext):
    if re.match(r'^(\+7|7|8)\s?(\(\s?\d{3}\s?\)|\d{3})\s?\d{7}$', message.text) is None:
        await message.answer("Некорректный ввод номера\nВведите номер телефона повторно")
        return
    await message.answer("Введите доп. инфо", reply_markup=cancel_keyboard())
    await state.update_data(tel_num=message.text)
    await ClientInfo.other_info.set()


@dp.message_handler(state=ClientInfo.other_info)
async def send_client_info(message: types.Message, state: FSMContext):
    await state.update_data(other_info=message.text)
    database.add_client(await state.get_data())
    await state.reset_data()
    await message.answer("Данные записаны")
    await state.finish()
    await start_menu(message)

executor.start_polling(dp)
