import json

from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.core.validators import URLValidator
from django.db import IntegrityError
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.http import url_has_allowed_host_and_scheme

from monitor.models import Website


@login_required
def add_website(request):
    """View to add a new website for monitoring."""
    if request.method == "POST":
        name = request.POST.get("name")
        url = request.POST.get("url")
        timer = (request.POST.get("timer") or "60").strip()
        if name and url and timer:
            if not url.startswith(("http://", "https://")):
                url = "https://" + url

            if not timer.isdigit() or int(timer) <= 0:
                error_message = "Timer must be a positive integer."
                return render(
                    request,
                    "monitor/add_website.html",
                    {"error_message": error_message},
                )

            timer = int(timer)
            validator = URLValidator()
            try:
                validator(url)
            except ValidationError:
                error_message = "Please enter a valid URL."
                return render(
                    request,
                    "monitor/add_website.html",
                    {"error_message": error_message},
                )

            try:
                Website.objects.create(
                    owner=request.user, name=name, url=url, timer=timer
                )
            except IntegrityError:
                error_message = "You already have a website with this URL."
                return render(
                    request,
                    "monitor/add_website.html",
                    {"error_message": error_message},
                )
            return redirect("dashboard")
    return render(request, "monitor/add_website.html")


@login_required
def delete_website(request, website_id):
    """View to delete a website from monitoring."""
    website = get_object_or_404(Website, id=website_id, owner=request.user)
    if request.method == "POST":
        website.delete()
    return redirect("dashboard")


@login_required
def toggle_pause(request, website_id):
    """View to toggle the pause state of a website."""
    website = get_object_or_404(Website, id=website_id, owner=request.user)
    if request.method == "POST":
        website.is_paused = not website.is_paused
        website.save()
    next_url = request.META.get("HTTP_REFERER")
    if next_url and url_has_allowed_host_and_scheme(
        next_url, allowed_hosts={request.get_host()}, require_https=request.is_secure()
    ):
        return redirect(next_url)
    return redirect("dashboard")


@login_required
def website_detail(request, website_id):
    """View to display details of a specific website."""
    website = get_object_or_404(Website, id=website_id, owner=request.user)

    if request.method == "POST":
        timer = request.POST.get("timer")
        if timer and timer.isdigit() and 5 <= int(timer) <= 10800:
            website.timer = int(timer)
            website.save()
        return redirect("website_detail", website_id=website.id)
    recent_checks = website.checks.all()[:20]
    total_checks = website.checks.count()
    context = {
        "website": website,
        "recent_checks": recent_checks,
        "total_checks": total_checks,
        "uptime": website.uptime_percentage(),
        "chart_data": json.dumps(website.response_time_history()),
    }
    return render(request, "monitor/website_details.html", context)
