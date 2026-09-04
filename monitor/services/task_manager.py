"""
This module contains functions for managing the asynchronous tasks that monitor websites.
"""

import asyncio

from monitor.services.monitor import monitor_website


async def reconcile_tasks(running_tasks, websites, client):
    """Reconcile the running tasks with the current list of websites."""
    website_ids = {website.pk for website in websites}

    for website in websites:
        task = running_tasks.get(website.pk)

        exception = None
        if task is not None and task.done():
            if task.cancelled():
                print(f"Task for {website.name} was cancelled.")
            else:
                exception = task.exception()
                if exception is not None:
                    print(f"Exception in task for {website.name}: {exception}")

            running_tasks.pop(website.pk, None)

            if exception is not None:
                task = asyncio.create_task(
                    monitor_website(website, client)
                )
                running_tasks[website.pk] = task

        elif task is None:
            task = asyncio.create_task(
                monitor_website(website, client)
            )
            running_tasks[website.pk] = task

    tasks_to_await = []
    for website_id in list(running_tasks.keys()):
        if website_id not in website_ids:
            task_to_cancel = running_tasks.pop(website_id, None)
            task_to_cancel.cancel()
            tasks_to_await.append(task_to_cancel)

    if tasks_to_await:
        await asyncio.gather(*tasks_to_await, return_exceptions=True)

    return running_tasks