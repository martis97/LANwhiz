import json
from threading import Thread

from django.shortcuts import render, redirect, HttpResponse
from django.http import JsonResponse

from LANwhiz.utils import Utilities as Utils
from LANwhiz.connect import Connect
from LANwhiz.web.lwapp.forms import *

connections = Connect() 

def index(request):
    """ Index Page """
    
    devices = Utils.get_all_devices()

    context = {
        "capture_output_cmds": [
            "show ip route",
            "show ip protocols",
            "show ip interface brief",
            "show running-config",
            "show startup-config"
        ],
        "devices": devices["routers"] + devices["switches"]
    }

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
        "global_commands": GlobalCmdsForm(initial={
            "global_commands": global_cmds
        }),
        "int_config": {},
        "line_config": {},
        "static_routes": [],
        "dynamic_routing": []
    }

    for interface, config in device_config["config"]["interfaces"].items():
        int_config_initial = {
            "ipv4": config.get("ipv4"),
            "ipv6": config.get("ipv6"),
            "description": config.get("description"),
            "nat": config["nat"] if config.get("nat") else "off",
            "other_commands": ",".join(config["other_commands"]) \
                                if config.get("other_commands") else ""
        }

        if config.get("acl"):
            int_config_initial.update({
                "inbound_acl": ",".join(config["acl"].get("inbound")),
                "outbound_acl": ",".join(config["acl"].get("outbound")),
            })

        context["int_config"][interface] = InterfaceConfigForm(
            initial=int_config_initial,
            prefix=interface
        )

    if device_config["config"].get("lines"):
        for line, config in device_config["config"]["lines"].items():
            line_config_initial = {
                "password": config["password"],
                "synchronous_logging": config["synchronous_logging"]
            }

            if config.get("acl"):
                int_config_initial.update({
                    "inbound_acl": ",".join(config["acl"].get("inbound")),
                    "outbound_acl": ",".join(config["acl"].get("outbound")),
                })
            context["line_config"][line] = LineConfigForm(
                initial=line_config_initial,
                prefix=line
            )

    if device_config["config"].get("routing"):
        if device_config["config"]["routing"].get("static"):
            context["static_routes"] = device_config["config"]["routing"]["static"]
        if device_config["config"]["routing"].get("ospf"):
            context["dynamic_routing"].append(device_config["config"]["routing"]["ospf"])

    print(context)

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


def action(request):
    post = [i[0] for i in list(dict(request.POST).values())[1:]]
    cmds =  []
    devices = []

    for i, data in enumerate(post):
        if data == "cmd":
            cmds.append(post[i + 1])
        elif data == "device":
            devices.append(post[i + 1])
    
    for device in devices:
        Thread(target=send_cmd_outputs, kwargs={
            "device": device, 
            "cmds": cmds
        }).start()

    return JsonResponse({"started": 1})
    

def send_cmd_outputs(device, cmds):
    response = {
        "device": device,
        "cmd_outs": {}
    }
    connection = connections.active.get(device)
    if not connection:
        config = Utils.read_config(device)
        access = {
            "mgmt_ip": config["mgmt_ip"],
            "port": config["mgmt_port"],
            "username": config["username"],
            "password": config["password"]
        }
        try:
            connection = connections.cisco_device(**access)
        except Exception:
            JsonResponse({"error": f"Could not connect to {device}"}, status=200)

    for cmd in cmds:
        response[cmd] = Utilities(connection).send_command(cmd)
    
    return JsonResponse(response, status=200)


