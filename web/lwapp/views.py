from django.shortcuts import render, redirect
from LANwhiz.utils import Utilities
from LANwhiz.connect import Connect
import json


context = {
    "name" : "User",
}


def index(request):
    """ Index Page """
    return render(request, 'index.html', context=context)


def devices(request):
    """ All Devices page """
    
    context.update(Utilities.get_all_devices())
    return render(request, 'devices.html', context=context)

def device_details(request, hostname):
    device_config = Utilities.read_config(hostname)
    context.update({
        "hostname": device_config["hostname"],
        "mgmt_ip": device_config["mgmt_ip"],
        "mgmt_port": device_config["mgmt_port"],
        "username": device_config["username"],
        "password": device_config["password"]
    })
    context.update(device_config["config"])
    return render(request, 'device-details.html', context=context)

def add_device(request):
    """ Add Device page """    
    if request.POST:
        params = ("host", "port", "username", "password")
        device_params = [request.POST.get(param) for param in params if param]
        new_device = Utilities.add_new_device(*device_params)
        return redirect(f"/devices/{new_device['hostname']}")
    else:
        return render(request, 'add-device.html', context=context)


