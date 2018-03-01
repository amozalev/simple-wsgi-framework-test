from wsgiref.simple_server import make_server
from app.myapp import MyApp


# def application(environ, start_response):
#     start_response('200 OK', [('Content-Type', 'text/html')])
#     return ['''Hello world!''']


app = MyApp()


if __name__ == '__main__':
    srv = make_server('localhost', 8000, app)
    print("Serving on port 8000")
    srv.serve_forever()
