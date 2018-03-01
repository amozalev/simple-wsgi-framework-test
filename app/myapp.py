import json
import re


class MyApp:
    def __init__(self):
        self.routes = {}
        self.headers = {}

    def __call__(self, environ, start_response):
        self.serve(environ)

        # for i in environ:
        #     print(i)

        status = '200 OK'
        self.headers['Content-Type'] = 'application/json'
        # response_headers = [('Content-type', 'application/json')]

        data = {"Hello World": 2}
        body = json.dumps(data, sort_keys=True, indent=4).encode("utf-8")

        start_response('200 OK', list(self.headers.items()))
        return [body]

    def route(self, route):
        def wrapper(func):
            self.routes[route] = func
            return func

        return wrapper

    def index(self):
        print('index')
        return 'index function'

    def comments(self):
        print('comments')
        return 'comments function'

    def serve(self, environ):
        self.urls = [
            ('/', self.index),
            ('/comments', self.comments)
        ]

        path = environ.get('PATH_INFO', '')
        for key, func in self.urls:
            match = re.search(key, path)
            if match is not None:
                func()
