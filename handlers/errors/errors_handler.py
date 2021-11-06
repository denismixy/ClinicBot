import logging

from loader import dp
from aiogram.utils.exceptions import TelegramAPIError


@dp.errors_handler()
async def errors_handler(update, exception):
    if isinstance(exception, TelegramAPIError):
        logging.exception(f'TelegramAPIError: {exception} \nUpdate: {update}')
    logging.exception(f'{update}\n{exception}')
    return True
