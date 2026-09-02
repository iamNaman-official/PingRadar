from django.urls import path

from .views.auth import signup
from .views.dashboard import dashboard
from .views.websites import add_website, delete_website, toggle_pause, website_detail

urlpatterns = [
    path("", dashboard, name="dashboard"),
    path("signup/", signup, name="signup"),
    path("add/", add_website, name="add_website"),
    path("toggle-pause/<int:website_id>/", toggle_pause, name="toggle_pause"),
    path("delete/<int:website_id>/", delete_website, name="delete_website"),
    path("website/<int:website_id>/", website_detail, name="website_detail"),
]
