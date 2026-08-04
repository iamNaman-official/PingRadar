import asyncio
import random

from router import route


@route("/")
async def home_handler():
    """Handle the root path and return a welcome message."""
    await asyncio.sleep(random.uniform(0.1, 0.6))  
    return (200, "Welcome to the Home Page")


@route("/slow")
async def slow_handler():
    """Simulate a slow response by sleeping for 3 seconds."""
    await asyncio.sleep(3)
    return (200, "Slow response")

@route("/very-slow")
async def very_slow_handler():
    """Simulate a very slow response by sleeping for 10 seconds."""
    await asyncio.sleep(10)
    return (200, "Very slow response")

@route("/error")
async def error_handler():
    """Simulate an internal server error."""
    return (500, "Internal Server Error")

@route("/timeout")
async def timeout_handler():
    """Simulate a request timeout."""
    await asyncio.sleep(20)
    return (408, "Request Timeout")

@route("/random")
async def random_handler():
    """Simulate a random response with varying delays and outcomes."""
    delay = random.uniform(0.1, 2.0)
    await asyncio.sleep(delay)
    outcome = random.random()

    if outcome < 0.10:
        return (404, "Not Found")
    elif outcome < 0.20:
        return (500, "Internal Server Error")
    elif outcome < 0.30:
        return (408, "Request Timeout")
    elif outcome < 0.40:
        return (400, "Bad Request")
    else:
        return (200, f"Random response after {delay:.2f} seconds")