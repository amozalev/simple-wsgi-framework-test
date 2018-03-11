import json
import os
import re
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
        self.environ = {}

        try:
            self.db = sqlite3.connect(config.DB_NAME)
        except sqlite3.Error as e:
            print('sqlite3.Error during db connection:', e)

    def __call__(self, environ, start_response):
        body = self.serve(environ)
        print(body)
        start_response(self.status, list(self.headers.items()))
        return body

    def index(self, environ):
        mapping_dict = {"data": ''}

        self.headers['Content-Type'] = 'text/html'
        return template_render('index.html', mapping_dict)

    def comment(self, environ):
        # Отображение формы ввода комментариев
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

    def view(self, environ):
        # Отображение комментариев
        cursor = self.db.cursor()
        query = ('''SELECT c.body, u.name, u.surname, u.patronymic_name, c.id
                    FROM comment c
                    JOIN user u ON u.id = c.user_id
                    ORDER BY 1''')

        mapping_dict = dict()
        mapping_dict['table'] = ''
        mapping_dict['table'] += '''<table class="table table-striped table-bordered">
                                        <tr><th></th><th>ФИО</th><th>Комментарий</th></tr>'''
        try:
            for i in cursor.execute(query):
                mapping_dict['table'] += '''<tr id="row_id_{}"><td><input name="comment_id_{}" value="{}" type="checkbox"/></td>
                                            <td>{} {} {}</td><td>{}</td></tr>'''. \
                    format(i[4], i[4], i[4], i[1], i[2], i[3], i[0])
        except sqlite3.Error as e:
            print('sqlite3.Error during request of existing comments:', e)

        mapping_dict['table'] += '</table>'

        self.headers['Content-Type'] = 'text/html'
        return template_render('view.html', mapping_dict)

    def stat(self, environ):
        # Отображение таблица со списком тех регионов, у которых количество комментариев больше 5
        path_parts = (environ['PATH_INFO']).split('/')

        cursor = self.db.cursor()
        mapping_dict = dict()
        mapping_dict['table'] = ''

        # Если есть цифра в ссылке, то отображаются города
        if path_parts[-1].isdigit():
            region_id = int(path_parts[-1])
            query = ('''SELECT ci.name, count(co.id)
                        FROM city ci
                        JOIN "user" u ON ci.id = u.city_id
                        JOIN comment co ON co.user_id = u.id
                        WHERE ci.region_id = ?
                        GROUP BY ci.name
                        ORDER BY ci.name
                        ''')

            mapping_dict['table'] += '''<table class="table table-striped table-bordered">
                                        <tr><th>Город</th><th>Кол-во комментариев</th></tr>'''

            try:
                for i in cursor.execute(query, (region_id,)):
                    mapping_dict['table'] += '<tr><td>{}</td><td>{}</td></tr>'. \
                        format(i[0], i[1])
            except sqlite3.Error as e:
                print('sqlite3.Error during request of regions and comments amount:', e)


        # Отображаются регионы
        else:
            query = ('''SELECT r.id, r.name, count(co.id)
                        FROM region r
                        JOIN city ci ON r.id = ci.region_id
                        JOIN "user" u ON ci.id = u.city_id
                        JOIN comment co ON co.user_id = u.id
                        GROUP BY r.name
                        HAVING count(co.id) > ?
                        ORDER BY r.name 
                        ''')

            mapping_dict['table'] += '''<table class="table table-striped table-bordered">
                                        <tr><th>Регион</th><th>Кол-во комментариев</th></tr>'''

            try:
                for i in cursor.execute(query, (config.COMMENTS_NUMBER,)):
                    mapping_dict['table'] += '<tr><td><a href="/stat/{}">{}</a></td><td>{}</td></tr>'. \
                        format(i[0], i[1], i[2])
            except sqlite3.Error as e:
                print('sqlite3.Error during request of regions and comments amount:', e)

        mapping_dict['table'] += '</table>'

        self.headers['Content-Type'] = 'text/html'
        return template_render('stat.html', mapping_dict)

    def save_comment(self, environ):
        if environ['REQUEST_METHOD'] != 'POST':
            return self.show_404()

        try:
            request_body_size = int(environ.get('CONTENT_LENGTH', 0))
        except ValueError:
            request_body_size = 0
        request_body = str(environ['wsgi.input'].read(request_body_size))
        body = urllib.parse.parse_qs(request_body, keep_blank_values=True, encoding='utf-8')

        msg = {}
        for i in body:
            msg[i.replace('b\'', '')] = body[i][0]

        # ---------------------- Проверка наличия пользователя. Если нет, то добавление ---------------
        cursor = self.db.cursor()
        try:
            cursor.execute('SELECT id FROM user WHERE surname = ? AND name = ?',
                           (msg["surname"], msg["name"]))
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
                               (msg["city"], msg["region"]))
                self.db.commit()
            except sqlite3.Error as e:
                self.db.rollback()
                print('sqlite3.Error during city existence check:', e)

            city_id = cursor.fetchone()[0]

            # ---------------------- Сохранение нового пользователя ---------------------
            try:
                cursor.execute('''INSERT INTO user(surname, name, patronymic_name, phone, email, city_id)
                                    VALUES (?, ?, ?, ?, ?, ?)''',
                               (msg["surname"],
                                msg["name"],
                                msg["patronymic_name"],
                                msg["phone"],
                                msg["email"],
                                city_id))
                self.db.commit()
            except sqlite3.Error as e:
                self.db.rollback()
                print('sqlite3.Error during user insert:', e)

        try:
            cursor.execute('SELECT id FROM user WHERE surname = ? AND name = ?',
                           (msg["surname"], msg["name"]))
            self.db.commit()
        except sqlite3.Error as e:
            self.db.rollback()
            print('sqlite3.Error during reception of user_id:', e)

        user_id = cursor.fetchone()[0]

        # ---------------------- Сохранение комментария ------------------
        try:
            cursor.execute('INSERT INTO comment(body, user_id) VALUES(?, ?)', (msg["comment"], user_id))
            self.db.commit()
        except sqlite3.Error as e:
            self.db.rollback()
            print('sqlite3.Error during comment insert:', e)

        msg = {'success': True, 'msg': 'Комментарий успешно добавлен'}

        body = json.dumps(msg, sort_keys=True, indent=4).encode("utf-8")

        self.headers['Content-Type'] = 'application/json'
        return [body]

    def delete_comment(self, environ):
        if environ['REQUEST_METHOD'] != 'POST':
            return self.show_404()

        try:
            request_body_size = int(environ.get('CONTENT_LENGTH', 0))
        except ValueError:
            request_body_size = 0
        request_body = str(environ['wsgi.input'].read(request_body_size))
        body = urllib.parse.parse_qs(request_body, keep_blank_values=True, encoding='utf-8')

        data = {}
        for i in body:
            data[i.replace('b\'', '')] = ((body[i][0]).replace('\'', ''),)
        print(data)

        msg = {}
        deleted_comment_id = list(data.values())
        print(deleted_comment_id)

        cursor = self.db.cursor()
        try:
            cursor.executemany('DELETE FROM comment WHERE id = ?', deleted_comment_id)
            self.db.commit()
            msg = {'success': True, 'msg': 'Комментарии успешно удалены', 'deleted_comment_id': deleted_comment_id}

        except sqlite3.Error as e:
            self.db.rollback()
            print('sqlite3.Error during comments deletion:', e)
            msg = {'success': True, 'msg': 'Произошла ошибка', 'deleted_comment_id': deleted_comment_id}

        body = json.dumps(msg, sort_keys=True, indent=4).encode("utf-8")

        self.headers['Content-Type'] = 'application/json'
        return [body]

    def static(self, environ):
        path = environ['PATH_INFO']
        path = path.replace(config.STATIC_URL_PREFIX, config.STATIC_FILE_DIR)

        # --------------------- Определение расширения файла -------------------
        name, ext = os.path.splitext(path)
        type = "application/octet-stream"
        if ext in self.MIME_TABLE:
            type = self.MIME_TABLE[ext]

        # --------------------- Чтение файла -----------------------------------
        content = ''
        try:
            h = open(path, 'rb')
            content = h.read()
            h.close()
        except FileNotFoundError:
            pass

        self.headers['Content-Type'] = type
        return [content]

    def show_404(self):
        mapping_dict = dict()
        mapping_dict['data'] = '<h1>404</h1><p>Страница не надена. Пожалуйста, перейдите по одной из ссылок в меню.</p>'

        self.headers['Content-Type'] = 'text/html'
        return template_render('index.html', mapping_dict)

    def serve(self, environ):
        urls = [
            (r'^$', self.index),
            (r'^comment', self.comment),
            (r'view', self.view),
            (r'stat/?$', self.stat),
            (r'stat/(.+)$', self.stat),
            (r'save_comment', self.save_comment),
            (r'delete_comment', self.delete_comment)
        ]

        path = environ.get('PATH_INFO', '').lstrip('/')

        for key, func in urls:
            match = re.search(key, path)
            if match is not None:
                return func(environ)
            elif environ['PATH_INFO'].startswith(config.STATIC_URL_PREFIX):
                return self.static(environ)
        return self.show_404()
