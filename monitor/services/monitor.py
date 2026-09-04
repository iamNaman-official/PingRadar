"""
This module contains functions for monitoring the status of websites asynchronously.
"""

import asyncio

from asgiref.sync import sync_to_async
from django.db import close_old_connections

from monitor.models import StatusCheck, Website
from monitor.services.checker import check_url_async

STATE_CHECK_INTERVAL = 2

async def monitor_website(website, client):
    """Monitor a single website in a loop."""
    website_id = website.pk
    try:
        while True:
            await sync_to_async(close_old_connections)()
            try:
                website = await sync_to_async(Website.objects.get)(pk=website.pk)
            except Website.DoesNotExist:
                print(f"Website {website_id} no longer exists. Stopping monitoring.")
                break

            if website.is_paused:
                print(f"Website {website.name} is paused. Skipping check.")
                await asyncio.sleep(STATE_CHECK_INTERVAL)
                continue

            result = await check_url_async(
                client,
                website.url,
            )

            await save_check_result(
                website,
                result,
            )

            current_timer = max(5, int(website.timer or 60))
            print(f"  {website.name}: Next check in {current_timer}s")
            await asyncio.sleep(current_timer)

    except asyncio.CancelledError:
        print(f"Monitoring task for website {website_id} has been cancelled.")
        raise

async def save_check_result(website, result):
    """Save the result of a website check to the database."""
    if result["up"] is None:
        print(f"Website {website.name} check skipped due to rate limiting.")
        return

    response_time = int(result["time"] * 1000) if result["status"] is not None else None
    await sync_to_async(StatusCheck.objects.create)(
        website=website,
        is_up=result["up"],
        response_time_ms=response_time,
        status_code=result["status"],
    )

    status_label = "UP" if result["up"] else "DOWN"
    if result["error"]:
        print(
            f"  {website.name}: "
            f"{status_label} ({result['error']}) "
            f"{website.timer}s interval"
        )
    else:
        print(
            f"  {website.name}: "
            f"{status_label} (Status Code: {result['status']}) "
            f"{website.timer}s interval"
        )