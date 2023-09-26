from mongoengine import *


class Videos(Document):
    video = ListField(DictField(), default=dict)
    course_id = StringField(required=True, unique=True)