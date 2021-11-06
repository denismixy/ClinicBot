from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from properties import Properties

prp: Properties = Properties("properties.json")
bot: Bot = Bot(token=prp.get_property("token"), parse_mode=types.ParseMode.HTML)
storage: MemoryStorage = MemoryStorage()
dp: Dispatcher = Dispatcher(bot, storage=storage)
