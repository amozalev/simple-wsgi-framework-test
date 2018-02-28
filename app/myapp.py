class MyApp:
    def __init__(self):
        self.routes = {}

    def route(self, route):
        def wrapper(func):
            self.routes[route] = func
            return func

        return wrapper

    def serve(self, path):
        view_function = self.routes.get(path)
        if view_function:
            return view_function()
        else:
            raise ValueError('Route "{}"" has not been registered'.format(path))
