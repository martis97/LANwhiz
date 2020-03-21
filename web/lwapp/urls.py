"""lanwhiz URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='LANwhiz - Home'),
    path('action/', views.action),
    path('ajax/new-acl/', views.new_acl),
    path('ajax/new-routing-protocol/', views.new_routing_protocol),
    path('ajax/new-dhcp-pool/', views.new_dhcp_pool),
    path('devices/', views.devices, name='LANwhiz - Devices'),    
    path('devices/add/', views.add_device, name='LANwhiz - Add Device'),
    path('devices/<str:hostname>/term', views.handle_terminal),
    path('devices/<str:hostname>/', views.device_details, name="LANwhiz - Device"),
    path('admin', admin.site.urls)
]
