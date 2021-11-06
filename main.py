import logging

from loader import dp
import handlers

from aiogram import executor


async def on_startup(dispatcher):
    logging.info("Бот запущен")


if __name__ == '__main__':
    print('here')
    executor.start_polling(dp, on_startup=on_startup)



