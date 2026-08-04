import asyncio

import handlers
from router import get_handler


async def home_route():
    handler = get_handler("/")
    status_code, body = await handler()
    assert status_code == 200
    assert body == "Welcome to the Home Page"
    print("✓ Home route works")

async def unknown_route():
    handler = get_handler("/unknown")
    status_code, body = await handler()
    assert status_code == 404
    assert body == "Route Not Found"
    print("✓ Unknown route works")

async def main():
    await home_route()
    await unknown_route()
    print("✓ All tests passed!")

if __name__ == "__main__":
    asyncio.run(main())