"""
This module contains functions for checking the status of URLs asynchronously using the httpx library.
"""

import time

import httpx


async def check_url_async(client, url):
    """Check a single URL asynchronously and return the result."""
    start = time.time()
    try:
        response = await client.get(
            url,
            timeout=10,
            headers={"User-Agent": "PingRadar-Monitor/1.0"},
        )
        elapsed = time.time() - start

        if response.status_code == 429:
            # Rate-limited, not actually down.
            # Skip recording this check as an outage.
            return {
                "up": None,
                "time": elapsed,
                "status": response.status_code,
                "error": "Rate Limited (429)",
            }

        return {
            "up": response.status_code < 400,
            "time": elapsed,
            "status": response.status_code,
            "error": None,
        }

    except httpx.TimeoutException:
        elapsed = time.time() - start

        return {
            "up": False,
            "time": elapsed,
            "status": None,
            "error": "Timeout",
        }

    except httpx.ConnectError:
        elapsed = time.time() - start

        return {
            "up": False,
            "time": elapsed,
            "status": None,
            "error": "Connection Error",
        }

    except httpx.RequestError as e:
        elapsed = time.time() - start

        return {
            "up": False,
            "time": elapsed,
            "status": None,
            "error": str(e),
        }

