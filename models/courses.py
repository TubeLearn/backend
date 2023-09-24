from mongoengine import *

class Courses(Document):
    title = StringField(required=True, unique=True)
    description = StringField(required=True)
    link = StringField(required=True)
    