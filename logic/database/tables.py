import peewee as pw
from logic.database.database import db


class Client(pw.Model):

    class Meta:
        database = db

    id = pw.IntegerField(unique=True, primary_key=True)
    phone = pw.CharField()
    full_name = pw.CharField()


class Employee(pw.Model):

    class Meta:
        database = db

    id = pw.IntegerField(unique=True, primary_key=True)
    phone = pw.CharField()
    full_name = pw.CharField()


db.create_tables([Client, Employee])
