import re

from aiogram.types.reply_keyboard import KeyboardButton
import database
import properties
from datetime import date
from enums import Keys


from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.utils import executor


# configure and run bot
property_file = properties.Properties("config.txt")
bot: Bot = Bot(property_file.get_property("bot_token"))
storage: MemoryStorage = MemoryStorage()
dp: Dispatcher = Dispatcher(bot, storage=storage)


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
    ShowInfo = State()
    AcceptInfo = State()
    ChangeInfo = State()
    Name = State()
    ValidateName = State()
    Birthday = State()
    ValidateBirthday = State()
    PhoneNumber = State()
    ValidateNumber = State()
    OtherInfo = State()
    GetInfo = State()


def cancel_keyboard():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = [Keys.back, Keys.cancel]
    keyboard.add(*buttons)
    return keyboard


@dp.message_handler(lambda msg: msg.text == "Отмена", state="*")
async def cancel(message: types.Message, state: FSMContext):
    await state.finish()
    # TODO: Убрать удаление записи, оставить только возврат на гл. меню (щас костыль)
    database.del_appointment(message.from_user.id)
    await Menu.start_menu.set()
    await start_menu(message, state)


@dp.message_handler(lambda msg: msg.text == "Назад", state="*")
async def back(message: types.Message, state: FSMContext):
    # TODO: Переделать, сделать возврат на пред. стейт
    await Menu.start_menu.set()
    await start_menu(message, state)


@dp.message_handler(commands="start", state="*")
async def cmd_start(message: types.Message, state: FSMContext):
    await message.answer("Добро пожаловать в нашу клинику")
    await Menu.start_menu.set()
    await start_menu(message, state)


@dp.message_handler(state=Menu.start_menu)
async def start_menu(message: types.Message, state: FSMContext):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    buttons = [
        types.KeyboardButton("Хочу записаться"),
        types.KeyboardButton("Посмотреть запись")
        ]
    keyboard.add(*buttons)
    await message.answer("Выберите действие", reply_markup=keyboard)
    await Menu.keyboard_menu.set()


@dp.message_handler(state=Menu.keyboard_menu)
async def callback_start_menu(message: types.Message, state: FSMContext):
    if message.text == "Хочу записаться":
        await Menu.sign_up.set()
        await sign_up(message, state)
    elif message.text == "Посмотреть запись":
        await Menu.show_appointment.set()
        await show_appointment(message, state)


@dp.message_handler(state=Menu.show_appointment)
async def show_appointment(message: types.Message, state: FSMContext):
    if not database.check_client_appointment(message.from_user.id):
        await message.answer("Вы не записывались в клинику")
        await Menu.start_menu.set()
        await start_menu(message, state)
        return
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    buttons = [
        types.InlineKeyboardButton(text="Удалить запись", callback_data="delete_appointment"),
        types.InlineKeyboardButton(text="Назад", callback_data="back")
        ]
    keyboard.add(*buttons)
    await message.answer(database.show_client_appointment(message.from_user.id), reply_markup=keyboard)


@dp.callback_query_handler(lambda call: True, state=Menu.show_appointment)
async def callback_show_appointment(call: types.CallbackQuery, state: FSMContext):
    await call.message.delete_reply_markup()
    await call.answer()
    if call.data == "delete_appointment":
        database.del_appointment(call.from_user.id)
        await call.message.delete()
        await call.message.answer("Запись успешно удалена")
    await Menu.start_menu.set()
    await start_menu(call.message, state)


@dp.message_handler(state=Menu.sign_up)
async def sign_up(message: types.Message, state: FSMContext):
    if database.check_client_appointment(message.from_user.id):
        await message.answer("Вы уже записаны")
        await Menu.start_menu.set()
        await start_menu(message, state)
        return
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    buttons = [
        types.InlineKeyboardButton(text="Я знаю врача", callback_data="know_doctor"),
        types.InlineKeyboardButton(text="Я не знаю врача", callback_data="dont_know_doctor")
        ]
    keyboard.add(*buttons)
    await message.answer("Выберите вариант", reply_markup=keyboard)


@dp.callback_query_handler(lambda call: True, state=Menu.sign_up)
async def callback_sign_up(call: types.CallbackQuery, state: FSMContext):
    if call.data == "know_doctor":
        await Appointment.know_doctor.set()
        await call.message.delete()
        await call.answer()
        await choose_doctor(call, state)
    elif call.data == "dont_know_doctor":
        await Appointment.dont_know_doctor.set()


@dp.message_handler(state=Appointment.know_doctor)
async def choose_doctor(call: types.CallbackQuery, state: FSMContext):
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    doctors_list = database.show_doctors()
    buttons = []
    for doctor in doctors_list:
        buttons.append(types.InlineKeyboardButton(text=doctor, callback_data=doctor))
    keyboard.add(*buttons)
    await call.message.answer("Выберите вашего врача", reply_markup=keyboard)


@dp.callback_query_handler(lambda call: True, state=Appointment.know_doctor)
async def callback_choose_doctor(call: types.CallbackQuery, state: FSMContext):
    await call.message.delete_reply_markup()
    await call.message.edit_text("Ваш врач: " + call.data)
    await call.answer()
    await state.update_data(client_id=call.from_user.id)
    await state.update_data(doctor = call.data)
    await Appointment.set_doctor.set()
    await choose_date(call, state)


@dp.message_handler(state=Appointment.set_doctor)
async def choose_date(call: types.CallbackQuery, state: FSMContext):
    keyboard = types.InlineKeyboardMarkup()
    buttons = [
        types.InlineKeyboardButton(text="01.10", callback_data="01.10"),
        types.InlineKeyboardButton(text="02.10", callback_data="02.10"),
        types.InlineKeyboardButton(text="03.10", callback_data="03.10"),
        types.InlineKeyboardButton(text="04.10", callback_data="04.10"),
        types.InlineKeyboardButton(text="05.10", callback_data="05.10"),
        types.InlineKeyboardButton(text="06.10", callback_data="06.10")
        ]
    keyboard.add(*buttons)
    await call.message.answer("Выберите дату", reply_markup=keyboard)


@dp.callback_query_handler(lambda call: True, state=Appointment.set_doctor)
async def callback_choose_date(call: types.CallbackQuery, state: FSMContext):
    await call.message.delete_reply_markup()
    await call.message.edit_text("Ваша дата: " + call.data)
    await call.answer()
    await state.update_data(date = call.data)
    await Appointment.set_date.set()
    await choose_time(call, state)


@dp.message_handler(state=Appointment.set_date)
async def choose_time(call: types.CallbackQuery, state: FSMContext):
    time_keyboard = types.InlineKeyboardMarkup()
    buttons = [
        types.InlineKeyboardButton(text="00:00", callback_data="00:00"),
        types.InlineKeyboardButton(text="01:00", callback_data="01:00"),
        types.InlineKeyboardButton(text="02:00", callback_data="02:00"),
        types.InlineKeyboardButton(text="03:00", callback_data="03:00"),
        types.InlineKeyboardButton(text="04:00", callback_data="04:00"),
    ]
    time_keyboard.add(*buttons)
    await call.message.answer("Выберите время", reply_markup=time_keyboard)
    

@dp.callback_query_handler(lambda call: True, state=Appointment.set_date)
async def callback_choose_time(call: types.CallbackQuery, state: FSMContext):
    await call.message.delete_reply_markup()
    await call.message.edit_text("Ваше время: " + call.data)
    await call.answer()
    await state.update_data(time = call.data)
    await Appointment.set_time.set()
    await send_appointment(call, state)


@dp.message_handler(state=Appointment.set_time)
async def send_appointment(call: types.CallbackQuery, state: FSMContext):
    database.add_appointment(await state.get_data())
    await state.reset_data()
    await Appointment.add_appointment.set()
    #await message.answer("Запись добавлена")
    await ClientInfo.ShowInfo.set()
    await show_client_info(call, state)


@dp.message_handler(state=ClientInfo.ShowInfo)
async def show_client_info(call: types.CallbackQuery, state: FSMContext):
    if database.check_client_info(call.from_user.id):
        show_info_keyboard = types.InlineKeyboardMarkup(row_width=2)
        buttons = [
            types.InlineKeyboardButton(text = "Изменить", callback_data="change_info"),
            types.InlineKeyboardButton(text = "Принять", callback_data="accept_info")
        ]
        show_info_keyboard.add(*buttons)
        await call.message.answer("Вы уже вводили свои данные\nПроверьте их правильность")
        await call.message.answer(database.show_client_info(call.from_user.id), reply_markup=show_info_keyboard)
    else:
        await ClientInfo.Name.set()
        await request_name(call.message, state)


@dp.callback_query_handler(lambda call: True, state=ClientInfo.ShowInfo)
async def switch_callback_client_info(call: types.CallbackQuery, state: FSMContext):
    await call.message.delete_reply_markup()
    if call.data == "accept_info":
        await ClientInfo.AcceptInfo.set()
        await accept_client_info(call, state)
    elif call.data == "change_info":
        await call.message.delete()
        await ClientInfo.ChangeInfo.set()
        await change_client_info(call, state)


async def accept_client_info(call: types.CallbackQuery, state: FSMContext):
    await call.message.answer("Запись в клинику прошла успешно\nВсего доброго!")
    await call.answer()
    await Menu.start_menu.set()
    await start_menu(call.message, state)


#TODO: Сделать выбор для изменения конкретного поля Клиента
async def change_client_info(call: types.CallbackQuery, state: FSMContext):
    database.del_client(call.from_user.id)
    await call.message.answer("Ваша учетная запись удалена\nВведите данные повторно")
    await call.answer()
    await ClientInfo.Name.set()
    await request_name(call.message, state)


# Обработка ФИО
@dp.message_handler(state=ClientInfo.Name)
async def request_name(message: types.Message, state: FSMContext):
    await message.answer("Введите свое ФИО", reply_markup=cancel_keyboard())
    await ClientInfo.ValidateName.set()


# TODO: Исправить валидацию (не проходит Тест Тест)
@dp.message_handler(lambda message: re.match(r'^[а-яА-Я]+(-[а-яА-Я]+)*$', message.text) is None,
                    state=ClientInfo.ValidateName)
async def wrong_name(message: types.Message, state: FSMContext):
    await message.answer("Некорректный ввод ФИО")
    await ClientInfo.Name.set()
    await request_name(message, state)


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
async def wrong_format_birthday(message: types.Message, state: FSMContext):
    await message.answer("Некорректный ввод даты рождения")
    await ClientInfo.Birthday.set()
    await request_birthday(message, state)


@dp.message_handler(lambda message: re.match(r'^(\d{2}|\d).(\d{2}|\d).(\d{4})$', message.text) is not None,
                    state=ClientInfo.ValidateBirthday)
async def correct_format_birthday(message: types.Message, state: FSMContext):
    res = re.match(r'^(\d{2}|\d).(\d{2}|\d).(\d{4})$', message.text)
    day, month, year = int(res[1]), int(res[2]), int(res[3])

    # Если дата некорректная (30 февраля, 46 марта etc)
    try:
        py_date = date(year, month, day)
        wrong_data = date.today() < py_date
    except ValueError:
        wrong_data = True

    if wrong_data:
        await wrong_format_birthday(message, state)
        return

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
async def wrong_phone(message: types.Message, state: FSMContext):
    await message.answer("Некорректный ввод номера телефона")
    await ClientInfo.PhoneNumber.set()
    await request_phone(message, state)


@dp.message_handler(lambda message: re.match(r'^(\+7|7|8)\s?(\(\s?\d{3}\s?\)|\d{3})\s?\d{7}$',
                                             message.text) is not None,
                    state=ClientInfo.ValidateNumber)
async def correct_phone(message: types.Message, state: FSMContext):
    await state.update_data(tel_num=message.text)
    await ClientInfo.OtherInfo.set()
    await request_info(message, state)


@dp.message_handler(state=ClientInfo.OtherInfo)
async def request_info(message: types.Message, state: FSMContext):
    await message.answer("Введите доп. информацию", reply_markup=cancel_keyboard())
    await ClientInfo.GetInfo.set()


@dp.message_handler(state=ClientInfo.GetInfo)
async def get_info(message: types.Message, state: FSMContext):
    await state.update_data(other_info=message.text)
    await message.answer("Запись в клинику прошла успешно\nВсего доброго!")
    database.add_client(await state.get_data())
    await state.reset_data()
    await Menu.start_menu.set()
    await start_menu(message, state)

executor.start_polling(dp)
