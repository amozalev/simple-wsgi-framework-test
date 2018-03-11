import os

DB_NAME = 'sqlite.db'
TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), 'app/templates')
STATIC_FILE_DIR = os.path.join(os.path.dirname(__file__), 'app/static')
STATIC_URL_PREFIX = '/static'
COMMENTS_NUMBER = 5
REGIONS_AND_CITIES = {'Краснодарский край': {'Краснодар', 'Кропоткин', 'Славянск'},
                   'Ростовская область': {'Ростов', 'Шахты', 'Батайск'},
                   'Ставропольский край': {'Ставрополь', 'Пятигорск', 'Кисловодск'}}
