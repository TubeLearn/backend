from mongoengine import *
from models.courses import Courses
from bson.objectid import ObjectId

class Videos(Document):
    video = ListField(DictField(), default=dict)
    course_id = ReferenceField(Courses, required=True, unique=True,dbref=ObjectId)