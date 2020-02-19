import json

from django.shortcuts import render, redirect, HttpResponse
from django.http import JsonResponse
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

    if device_config["config"].get("global_commands"):
        global_cmds = ",".join(device_config["config"]["global_commands"])

    context = {
        "hostname": device_config["hostname"],
        "access_form": AccessForm(initial=access_form_initial), 
        "global_cmds": GlobalCmdsForm(initial=global_cmds),
        "int_config": {}
    }

    for interface, config in device_config["config"]["interfaces"].items():
        if config.get("acl"):
            int_config_initial = {
                "inbound_acl": ",".join(config["acl"].get("inbound")),
                "outbound_acl": ",".join(config["acl"].get("outbound")),
                "nat": config["nat"] if config.get("nat") else "off"
            } 
        else: 
            int_config_initial = {
                "nat": config["nat"] if config.get("nat") else "off"
            }

        context["int_config"][interface] = InterfaceConfigForm(
            initial=int_config_initial
        )

    return render(request, 'device-details.html', context=context)


def handle_terminal(request, hostname):
    """ Handles the requests for the embedded terminal of device's details
        page
    """

    connection = connections.active.get(hostname)
    if not connection:
        config = Utils.read_config(hostname)
        access = {
            "mgmt_ip": config["mgmt_ip"],
            "port": config["mgmt_port"],
            "username": config["username"],
            "password": config["password"]
        }
        try:
            connection = connections.cisco_device(**access)
        except Exception as e:
            return JsonResponse({"error": e.args[1]}, status=200)

    cmd = request.POST.get("cmd")
    cmd_out = None if not cmd else Utils(connection).send_command(cmd, web=True)

    response = {
        "prompt": connection.find_prompt(),
        "cmd_out": None if not cmd_out else cmd_out.split("\n")[1:-1]
    }

    return JsonResponse(response, status=200)



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


