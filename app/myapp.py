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
        except sqlite3.Error:
            print("Error")

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
        data = 'index data'
        self.headers['Content-Type'] = 'text/html'
        return [data.encode('utf-8')]

    def comments(self, environ, start_response):
        # Отображение формы ввода комментариев
        print('comments')
        self.headers['Content-Type'] = 'text/html'
        return template_render('index.html')

    def view(self, environ, start_response):
        # Отображение комментариев
        print('view func')
        self.headers['Content-Type'] = 'application/json'
        data = {"Hello World": 2}
        body = json.dumps(data, sort_keys=True, indent=4).encode("utf-8")

        # start_response(self.status, list(self.headers.items()))
        return [body]

    def stat(self, environ, start_response):
        # Отображение таблица со списком тех регионов, у которых количество комментариев больше 5,
        print('stats')
        return 'view comments function'

    def save_comment(self, environ, start_response):

        try:
            request_body_size = int(environ.get('CONTENT_LENGTH', 0))
        except ValueError:
            request_body_size = 0
        request_body = str(environ['wsgi.input'].read(request_body_size))
        body = urllib.parse.parse_qs(request_body, keep_blank_values=True, encoding='utf-8')

        data = {}
        for i in body:
            data[i.replace('b\'', '')] = body[i][0]
        # print(data, type(data))

        if 'surname' and 'name' in data:
            # ---------------------- Проверка есть ли уже такой регион ---------------------------
            try:
                cursor = self.db.cursor()
                cursor.execute('SELECT id FROM region WHERE name = ?', (data["region"],))
                self.db.commit()
            except sqlite3.Error as e:
                self.db.rollback()
                print('sqlite3.Error during region existence check:', e)

            if cursor.fetchone() is None:
                try:
                    cursor.execute('INSERT INTO region(name) VALUES(?)', (data["region"],))
                    self.db.commit()
                except sqlite3.Error as e:
                    self.db.rollback()
                    print('sqlite3.Error during region insert:', e)

            # ------------ Проверка есть ли уже такой город, получение id созданного региона, добавл. города --------
            try:
                cursor.execute('SELECT id FROM city WHERE name = ?', (data["city"],))
                self.db.commit()
            except sqlite3.Error as e:
                self.db.rollback()
                print('sqlite3.Error during city existence check:', e)

            if cursor.fetchone() is None:
                try:
                    cursor.execute('SELECT id FROM region WHERE name = ?', (data["region"],))
                    self.db.commit()
                except sqlite3.Error as e:
                    self.db.rollback()
                    print('sqlite3.Error during region existence check:', e)

                region_id = cursor.fetchone()[0]

                try:
                    cursor.execute('INSERT INTO city(name, region_id) VALUES(?, ?)', (data["city"], region_id))
                    self.db.commit()
                except sqlite3.Error as e:
                    self.db.rollback()
                    print('sqlite3.Error during city insert:', e)

            # ---------------------- Получение id добавленного города------- ------------------
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

            # ---------------------- Проверка наличия пользователя. Если нет, добавление ---------------
            try:
                cursor.execute('SELECT id FROM user WHERE surname = ? AND name = ?',
                               (data["surname"], data["name"]))
                self.db.commit()
            except sqlite3.Error as e:
                self.db.rollback()
                print('sqlite3.Error during user existence check:', e)

            if cursor.fetchone() is None:
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

    def serve(self, environ, start_response):
        urls = [
            ('', self.index),
            ('comments', self.comments),
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
