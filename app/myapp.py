import json
import os
# import re
from .templating import template_render
import urllib.parse
import sqlite3
import config


class MyApp:
    def __init__(self):
        self.routes = {}
        self.headers = {}
        self.status = '200 OK'
        self.MIME_TABLE = {'.txt': 'text/plain',
                           '.html': 'text/html',
                           '.css': 'text/css',
                           '.js': 'application/javascript',
                           }

        try:
            self.db = sqlite3.connect('sqlite.db')
        except sqlite3.Error as e:
            print('sqlite3.Error during db connection:', e)

    def __call__(self, environ, start_response):
        body = self.serve(environ, start_response)

        # self.headers['Content-length'] = str(len(body))
        start_response(self.status, list(self.headers.items()))
        return body

    # def route(self, route):
    #     def wrapper(func):
    #         self.routes[route] = func
    #         return func
    #
    #     return wrapper

    def index(self, environ, start_response):
        print('index')
        self.headers['Content-Type'] = 'text/html'
        return template_render('index.html')

    def comment(self, environ, start_response):
        # Отображение формы ввода комментариев
        print('comment')
        raw_data = {}

        cursor = self.db.cursor()
        query = ('''SELECT r.name, c.name 
                    FROM city c
                    JOIN region r ON c.region_id = r.id
                    ORDER BY r.name''')

        try:
            for i in cursor.execute(query):
                if i[0] not in raw_data:
                    arr = []
                    raw_data[i[0]] = arr
                raw_data[i[0]].append(i[1])

        except sqlite3.Error as e:
            print('sqlite3.Error during request of existing regions and cities:', e)

        mapping_dict = {"data": json.dumps(raw_data, ensure_ascii=False)}

        self.headers['Content-Type'] = 'text/html'
        return template_render('comment.html', mapping_dict)

    def view(self, environ, start_response):
        # Отображение комментариев
        print('view func')
        # data = {"Hello World": 2}
        # body = json.dumps(data, sort_keys=True, indent=4).encode("utf-8")

        cursor = self.db.cursor()
        query = ('''SELECT c.body, u.name, u.surname, u.patronymic_name, c.id
                    FROM comment c
                    JOIN user u ON u.id = c.user_id
                    ORDER BY 1''')

        mapping_dict = {}
        mapping_dict['table'] = ''
        mapping_dict[
            'table'] += '<table class="table table-striped table-bordered"><tr><th></th><th>ФИО</th><th>Комментарий</th></tr>'
        try:
            for i in cursor.execute(query):
                mapping_dict[
                    'table'] += '<tr><td><input name="commentid_{}" type="checkbox"/></td><td>{} {} {}</td><td>{}</td></tr>'. \
                    format(i[4], i[1], i[2], i[3], i[0])
        except sqlite3.Error as e:
            print('sqlite3.Error during request of existing comments:', e)

        mapping_dict['table'] += '</table>'

        self.headers['Content-Type'] = 'text/html'
        return template_render('view.html', mapping_dict)

    def stat(self, environ, start_response):
        # Отображение таблица со списком тех регионов, у которых количество комментариев больше 5,
        print('stats')
        return 'view comments function'

    # def cities_of_region(self, environ, start_response):
    #     # self.is_post_request(environ, start_response)
    #     if environ['REQUEST_METHOD'] != 'POST':
    #         self.show_404(environ, start_response)
    #
    #     # for i in environ.items():
    #     #     print(i)
    #
    #     try:
    #         request_body_size = int(environ.get('CONTENT_LENGTH', 0))
    #     except ValueError:
    #         request_body_size = 0
    #     request_body = str(environ['wsgi.input'].read(request_body_size))
    #     body = urllib.parse.parse_qs(request_body, keep_blank_values=True, encoding='utf-8')
    #
    #     print('========', body)
    #
    #     data = {'success': True}
    #     body = json.dumps(data, sort_keys=True, indent=4).encode("utf-8")
    #
    #     self.headers['Content-Type'] = 'application/json'
    #     return [body]

    def save_comment(self, environ, start_response):
        if environ['REQUEST_METHOD'] != 'POST':
            self.show_404(environ, start_response)

        try:
            request_body_size = int(environ.get('CONTENT_LENGTH', 0))
        except ValueError:
            request_body_size = 0
        request_body = str(environ['wsgi.input'].read(request_body_size))
        body = urllib.parse.parse_qs(request_body, keep_blank_values=True, encoding='utf-8')

        data = {}
        for i in body:
            data[i.replace('b\'', '')] = body[i][0]

        if ('surname', 'name', 'region', 'comment') in data:
            # ---------------------- Проверка наличия пользователя. Если нет, то добавление ---------------
            cursor = self.db.cursor()
            try:
                cursor.execute('SELECT id FROM user WHERE surname = ? AND name = ?',
                               (data["surname"], data["name"]))
                self.db.commit()
            except sqlite3.Error as e:
                self.db.rollback()
                print('sqlite3.Error during user existence check:', e)

            if cursor.fetchone() is None:
                # ---------------------- Получение id города---------------------
                try:
                    cursor.execute('''SELECT city.id
                                      FROM city
                                      JOIN region ON city.region_id = region.id
                                      WHERE city.name = ? AND region.name = ?''',
                                   (data["city"], data["region"]))
                    self.db.commit()
                except sqlite3.Error as e:
                    self.db.rollback()
                    print('sqlite3.Error during city existence check:', e)

                city_id = cursor.fetchone()[0]

                # ---------------------- Сохранение нового пользователя ---------------------
                try:
                    cursor.execute('''INSERT INTO user(surname, name, patronymic_name, phone, email, city_id)
                                        VALUES (?, ?, ?, ?, ?, ?)''',
                                   (data["surname"],
                                    data["name"],
                                    data["patronymic_name"],
                                    data["phone"],
                                    data["email"],
                                    city_id))
                    self.db.commit()
                except sqlite3.Error as e:
                    self.db.rollback()
                    print('sqlite3.Error during user insert:', e)

            try:
                cursor.execute('SELECT id FROM user WHERE surname = ? AND name = ?',
                               (data["surname"], data["name"]))
                self.db.commit()
            except sqlite3.Error as e:
                self.db.rollback()
                print('sqlite3.Error during reception of user_id:', e)

            user_id = cursor.fetchone()[0]

            # ---------------------- Сохранение комментария ------------------
            try:
                cursor.execute('INSERT INTO comment(body, user_id) VALUES(?, ?)', (data["comment"], user_id))
                self.db.commit()
            except sqlite3.Error as e:
                self.db.rollback()
                print('sqlite3.Error during comment insert:', e)

            data = {'success': True, 'msg': 'Комментарий успешно добавлен.'}
        else:
            data = {'success': False, 'msg': 'Фамилия и имя должны быть заполнены.'}

        body = json.dumps(data, sort_keys=True, indent=4).encode("utf-8")

        self.headers['Content-Type'] = 'application/json'
        return [body]

    def static(self, environ, start_response):
        path = environ['PATH_INFO']
        path = path.replace(config.STATIC_URL_PREFIX, config.STATIC_FILE_DIR)

        # --------------------- Определение расширения файла -------------------
        name, ext = os.path.splitext(path)
        type = "application/octet-stream"
        if ext in self.MIME_TABLE:
            type = self.MIME_TABLE[ext]

        # --------------------- Чтение файла -----------------------------------
        try:
            h = open(path, 'rb')
            content = h.read()
            h.close()
        except FileNotFoundError:
            pass

        self.headers['Content-Type'] = type
        return [content]

    def show_404(self, environ, start_response):
        self.headers['Content-Type'] = 'text/html'
        return template_render('404.html')

    def is_post_request(self, environ, start_response):
        if environ['REQUEST_METHOD'] != 'POST':
            self.show_404(environ, start_response)

    def serve(self, environ, start_response):
        urls = [
            ('', self.index),
            ('comment', self.comment),
            ('view', self.view),
            ('stat', self.stat),
            ('save_comment', self.save_comment)
        ]

        path = environ.get('PATH_INFO', '').lstrip('/')

        for key, func in urls:
            # match = re.search(key, path)
            if path == key:
                # if match is not None:
                return func(environ, start_response)
            elif environ['PATH_INFO'].startswith(config.STATIC_URL_PREFIX):
                # if not os.path.exists(path):
                #     return self.show_404(environ, start_response)
                return self.static(environ, start_response)
        return self.show_404(environ, start_response)
