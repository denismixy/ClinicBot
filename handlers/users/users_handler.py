import logging

from aiogram import types
from aiogram.dispatcher.filters.builtin import CommandStart, CommandHelp

from loader import dp


@dp.message_handler(CommandStart)
async def start_user(message: types.Message):
    print('here')
    await message.answer("Привет, пользователь")