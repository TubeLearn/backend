from flask import Blueprint

app_view = Blueprint('app_views', __name__, url_prefix='/')

from api.views.users import *
from api.views.courses import *
from api.views.videos import *
from api.views.tests import *