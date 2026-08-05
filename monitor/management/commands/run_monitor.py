import asyncio
import time

import httpx
from asgiref.sync import sync_to_async
from django.core.management.base import BaseCommand

from monitor.models import StatusCheck, Website


class Command(BaseCommand):
    help = "Continuously checks all tracked websites concurrently and records their status."

    def handle(self, *args, **options):
        self.stdout.write("Starting the monitor loop... Press Ctrl+C to stop.")
        try:
            asyncio.run(self.monitor_loop())
        except KeyboardInterrupt:
            self.stdout.write("\nMonitor loop stopped.")
            
    async def monitor_loop(self):
        while True:
            websites = await self.get_all_websites()
            self.stdout.write(f"Checking {len(websites)} websites...")

            if websites:
                await self.check_and_save_all(websites)

            self.stdout.write("Done. Waiting 60 seconds...\n")
            await asyncio.sleep(60)

    async def get_all_websites(self):
        websites = await sync_to_async(list)(Website.objects.filter(is_paused=False))
        return websites

    async def check_and_save_all(self, websites):
        async with httpx.AsyncClient() as client:
            # Build one task per website - none of these run yet,
            # they're just scheduled.
            tasks = [self.check_url_async(client, site.url) for site in websites]

            # Fire all of them off together, wait for all to finish.
            results = await asyncio.gather(*tasks)

        save_tasks = [
            self.save_check_result(website, result)
            for website, result in zip(websites, results)
        ]
        await asyncio.gather(*save_tasks)

    async def check_url_async(self, client, url):
        start = time.time()
        try:
            response = await client.get(
                url,
                timeout=10,
                headers={"User-Agent": "PingRadar-Monitor/1.0"}
            )
            elapsed = time.time() - start

            if response.status_code == 429:
                # Rate-limited, not actually down - flag it separately
                # so it doesn't get recorded as a false outage.
                return {
                    "up": None,
                    "time": elapsed,
                    "status": response.status_code,
                }

            return {
                "up": response.status_code < 400,
                "time": elapsed,
                "status": response.status_code,
            }
        except Exception:
            elapsed = time.time() - start
            return {
                "up": False,
                "time": elapsed,
                "status": None,
            }

    async def save_check_result(self, website, result):
        if result["up"] is None:
            # Rate-limited - skip logging this cycle rather than
            self.stdout.write(f"  {website.name}: RATE LIMITED (429) - skipped")
            return

        await sync_to_async(StatusCheck.objects.create)(
            website=website,
            is_up=result["up"],
            response_time_ms=int(result["time"] * 1000) if result["up"] else None,
            status_code=result["status"],
        )
        status_label = "UP" if result["up"] else "DOWN"
        self.stdout.write(f"  {website.name}: {status_label} ({result['status']})")