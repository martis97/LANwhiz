import json

from django.shortcuts import render, redirect, HttpResponse
from LANwhiz.utils import Utilities as Utils
from LANwhiz.connect import Connect
from LANwhiz.web.lwapp.forms import *

connections = Connect() 

def index(request):
    """ Index Page """
    context = {}
    return render(request, 'index.html', context=context)


def devices(request):
    """ All Devices page """
    
    return render(request, 'devices.html', context=Utils.get_all_devices())


def device_details(request, hostname):


    device_config = Utils.read_config(hostname)

    access_form_initial = {
        "hostname": device_config["hostname"],
        "mgmt_ip": device_config["mgmt_ip"],
        "mgmt_port": device_config["mgmt_port"],
        "username": device_config["username"],
        "password": device_config["password"]
    }

    context = {
        "hostname": device_config["hostname"],
        "access_form": AccessForm(initial=access_form_initial),
        "int_config_form": InterfaceConfigForm(),
        "int_nat_form": NATRadioForm()
    }

    context.update(device_config["config"])

    return render(request, 'device-details.html', context=context)


def handle_terminal(request, hostname):
    """ Handles the requests for the embedded terminal of device's details
        page
    """

    connection = connections.active.get(hostname)

    if request.POST.get("cmd"):
        cmd = request.POST.get("cmd")
        if not connection:
            config = Utils.read_config(hostname)
            access = {
                "mgmt_ip": config["mgmt_ip"],
                "port": config["mgmt_port"],
                "username": config["username"],
                "password": config["password"]
            }
            connection = connections.cisco_device(**access)

    response = Utils(connection).send_command(cmd, web=True)

    return HttpResponse(response, status=200)



def add_device(request):
    """ Add Device page """    
    context = {}

    if request.POST:
        print(request.POST)
        host = request.POST.get("mgmt_ip")
        port = int(request.POST.get("mgmt_port"))
        username = request.POST.get("username")
        password = request.POST.get("password")
        params = (host, port, username, password)
        new_device = Utils.add_new_device(*params)
        return redirect(f"/devices/{new_device['hostname']}")
    else:
        return render(request, 'add-device.html', context=context)


