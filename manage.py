from wsgiref.simple_server import make_server
from app.myapp import MyApp


def run():
    app = MyApp()
    try:
        srv = make_server('localhost', 8000, app)
        print("--- Start app on port 8000 ---")
        srv.serve_forever()
    except KeyboardInterrupt:
        print('--- Stop app ---')


if __name__ == '__main__':
    run()
