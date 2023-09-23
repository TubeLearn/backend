from mongoengine import *

class Courses(Document):
    title = StringField(required=True)
    description = StringField(required=True)
    length = DecimalField(required=True)
    link = StringField(required=True)
    