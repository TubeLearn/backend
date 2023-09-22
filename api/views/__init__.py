from flask import Blueprint

app_view = Blueprint('app_views', __name__, url_prefix='/')

from .users import *
from .courses import *