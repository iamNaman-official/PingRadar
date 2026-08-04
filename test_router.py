import asyncio
import handlers
from router import get_handler

async def main():
    """Test the routing logic by directly invoking handlers for specific paths."""
    handler = get_handler("/normal")
    status, response = await handler()
    print(f"/normal -> Status: {status}, Response: {response}")

asyncio.run(main())

