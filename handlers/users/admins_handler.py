import logging

from aiogram import types
from aiogram.dispatcher.filters.builtin import CommandStart, CommandHelp

from loader import dp
from filters import access_filter


@dp.message_handler(access_filter.EmployeeFilter(), CommandStart())
async def start_user(message: types.Message):
    await message.answer("Администратор")
