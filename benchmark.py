"""
Benchmark sequential and concurrent HTTP requests.

Measures the performance difference between synchronous
requests using httpx.Client and concurrent requests
using asyncio with httpx.AsyncClient.

Both strategies reuse ONE client, created once in main() and passed
down as a parameter - not recreated on every call. A fresh client
means a fresh connection (new TCP/TLS handshake on its first request),
so recreating one per call would silently reintroduce a cold-start
cost every time, defeating the point of warming up at all.
"""

import asyncio
import time

import httpx

# -----------------------------
# Configuration
# -----------------------------

TIMEOUT = 5
MAX_CONCURRENT = 10
BASE_URL = "http://localhost:8080"

ENDPOINTS = [
    f"{BASE_URL}/",
    f"{BASE_URL}/slow",
    f"{BASE_URL}/very-slow",
    f"{BASE_URL}/error",
    f"{BASE_URL}/timeout",
    f"{BASE_URL}/random",
]

URLS =[]

for endpoint in ENDPOINTS:
    URLS.extend([endpoint] * 10)

async def warm_up(sync_client: httpx.Client, async_client: httpx.AsyncClient, url: str) -> None:
    """
    Warm up both clients before timing begins.
    Using the same client instances for the warm-up and the benchmark
    ensures their underlying connections are already established.
    Warming up a different client would not warm the connections reused
    by the benchmark.
    """
    try:
        sync_client.get(url)
    except httpx.RequestError:
        pass
    try:
        await async_client.get(url)
    except httpx.RequestError:
        pass


# -----------------------------
# Sequential Benchmark
# -----------------------------


def check_url_sync(client: httpx.Client, url: str) -> dict:
    """Check a single URL synchronously."""
    start = time.perf_counter()
    try:
        response = client.get(url)
        return {
            "url": url,
            "status": response.status_code,
            "up": response.status_code < 400,
            "response_time": time.perf_counter() - start,
        }

    except httpx.RequestError:
        return {
            "url": url,
            "status": None,
            "up": False,
            "response_time": time.perf_counter() - start,
        }


def check_all_sequential(client: httpx.Client, urls: list[str]) -> tuple[list[dict], float]:
    """Check all URLs sequentially."""
    start = time.perf_counter()
    results = [check_url_sync(client, url) for url in urls]
    total_time = time.perf_counter() - start
    return results, total_time

# -----------------------------
# Concurrent Benchmark
# -----------------------------

async def check_url_async(client: httpx.AsyncClient, url: str, semaphore: asyncio.Semaphore) -> dict:
    """Check a single URL asynchronously, using a semaphore to limit concurrency."""
    async with semaphore:
        start = time.perf_counter()
        try:
            response = await client.get(url)
            return {
                "url": url,
                "status": response.status_code,
                "up": response.status_code < 400,
                "response_time": time.perf_counter() - start,
            }

        except httpx.RequestError:
            return {
                "url": url,
                "status": None,
                "up": False,
                "response_time": time.perf_counter() - start,
            }


async def check_all_concurrent(client: httpx.AsyncClient, urls: list[str]) -> tuple[list[dict], float]:
    """Check all URLs concurrently, using a semaphore to limit concurrency."""
    start = time.perf_counter()
    semaphore = asyncio.Semaphore(MAX_CONCURRENT)  
    results = await asyncio.gather(*(check_url_async(client, url, semaphore) for url in urls))
    total_time = time.perf_counter() - start
    return results, total_time

# -----------------------------
# Utility Functions
# -----------------------------

def print_results(results: list[dict]) -> None:
    """Print the results of the benchmark."""
    for result in results:
        status = "UP" if result["up"] else "DOWN"

        print(
            f"{status:4} | "
            f"{result['status']} | "
            f"{result['response_time']:.3f}s | "
            f"{result['url']}"
        )


def print_summary(sync_time: float, async_time: float) -> None:
    """Print a summary of the benchmark results."""
    speedup = sync_time / async_time

    print("\n" + "=" * 50)
    print("Benchmark Summary")
    print("=" * 50)

    print(f"URLs Tested        : {len(URLS)}")
    print(f"Sequential Time    : {sync_time:.2f} seconds")
    print(f"Concurrent Time    : {async_time:.2f} seconds")
    print(f"Speedup            : {speedup:.2f}x faster")

    print("=" * 50)


# -----------------------------
# Main Execution
# -----------------------------
async def main() -> None:
    """Both clients are created ONCE here, and stay open for everything
    below - every call reuses the same underlying connection instead
    of paying a fresh TCP/TLS handshake each time."""
    with httpx.Client(timeout=TIMEOUT) as sync_client:
        async with httpx.AsyncClient(timeout=TIMEOUT) as async_client:

            await warm_up(sync_client, async_client, URLS[0])

            print("\nRunning concurrent benchmark...\n")
            async_results, async_time = await check_all_concurrent(async_client, URLS)
            print_results(async_results)

            print("\nRunning sequential benchmark...\n")
            sync_results, sync_time = check_all_sequential(sync_client, URLS)
            print_results(sync_results)

    print_summary(sync_time, async_time)


if __name__ == "__main__":
    asyncio.run(main())