import asyncio
from router import route, get_handler

@route("/")
async def home_handler():
    return 200, "Welcome to the Home Page"

async def main():
    paths = ["/", "/missing"]
    for path in paths:
        handler = get_handler(path)
        status, response = await handler()
        print(f"{path} -> Status: {status}, Response: {response}")

asyncio.run(main())

