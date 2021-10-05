'''
Copyright "PARTY ON BAAAAAD"
Donate please, NOT LESS 300$
FUCKING SLAVES
STICK UR FINGER IN MY ASS
'''
import re
import database
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.utils import executor

storage = None
bot = None
dp = None


def search_property(property_name):
    pattern = property_name + r' = "(.*)"'
    result = ""
    with open("config.txt", "r") as config:
        for string in config.readlines():
            if re.search(pattern, string):
                search_result = re.search(pattern, string)
                result = search_result.group(1)
    return result


def init_bot():
    global bot, dp, storage
    bot = Bot(search_property("bot_token"))
    storage = MemoryStorage()
    dp = Dispatcher(bot, storage=storage)


init_bot()
# =============================КЛАССЫ FSM=================================================


class Menu(StatesGroup):
    start_menu = State()
    sign_up = State()
    show_appointment = State()
    choose_doctor = State()


class Appointment(StatesGroup):
    know_doctor = State()
    dont_know_doctor = State()
    set_doctor = State()
    set_date = State()
    set_time = State()


class ClientInfo(StatesGroup):
    name = State()
    birthday = State()
    tel_num = State()
    other_info = State()


# =============================МЕНЮ=================================================
@dp.message_handler(commands='start', state='*')
async def cmd_start(message: types.Message):
    await message.answer("Добро пожаловать в нашу клинику")
    await Menu.start_menu.set()
    await start_menu(message)


@dp.message_handler(state=Menu.start_menu)
async def start_menu(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = ['Хочу записаться', 'Посмотреть запись']
    keyboard.add(*buttons)

    await Menu.sign_up.set()
    await message.answer("Выберите действие", reply_markup=keyboard)


@dp.message_handler(state=Menu.sign_up)
async def sign_up(message: types.Message, state: FSMContext):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = ['Я знаю врача', 'Я не знаю врача']
    keyboard.add(*buttons)

    await message.answer('Выберите', reply_markup=keyboard)
    await Menu.choose_doctor.set()


# TODO
async def show_note(message: types.Message):
    await Menu.show_appointment.set()
    await message.answer('')


# ==========================ЗАПИСЬ В ТАБЛИЦУ ЗАПИСЕЙ====================================================

@dp.message_handler(state=Menu.choose_doctor)
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


@dp.message_handler(state=Appointment.know_doctor)
async def choose_doctor(message: types.Message, state: FSMContext):
    if database.check_client_note(message.from_user.id):
        await message.answer('Вы уже записаны')
        await cmd_start(message)
        return
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = database.show_doctors()
    keyboard.add(*buttons)

    await message.answer('Выберите вашего врача', reply_markup=keyboard)
    await Appointment.set_doctor.set()


@dp.message_handler(state=Appointment.set_doctor)
async def choose_date(message: types.Message, state: FSMContext):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = ['01.10', '02.10', '03.10', '04.10', '05.10', '06.10', '07.10']
    keyboard.add(*buttons)

    await state.update_data(client_id=message.from_user.id)
    await state.update_data(doctor=message.text)

    await message.answer('Выберите дату', reply_markup=keyboard)
    await Appointment.set_date.set()


@dp.message_handler(state=Appointment.set_date)
async def choose_time(message: types.Message, state: FSMContext):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = ['00:00', '01:00', '02:00', '03:00', '04:00']
    keyboard.add(*buttons)

    await state.update_data(date=message.text)
    await message.answer('Выберите время', reply_markup=keyboard)
    await Appointment.set_time.set()


@dp.message_handler(state=Appointment.set_time)
async def send_appointment(message: types.Message, state: FSMContext):
    await state.update_data(time=message.text)
    database.add_note(await state.get_data())
    await state.reset_data()
    await message.answer('Запись добавлена')
    await cmd_start(message)


# =================================КЛАССЫ ОБЪЕКТОВ=============================================

class Client:
    def __init__(self, client_id, name=None, birthday=None, tel_num=None, other_info=None) -> None:
        self.client_id = client_id
        self.name = name
        self.birthday = birthday
        self.tel_num = tel_num
        self.other_info = other_info


executor.start_polling(dp)
