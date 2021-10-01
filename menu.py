from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ParseMode, message

from appointment import switch_doctor

class Menu(StatesGroup):
    start_menu = State()
    sign_up = State() 
    show_appointment = State()
    choose_doctor = State()

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



def register_handlers_menu(dp: Dispatcher):
    dp.register_message_handler(cmd_start, commands='start', state='*')
    dp.register_message_handler(start_menu, state=Menu.start_menu)
    dp.register_message_handler(sign_up, state=Menu.sign_up)
    dp.register_message_handler(switch_doctor, state=Menu.choose_doctor)