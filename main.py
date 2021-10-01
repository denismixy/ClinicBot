'''
Copyright "PARTY ON BAAAAAD"
Donate please, NOT LESS 300$
FUCKING SLAVES
STICK UR FINGER IN MY ASS
'''


import aiogram.utils.markdown as md
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ParseMode, message
from aiogram.utils import executor


import config, database

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

async def cmd_start(message: types.Message):
    await message.answer("Добро пожаловать в нашу клинику")
    await Menu.start_menu.set()
    await start_menu(message)

async def start_menu(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = ['Хочу записаться', 'Посмотреть запись']
    keyboard.add(*buttons)

    await Menu.sign_up.set()
    await message.answer("Выберите действие", reply_markup=keyboard)


async def sign_up(message: types.Message, state: FSMContext):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = ['Я знаю врача', 'Я не знаю врача']
    keyboard.add(*buttons)

    await message.answer('Выберите', reply_markup=keyboard)
    await Menu.choose_doctor.set()


async def show_note(message: types.Message): #СДЕЛАТЬ НАДО
    await Menu.show_appointment.set()
    await message.answer('')


# ==========================ЗАПИСЬ В ТАБЛИЦУ ЗАПИСЕЙ====================================================

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
        await cmd_start(message)
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
    await cmd_start(message)

# =================================КЛАССЫ ОБЪЕКТОВ=============================================

class Client:
    def __init__(self, client_id, name=None, birthday=None, tel_num=None, other_info=None) -> None:
        self.client_id = client_id
        self.name = name
        self.birthday = birthday
        self.tel_num = tel_num
        self.other_info = other_info

# =================================ОБРАБОТЧИКИ=============================================

def register_handlers_menu(dp: Dispatcher):
    dp.register_message_handler(cmd_start, commands='start', state='*')
    dp.register_message_handler(start_menu, state=Menu.start_menu)
    dp.register_message_handler(sign_up, state=Menu.sign_up)
    dp.register_message_handler(switch_doctor, state=Menu.choose_doctor)

def register_handlers_appointment(dp: Dispatcher):
    dp.register_message_handler(choose_doctor, state=Appointment.know_doctor)
    dp.register_message_handler(choose_date, state=Appointment.set_doctor)
    dp.register_message_handler(choose_time, state=Appointment.set_date)
    dp.register_message_handler(send_appointment, state=Appointment.set_time)

# ==============================================================================

def main():
    bot = Bot(token=config.bottoken)

    storage = MemoryStorage()
    dp = Dispatcher(bot, storage=storage)

    register_handlers_menu(dp)
    register_handlers_appointment(dp)
    
    executor.start_polling(dp)

main()
