import asyncio
import time

import httpx
from asgiref.sync import sync_to_async
from django.core.management.base import BaseCommand

from monitor.models import StatusCheck, Website

# from arduino_display import update_display


class Command(BaseCommand):
    help = "Continuously checks tracked websites using their individual timers."
    STATE_CHECK_INTERVAL = 2
    TIME_MANAGER_INTERVAL = 2

    def handle(self, *args, **options):
        """Start the monitor loop, which checks each website according to its configured timer."""
        self.stdout.write("Starting the monitor loop... Press Ctrl+C to stop.")
        try:
            asyncio.run(self.monitor_loop())
        except KeyboardInterrupt:
            self.stdout.write("\nMonitor loop stopped.")

    async def monitor_loop(self):
        """Main monitoring loop."""
        running_tasks = {}

        async with httpx.AsyncClient() as client:
            try:
                while True:
                    websites = await self.get_all_websites()
                    website_ids = {website.pk for website in websites}

                    for website in websites:
                        task = running_tasks.get(website.pk)

                        if task is not None and task.done():
                            exception = task.exception()

                            if exception is not None:
                                self.stdout.write(
                                    f"Error in monitoring task for "
                                    f"{website.name}: {exception}"
                                )

                            del running_tasks[website.pk]

                            task = asyncio.create_task(
                                self.monitor_website(website, client)
                            )
                            running_tasks[website.pk] = task

                        elif task is None:
                            task = asyncio.create_task(
                                self.monitor_website(website, client)
                            )
                            running_tasks[website.pk] = task

                    for website_id in list(running_tasks.keys()):
                        if website_id not in website_ids:
                            self.stdout.write(
                                f"Website {website_id} has been removed. "
                                "Cancelling its monitoring task."
                            )

                            running_tasks[website_id].cancel()

                            try:
                                await running_tasks[website_id]
                            except asyncio.CancelledError:
                                self.stdout.write(
                                    f"Monitoring for website {website_id} "
                                    "has been cancelled."
                                )

                            del running_tasks[website_id]

                    self.stdout.write(
                        f"Sleeping for {self.TIME_MANAGER_INTERVAL}s before next check..."
                    )
                    await asyncio.sleep(self.TIME_MANAGER_INTERVAL)
            finally:
                for task in list(running_tasks.values()):
                    task.cancel()

                for task in list(running_tasks.values()):
                    try:
                        await task
                    except asyncio.CancelledError:
                        pass

    async def monitor_website(self, website, client):
        """Monitor a single website in a loop."""
        website_id = website.pk
        try:
            while True:
                try:
                    website = await sync_to_async(Website.objects.get)(pk=website.pk)
                except Website.DoesNotExist:
                    self.stdout.write(
                        f"Website {website_id} no longer exists. Stopping monitoring."
                    )
                    break

                if website.is_paused:
                    self.stdout.write(
                        f"Website {website.name} is paused. Skipping check."
                    )
                    await asyncio.sleep(self.STATE_CHECK_INTERVAL)
                    continue

                result = await self.check_url_async(
                    client,
                    website.url,
                )

                await self.save_check_result(
                    website,
                    result,
                )

                current_timer = max(
                    5,
                    int(website.timer or 60),
                )

                self.stdout.write(f"  {website.name}: Next check in {current_timer}s")

                await asyncio.sleep(current_timer)

        except asyncio.CancelledError:
            self.stdout.write(
                f"Monitoring for website {website_id} has been cancelled."
            )
            raise

    async def get_all_websites(self):
        """Fetch all websites from the database asynchronously."""
        websites = await sync_to_async(list)(Website.objects.all())
        return websites

    async def check_url_async(self, client, url):
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

    async def save_check_result(self, website, result):
        """Save the result of a website check to the database."""
        if result["up"] is None:
            self.stdout.write(f"  {website.name}: RATE LIMITED (429) - skipped")
            return

        await sync_to_async(StatusCheck.objects.create)(
            website=website,
            is_up=result["up"],
            response_time_ms=(int(result["time"] * 1000) if result["up"] else None),
            status_code=result["status"],
        )

        # Arduino display integration.
        # Not ready for production use.

        # update_display(
        #     website.name,
        #     "UP" if result["up"] else "DOWN",
        #     result["status"] if result["status"] else "ERR",
        #     int(result["time"] * 1000),
        # )
        status_label = "UP" if result["up"] else "DOWN"

        if result["error"]:
            self.stdout.write(
                f"  {website.name}: "
                f"{status_label} ({result['error']}) "
                f"{website.timer}s interval"
            )
        else:
            self.stdout.write(
                f"  {website.name}: "
                f"{status_label} ({result['status']}) "
                f"{website.timer}s interval"
            )
