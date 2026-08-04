import asyncio
from router import add_path, get_handler

async def handler():
    return "Normal response"

add_path("/normal", handler)
async def main():
    path = "/missing"
    handler = get_handler(path)
    response = await handler()
    print(f"Response for {path}: {response}")

asyncio.run(main())
