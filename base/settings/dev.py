import os
import json
from base.settings.base import *

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_DIR = os.path.join(BASE_DIR, '../db_config/')

db_json = open(os.path.join(CONFIG_DIR, 'database_settings_dev.json')).read()
DATABASES = json.loads(db_json)

CORS_ORIGIN_ALLOW_ALL = True
CORS_ALLOW_CREDENTIALS = True

# MODEL_API_URL = 'http://10.70.201.254:80/model-engine/'
MODEL_API_URL = 'http://10.70.189.6:8090/'
UI_URL = 'http://10.106.6.61:3000/'
ES_LOGURL = "http://dev.innerapi.wehago.com/logsystem/"

FILES_PATH = '/img_labeling/img/'