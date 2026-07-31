from django.shortcuts import redirect, render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login as auth_login
from monitor.models import Website, StatusCheck
import json

# Create your views here.
def landing(request):
    return render(request, 'monitor/landing.html')

def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            return redirect('dashboard')
    else:
        form = UserCreationForm()
    return render(request, 'monitor/signup.html', {'form': form})

@login_required
def dashboard(request):
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
        'websites': websites,
        'total_sites': total_sites,
        'active_sites': active_sites,
        'paused_sites': paused_sites,
        'down_sites': down_sites
    }
    return render(request, 'monitor/dashboard.html', context)

@login_required
def add_website(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        url = request.POST.get('url')
        if name and url:
            Website.objects.create(owner=request.user, name=name, url=url)
            return redirect('dashboard')
    return render(request, 'monitor/add_website.html')

@login_required
def delete_website(request, website_id):
    website = get_object_or_404(Website, id=website_id, owner=request.user)
    if request.method == 'POST':
        website.delete()
    return redirect('dashboard')

@login_required
def toggle_pause(request, website_id):
    website = get_object_or_404(Website, id=website_id, owner=request.user)
    if request.method == 'POST':
        website.is_paused = not website.is_paused
        website.save()
    return redirect('dashboard')

@login_required
def website_detail(request, website_id):
    website = get_object_or_404(Website, id=website_id, owner=request.user)
    recent_checks = website.checks.all()[:20]
    total_checks = website.checks.count()
    context = {
        'website': website,
        'recent_checks': recent_checks,
        'total_checks': total_checks,
        'uptime': website.uptime_percentage(),
        'chart_data': json.dumps(website.response_time_history()),
    }
    return render(request, 'monitor/website_details.html', context)