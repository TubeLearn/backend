from mongoengine import *
class Users(Document):
    email = EmailField(required=True, unique=True)
    password = StringField(required=True)
    username = StringField(required=True)