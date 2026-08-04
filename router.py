routes = {}

def route(path):
    def decorator(handler):
        routes[path] = handler
        return handler
    return decorator

def get_handler(path):
    handler = routes.get(path)
    if handler is None:
        return not_found_handler
    return handler

async def not_found_handler():
    return 404, "Route Not Found"