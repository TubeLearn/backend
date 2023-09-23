from mongoengine import *
from bson.objectid import ObjectId

class videos(Document):
    video = ListField(DictField(), default=dict)