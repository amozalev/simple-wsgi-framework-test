from manage import app


class Views:
    # @app.route('/')
    def index(self):
        print('create /')
        return 'index function'

    # @app.route('/comments')
    def comments(self):
        print('create /comments')
        return 'comments function'
