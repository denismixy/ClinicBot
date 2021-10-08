import re
import database
import properties

from typing import Optional

from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.utils import executor

from enums import Keys

# configure and run bot
property_file = properties.Properties("config.txt")
bot: Bot = Bot(property_file.get_property("bot_token"))
storage: MemoryStorage = MemoryStorage()
dp: Dispatcher = Dispatcher(bot, storage=storage)
executor.start_polling(dp)


class Menu(StatesGroup):
    start_menu = State()
    keyboard_menu = State()
    sign_up = State()
    show_appointment = State()
    choose_doctor = State()


class Appointment(StatesGroup):
    know_doctor = State()
    dont_know_doctor = State()
    set_doctor = State()
    set_date = State()
    set_time = State()
    add_appointment = State()


class ClientInfo(StatesGroup):
    Name = State()
    ValidateName = State()
    Birthday = State()
    ValidateBirthday = State()
    PhoneNumber = State()
    ValidateNumber = State()
    OtherInfo = State()
    GetInfo = State()


def cancel_keyboard():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    buttons = [Keys.back, Keys.cancel]
    keyboard.add(*buttons)
    return keyboard


@dp.message_handler(lambda msg: msg.text == "Отмена", state="*")
async def cancel(message: types.Message, state: FSMContext):
    await state.finish()
    database.del_appointment(message.from_user.id)
    await Menu.start_menu.set()
    await start_menu(message)


@dp.message_handler(commands="start", state="*")
async def cmd_start(message: types.Message):
    await message.answer("Добро пожаловать в нашу клинику")
    await Menu.start_menu.set()
    await start_menu(message)


@dp.message_handler(state=Menu.start_menu)
async def start_menu(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = ["Хочу записаться", "Посмотреть запись"]
    keyboard.add(*buttons)
    await Menu.keyboard_menu.set()
    await message.answer("Выберите действие", reply_markup=keyboard)


@dp.message_handler(state=Menu.keyboard_menu)
async def keyboard_menu(message: types.Message, state: FSMContext):
    if message.text == "Хочу записаться":
        await Menu.sign_up.set()
        await sign_up(message)
    elif message.text == "Посмотреть запись":
        await Menu.show_appointment.set()
        await show_appointment(message)


async def sign_up(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = ["Я знаю врача", "Я не знаю врача"]
    keyboard.add(*buttons)
    keyboard.add(Keys.cancel, Keys.back)
    await message.answer("Выберите", reply_markup=keyboard)
    await Menu.choose_doctor.set()


async def show_appointment(message: types.Message):
    if not database.check_client_appointment(message.from_user.id):
        await message.answer("Вы не записывались в клинику")
        await start_menu(message)
        return
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    buttons = [Keys.cancel, "Удалить запись"]
    keyboard.add(*buttons)
    await message.answer(database.show_client_appointment(message.from_user.id), reply_markup=keyboard)


@dp.message_handler(state=Menu.show_appointment)
async def del_appointment(message: types.Message):
    database.del_appointment(message.from_user.id)
    await message.answer("Запись успешно удалена")
    await start_menu(message)


@dp.message_handler(state=Menu.choose_doctor)
async def switch_doctor(message: types.Message, state: FSMContext):
    if message.text == "Я знаю врача":
        await Appointment.know_doctor.set()
        await choose_doctor(message)
    elif message.text == "Я не знаю врача":
        await Appointment.dont_know_doctor.set()


async def choose_doctor(message: types.Message):
    if database.check_client_appointment(message.from_user.id):
        await message.answer("Вы уже записаны")
        await start_menu(message)
        return
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = database.show_doctors()
    keyboard.add(*buttons)
    keyboard.add(Keys.cancel, Keys.back)
    await message.answer("Выберите вашего врача", reply_markup=keyboard)
    await Appointment.set_doctor.set()


@dp.message_handler(state=Appointment.set_doctor)
async def choose_date(message: types.Message, state: FSMContext):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = ["01.10", "02.10", "03.10", "04.10", "05.10", "06.10", "07.10"]
    keyboard.add(*buttons)
    keyboard.add(Keys.cancel, Keys.back)
    await state.update_data(client_id=message.from_user.id)
    await state.update_data(doctor=message.text)
    await message.answer("Выберите дату", reply_markup=keyboard)
    await Appointment.set_date.set()


@dp.message_handler(state=Appointment.set_date)
async def choose_time(message: types.Message, state: FSMContext):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    buttons = ["00:00", "01:00", "02:00", "03:00", "04:00"]
    keyboard.add(*buttons)
    keyboard.add(Keys.cancel, Keys.back)
    await state.update_data(date=message.text)
    await message.answer("Выберите время", reply_markup=keyboard)
    await Appointment.set_time.set()


@dp.message_handler(state=Appointment.set_time)
async def send_appointment(message: types.Message, state: FSMContext):
    await state.update_data(time=message.text)
    database.add_appointment(await state.get_data())
    await state.reset_data()
    await Appointment.add_appointment.set()
    await message.answer("Запись добавлена")
    await ClientInfo.Name.set()
    await request_name(message)

# Обработка ФИО
@dp.message_handler(state=ClientInfo.Name)
async def request_name(message: types.Message):
    if database.check_client_info(message.from_user.id):
        await message.answer("Вы уже вводили свои данные")
        await message.answer(database.show_client_info(message.from_user.id))
        await start_menu(message)
        # TODO: Проверить, хочет ли клиент изменить / посмотреть данные
        return
    await message.answer("Введите свое ФИО", reply_markup=cancel_keyboard())
    await ClientInfo.ValidateName.set()


@dp.message_handler(lambda message: re.match(r'^[а-яА-Я]+(-[а-яА-Я]+)*$', message.text) is None,
                    state=ClientInfo.ValidateName)
async def wrong_name(message: types.Message, state: FSMContext):
    await message.answer("Некорректный ввод ФИО, введите ФИО повторно")
    await ClientInfo.Name.set()


@dp.message_handler(lambda message: re.match(r'^[а-яА-Я]+(-[а-яА-Я]+)*$', message.text) is not None,
                    state=ClientInfo.ValidateName)
async def correct_name(message: types.Message, state: FSMContext):
    await state.update_data(client_id=message.from_user.id, name=message.text)
    await ClientInfo.Birthday.set()
    await request_birthday(message, state)


# Обработка даты рождения
@dp.message_handler(state=ClientInfo.Birthday)
async def request_birthday(message: types.Message, state: FSMContext):
    await message.answer("Введите дату своего рождения (дд.мм.гггг)", reply_markup=cancel_keyboard())
    await ClientInfo.ValidateBirthday.set()


@dp.message_handler(lambda message: re.match(r'^(\d{2}|\d).(\d{2}|\d).(\d{4})$', message.text) is None,
                    state=ClientInfo.ValidateBirthday)
async def wrong_birthday(message: types.Message):
    await message.answer("Некорректный ввод даты рождения, введите повторно")
    await ClientInfo.Birthday.set()


@dp.message_handler(lambda message: re.match(r'^(\d{2}|\d).(\d{2}|\d).(\d{4})$', message.text) is not None,
                    state=ClientInfo.ValidateBirthday)
async def correct_birthday(message: types.Message, state: FSMContext):
    await state.update_data(birthday=message.text)
    await ClientInfo.PhoneNumber.set()
    await request_phone(message, state)


# Обработка телефонного номера
@dp.message_handler(state=ClientInfo.PhoneNumber)
async def request_phone(message: types.Message, state: FSMContext):
    await message.answer("Введите номер телефона", reply_markup=cancel_keyboard())
    await ClientInfo.ValidateNumber.set()


@dp.message_handler(lambda message: re.match(r'^(\+7|7|8)\s?(\(\s?\d{3}\s?\)|\d{3})\s?\d{7}$',
                                             message.text) is None,
                    state=ClientInfo.ValidateNumber)
async def wrong_birthday(message: types.Message):
    await message.answer("Некорректный ввод номера телефона, введите повторно")
    await ClientInfo.PhoneNumber.set()


@dp.message_handler(lambda message: re.match(r'^(\+7|7|8)\s?(\(\s?\d{3}\s?\)|\d{3})\s?\d{7}$',
                                             message.text) is not None,
                    state=ClientInfo.ValidateNumber)
async def correct_birthday(message: types.Message, state: FSMContext):
    await state.update_data(tel_num=message.text)
    await ClientInfo.OtherInfo.set()
    await request_info(message, state)


@dp.message_handler(state=ClientInfo.OtherInfo)
async def request_info(message: types.Message, state: FSMContext):
    await message.answer("Введите доп. информацию", reply_markup=cancel_keyboard())
    await ClientInfo.GetInfo.set()


@dp.message_handler(state=ClientInfo.OtherInfo)
async def get_info(message: types.Message, state: FSMContext):
    await message.answer("Введите доп. информацию", reply_markup=cancel_keyboard())
    await ClientInfo.GetInfo.set()

@dp.message_handler(state=ClientInfo.GetInfo)
async def input_other_info(message: types.Message, state: FSMContext):
    await state.update_data(other_info=message.text)
    if message.text != '':
        await message.answer("Дополнительная информация записана.")
    else:
        await message.answer("Информация введена")


@dp.message_handler(state=ClientInfo.other_info)
async def send_client_info(message: types.Message, state: FSMContext):
    await state.update_data(other_info=message.text)
    database.add_client(await state.get_data())
    await state.reset_data()
    await message.answer("Данные записаны")
    await state.finish()
    await start_menu(message)


