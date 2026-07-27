from django.urls import path

from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('signup/', views.signup, name='signup'),
    path('add/', views.add_website, name='add_website'),
    path('delete/<int:website_id>/', views.delete_website, name='delete_website'),
    path('website/<int:website_id>/', views.website_detail, name='website_detail'),

]