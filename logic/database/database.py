import logging
import peewee as pw
from loader import prp

db = pw.SqliteDatabase(prp.get_property("database"))



