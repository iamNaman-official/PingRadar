import asyncio

import httpx
from asgiref.sync import sync_to_async
from django.core.management.base import BaseCommand
from django.db import close_old_connections

from monitor.models import Website
from monitor.services.task_manager import reconcile_tasks

TIME_MANAGER_INTERVAL = 2


class Command(BaseCommand):
    help = "Continuously checks tracked websites using their individual timers."

    def handle(self, *args, **options):
        """Start the monitor loop, which checks each website according to its configured timer."""
        self.stdout.write("Starting the monitor loop... Press Ctrl+C to stop.")
        try:
            asyncio.run(self.monitor_loop())
        except KeyboardInterrupt:
            self.stdout.write("\nMonitor loop stopped.")

    async def monitor_loop(self):
        """Main monitoring loop - owns the process lifetime, delegates per-cycle
        task bookkeeping to reconcile_tasks()."""
        running_tasks = {}

        async with httpx.AsyncClient() as client:
            try:
                while True:
                    await sync_to_async(close_old_connections)()
                    websites = await self.get_all_websites()

                    running_tasks = await reconcile_tasks(running_tasks, websites, client)

                    self.stdout.write(
                        f"Sleeping for {TIME_MANAGER_INTERVAL}s before next check."
                    )
                    await asyncio.sleep(TIME_MANAGER_INTERVAL)

            finally:
                # Shutdown: cancel every still-running task and wait for
                # them to actually finish cancelling before exiting.
                for task in running_tasks.values():
                    task.cancel()
                if running_tasks:
                    await asyncio.gather(*running_tasks.values(), return_exceptions=True)

    async def get_all_websites(self):
        """Fetch all websites from the database asynchronously."""
        websites = await sync_to_async(list)(Website.objects.all())
        return websites