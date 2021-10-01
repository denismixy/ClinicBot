import aiogram.utils.markdown as md
from aiogram import Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ParseMode, message



class ClientInfo(StatesGroup):
    name = State() 
    birthday = State()
    tel_num = State() 
    other_info = State()






class Client:
    def __init__(self, client_id, name=None, birthday=None, tel_num=None, other_info=None) -> None:
        self.client_id = client_id
        self.name = name
        self.birthday = birthday
        self.tel_num = tel_num
        self.other_info = other_info