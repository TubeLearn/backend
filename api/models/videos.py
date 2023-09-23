from mongoengine import *

class videos(Document):
    video = ListField(DictField(), default=list)