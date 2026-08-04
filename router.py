routes = {}

def add_path(path, handler):
    routes[path] = handler

def get_handler(path):
    handler = routes.get(path)
    if handler is None:
        return not_found_handler
    return handler

async def not_found_handler():
    return "Route Not Found"