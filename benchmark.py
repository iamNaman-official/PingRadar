import httpx
import time
import asyncio

urls = [
    "https://pokeapi.co/api/v2/pokemon/charizard",
    "https://pokeapi.co/api/v2/pokemon/bulbasaur",
    "https://pokeapi.co/api/v2/pokemon/squirtle",
    "https://pokeapi.co/api/v2/pokemon/pikachu",
    "https://pokeapi.co/api/v2/pokemon/sceptile",
    "https://pokeapi.co/api/v2/pokemon/garchomp",
    "https://pokeapi.co/api/v2/pokemon/dragonite",
    "https://pokeapi.co/api/v2/pokemon/tyranitar",
    "https://pokeapi.co/api/v2/pokemon/gardevoir",
    "https://pokeapi.co/api/v2/pokemon/absol",
    "https://pokeapi.co/api/v2/pokemon/latios",
    "https://pokeapi.co/api/v2/pokemon/latias",
    "https://pokeapi.co/api/v2/pokemon/kyogre", 
    "https://pokeapi.co/api/v2/pokemon/groudon",
    "https://pokeapi.co/api/v2/pokemon/reshiram",
    "https://pokeapi.co/api/v2/pokemon/zekrom",
    "https://pokeapi.co/api/v2/pokemon/kyurem",
    "https://pokeapi.co/api/v2/pokemon/xerneas",
    "https://pokeapi.co/api/v2/pokemon/yveltal",
    "https://pokeapi.co/api/v2/pokemon/zygarde",
    "https://pokeapi.co/api/v2/pokemon/necrozma",
    "https://pokeapi.co/api/v2/pokemon/darkrai",
    "https://pokeapi.co/api/v2/pokemon/arceus",
    "https://pokeapi.co/api/v2/pokemon/mewtwo",
    "https://pokeapi.co/api/v2/pokemon/mew",
    "https://pokeapi.co/api/v2/pokemon/celebi",
    "https://pokeapi.co/api/v2/pokemon/jirachi",
    "https://pokeapi.co/api/v2/pokemon/deoxys",
    "https://pokeapi.co/api/v2/pokemon/greninja",
    "https://pokeapi.co/api/v2/pokemon/decidueye",
    "https://pokeapi.co/api/v2/pokemon/incineroar",
    "https://pokeapi.co/api/v2/pokemon/primarina",
    "https://pokeapi.co/api/v2/pokemon/lycanroc",   
    "https://pokeapi.co/api/v2/pokemon/toxtricity",
    "https://pokeapi.co/api/v2/pokemon/dracovish",
    "https://pokeapi.co/api/v2/pokemon/arctovish",
    "https://pokeapi.co/api/v2/pokemon/dragapult",
]

# def url_check_sync(url):
#     start = time.time()
#     try:
#         response = httpx.get(url, timeout=5)
#         elapsed = time.time() - start
#         return {"url": url, "up": True, "time": elapsed, "status": response.status_code}
#     except Exception as e:
#         elapsed = time.time() - start
#         return {"url": url, "up": False, "time": elapsed, "status": None}
    
# def url_check_async(urls):
#     start = time.time()
#     results = [url_check_sync(url) for url in urls]
#     total_time = time.time() - start
#     return results, total_time

# if __name__ == "__main__":
#     results, total_time = url_check_async(urls)
#     for result in results:
#         print(result)
#     print(f"Total time for {len(urls)} requests: {total_time:.2f} seconds")

async def check_url_async(client, url):
    start = time.time()
    try:
        response = await client.get(url, timeout=5)
        elapsed = time.time() - start
        return {"url": url, "up": response.status_code < 400, "time": elapsed, "status": response.status_code}
    except Exception:
        elapsed = time.time() - start
        return {"url": url, "up": False, "time": elapsed, "status": None}

async def check_all_concurrent(urls):
    start = time.time()
    async with httpx.AsyncClient() as client:
        tasks = [check_url_async(client, url) for url in urls]
        results = await asyncio.gather(*tasks)
    total_time = time.time() - start
    return results, total_time

if __name__ == "__main__":
    results, total_time = asyncio.run(check_all_concurrent(urls))
    for result in results:
        print(result)
    print(f"Total time for {len(urls)} requests: {total_time:.2f} seconds")
