import typing

from aiogram import types
from aiogram.dispatcher.filters.filters import BoundFilter

from loader import dp

from logic.database import checkers


class EmployeeFilter(BoundFilter):
    key = "is_employee"

    async def check(self, message: types.Message):
        return checkers.check_employee(message.chat.id)


class ClientFilter(BoundFilter):
    key = "is_client"

    async def check(self, message: types.Message):
        return checkers.check_client(message.chat.id)
