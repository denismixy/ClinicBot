import logging
import peewee as pw

db = pw.SqliteDatabase('clinic.db')


class Clients(pw.Model):
    client_id = pw.IntegerField(primary_key=True, unique=True)
    name = pw.CharField()
    birthday = pw.DateField()
    tel_num = pw.IntegerField()
    other_info = pw.CharField()

    class Meta:
        database = db


class Doctors(pw.Model):
    doctor_id = pw.IntegerField(primary_key=True, unique=True)
    name = pw.CharField()

    class Meta:
        database = db


class AppointmentsList(pw.Model):
    client_id = pw.ForeignKeyField(Clients)
    doctor_id = pw.ForeignKeyField(Doctors)
    date_and_time = pw.DateField()

    class Meta:
        database = db


class Holidays(pw.Model):
    date = pw.DateField()
    type = pw.CharField()

    class Meta:
        database = db


class WeekSchedule(pw.Model):
    day = pw.CharField()
    time = pw.CharField()

    class Meta:
        database = db


db.connect()
# db.drop_tables([Clients, Doctors, AppointmentsList, Holidays, WeekSchedule])
# db.create_tables([Clients, Doctors, AppointmentsList, Holidays, WeekSchedule])


# add client into DB
def add_client(person) -> None:
    Clients.create(client_id=person.client_id,
                   name=person.name,
                   birthday=person.birthday,
                   tel_num=person.tel_num,
                   other_info=person.other_info)


def check_client_info(id: int) -> bool:
    try:
        Clients.get(Clients.client_id == id)
        return True
    except Exception:
        return False


def check_client_note(id: int) -> bool:
    try:
        AppointmentsList.get(AppointmentsList.client_id == id)
        return True
    except Exception:
        return False


# show client info
def show_client_info(id: int) -> str:
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
    except Exception:
        return 'О вас нет никакой информации'


def add_note(note) -> None:
    AppointmentsList.create(client_id=note['client_id'],
                            doctor_id=Doctors.get(Doctors.name == note['doctor']),
                            date_and_time=note['date'] + ' ' + note['time'])


def show_doctors() -> list:
    output = []
    try:
        for doctor in Doctors.select():
            output.append(doctor.name)
        return output

    except Exception:
        logging.error("Упало обращение к таблице докторов")