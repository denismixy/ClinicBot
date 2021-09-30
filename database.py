
import peewee
import datetime
from peewee import *

db = SqliteDatabase('clinic.db')


class Clients(Model):
<<<<<<< HEAD
    client_id = IntegerField(primary_key=True, unique=True)
    name = CharField()
    birthday = DateField()
    tel_num = IntegerField()
    other_info = CharField()

    class Meta:
        database = db


class Doctors(Model):
    doctor_id = IntegerField(primary_key=True, unique=True)
    name = CharField()

    class Meta:
        database = db


class AppointmentsList(Model):
    client_id = ForeignKeyField(Clients)
    doctor_id = ForeignKeyField(Doctors)
    date_and_time = DateField()

    class Meta:
        database = db


class Holidays(Model):
    date = DateField()
    type = CharField()

    class Meta:
        database = db


class WeekSchedule(Model):
    day = CharField()
    time = CharField()

    class Meta:
        database = db
=======
  client_id = IntegerField(primary_key=True, unique=True)
  name = CharField()
  birthday = DateField()
  tel_num = IntegerField()
  other_info = CharField()

  class Meta:
    database = db


class Doctors(Model):
  doctor_id = IntegerField(primary_key=True, unique=True)
  name = CharField()

  class Meta:
    database = db


class AppointmentsList(Model):
  client_id = ForeignKeyField(Clients)
  doctor_id = ForeignKeyField(Doctors)
  date_and_time = DateField()

  class Meta:
    database = db


class Holidays(Model):
  date = DateField()
  type = CharField()

  class Meta:
    database = db


class WeekSchedule(Model):
  day = CharField()
  time = CharField()

  class Meta:
    database = db
>>>>>>> b7850c218138fc2d65cb40e3461dcd55985115f9


db.connect()
#db.drop_tables([Clients, Doctors, AppointmentsList, Holidays, WeekSchedule])
#db.create_tables([Clients, Doctors, AppointmentsList, Holidays, WeekSchedule])




# add client into DB
def add_client(person) -> None:
<<<<<<< HEAD
    Clients.create(client_id=person.client_id, name=person.name, birthday=person.birthday, tel_num=person.tel_num, other_info=person.other_info)


def check_client_info(id: int) -> bool:
    try:
        client = Clients.get(Clients.client_id == id)
        return True
    except(Exception):
        return False

def check_client_note(id: int) -> bool:
    try:
        note = AppointmentsList.get(AppointmentsList.client_id == id)
        return True
    except(Exception):
        return False
=======
  Clients.create(client_id=person.client_id, name=person.name, birthday=person.birthday, tel_num=person.tel_num, other_info=person.other_info)


def check_client_info(id: int) -> bool:
  try:
    client = Clients.get(Clients.client_id == id)
    return True
  except(Exception):
    return False

def check_client_note(id: int) -> bool:
  try:
    note = AppointmentsList.get(AppointmentsList.client_id == id)
    return True
  except(Exception):
    return False
>>>>>>> b7850c218138fc2d65cb40e3461dcd55985115f9



# show client info
def show_client_info(id: int) -> str:
<<<<<<< HEAD
    client = Clients.get(Clients.client_id == id)
    output = "Подтвердите свои данные:\n"
    output += f"Ваше имя: {client.name}\n"
    output += f"Ваше д\р: {client.birthday}\n"
    output += f"Ваш телефон: {client.tel_num}\n"
    output += f"Доп. инфо: {client.other_info}"
    return output


def show_client_note(id: int) -> str:
    try:
        note = AppointmentsList.get(AppointmentsList.client_id == id)
        client = Clients.get(Clients.client_id == note.client_id)
        doctor = Doctors.get(Doctors.doctor_id == note.doctor_id)
        output = ""
        output += f"Ваше имя: {client.name}\n"
        output += f"Ваш врач: {doctor.name}\n"
        output += f"Ваше время: {note.date_and_time}"
        return output
    except(Exception):
        return 'О вас нет никакой информации'

def add_note(data) -> None:
    AppointmentsList.create(client_id=data[0], doctor_id=Doctors.get(Doctors.name == data[1]), date_and_time=data[2] + ' ' + data[3])
=======
  client = Clients.get(Clients.client_id == id)
  output = "Подтвердите свои данные:\n"
  output += f"Ваше имя: {client.name}\n"
  output += f"Ваше д\р: {client.birthday}\n"
  output += f"Ваш телефон: {client.tel_num}\n"
  output += f"Доп. инфо: {client.other_info}"
  return output


def show_client_note(id: int) -> str:
  try:
    note = AppointmentsList.get(AppointmentsList.client_id == id)
    client = Clients.get(Clients.client_id == note.client_id)
    doctor = Doctors.get(Doctors.doctor_id == note.doctor_id)
    output = ""
    output += f"Ваше имя: {client.name}\n"
    output += f"Ваш врач: {doctor.name}\n"
    output += f"Ваше время: {note.date_and_time}"
    return output
  except(Exception):
    return 'О вас нет никакой информации'

def add_note(data) -> None:
  AppointmentsList.create(client_id=data[0], doctor_id=Doctors.get(Doctors.name == data[1]), date_and_time=data[2] + ' ' + data[3])
>>>>>>> b7850c218138fc2d65cb40e3461dcd55985115f9



def show_doctors() -> list:
<<<<<<< HEAD
    output = []
    for doctor in Doctors.select():
        output.append(doctor.name)
    return output
=======
  output = []
  for doctor in Doctors.select():
    output.append(doctor.name)
  return output
>>>>>>> b7850c218138fc2d65cb40e3461dcd55985115f9
