import json
# import re
from .templating import template_render
import config


class MyApp:
    def __init__(self):
        self.routes = {}
        self.headers = {}
        self.status = '200 OK'

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

    def static(self, environ, start_response):
        path = environ['PATH_INFO']
        path = path.replace(config.STATIC_URL_PREFIX, config.STATIC_FILE_DIR)

        h = open(path, 'rb')
        content = h.read()
        h.close()

        return [content]

    def show_404(self, environ, start_response):
        self.headers['Content-Type'] = 'text/html'
        return ["""<html><h1>Page not Found</h1><p>
                           That page is unknown. Return to 
                           the <a href="/">home page</a></p>
                           </html>""".encode("utf-8")]

    def serve(self, environ, start_response):
        urls = [
            ('', self.index),
            ('comments', self.comments),
            ('view', self.view),
            ('stat', self.stat)
        ]

        path = environ.get('PATH_INFO', '').lstrip('/')

        for key, func in urls:
            # match = re.search(key, path)
            if path == key:
                # if match is not None:
                return func(environ, start_response)
            elif environ['PATH_INFO'].startswith(config.STATIC_URL_PREFIX):
                return self.static(environ, start_response)
        return self.show_404(environ, start_response)
