from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from monitor.models import Website


@login_required
def dashboard(request):
    """Dashboard view for logged-in users."""
    websites = Website.objects.filter(owner=request.user)
    total_sites = websites.count()
    active_sites = websites.filter(is_paused=False).count()
    paused_sites = websites.filter(is_paused=True).count()

    down_sites = 0

    for site in websites.filter(is_paused=False):
        latest_check = site.latest_check()
        if latest_check and not latest_check.is_up:
            down_sites += 1

    context = {
        "websites": websites,
        "total_sites": total_sites,
        "active_sites": active_sites,
        "paused_sites": paused_sites,
        "down_sites": down_sites,
    }
    return render(request, "monitor/dashboard.html", context)
