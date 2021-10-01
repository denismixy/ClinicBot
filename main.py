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

from menu import register_handlers_menu
from appointment import register_handlers_appointment

import config

class Client(StatesGroup):
    name = State() 
    birthday = State()
    tel_num = State() 
    other_info = State()


def main():
    bot = Bot(token=config.bottoken)

    storage = MemoryStorage()
    dp = Dispatcher(bot, storage=storage)

    register_handlers_menu(dp)
    register_handlers_appointment(dp)
    
    executor.start_polling(dp)

main()

    


