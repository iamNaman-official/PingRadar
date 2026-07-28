from django.core.serializers import json
from django.shortcuts import redirect, render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login as auth_login
from monitor.models import Website, StatusCheck
import json

# Create your views here.

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
    context = {
        'websites': websites
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
def website_detail(request, website_id):
    website = get_object_or_404(Website, id=website_id, owner=request.user)
    status_checks = StatusCheck.objects.filter(website=website)
    context = {
        'website': website,
        'status_checks': status_checks,
        'uptime_percentage': website.uptime_percentage(),
        'latest_status': website.latest_check(),
        'response_time_history': json.dumps(website.response_time_history()),
    }
    return render(request, 'monitor/website_details.html', context)