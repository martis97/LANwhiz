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

    print(json.dumps(dict(request.POST), indent=4))

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
        "static_routes": "",
        "new_static_route": NewStaticRouteForm(),
        "dynamic_routing": [],
        "ospf_nets_to_advertise": [],
        "acl": {
            "standard": [],
            "extended": []
        },
        "dhcp_pools": []
    }

    for interface, config in device_config["config"]["interfaces"].items():
        context["int_config"][interface] = get_interface_config_initial(
            interface, config
        )

        if config.get("ipv4"): 
            net_addr, prefix = Utils.get_network_address(config["ipv4"])
            context["ospf_nets_to_advertise"].append(f"{net_addr}/{prefix}")


    if device_config["config"].get("lines"):
        for line, config in device_config["config"]["lines"].items():
            context["line_config"][line] = get_line_config_initial(line, config)

    if device_config["config"].get("routing"):

        if device_config["config"]["routing"].get("static"):
            static_routes = []
            for route in device_config["config"]["routing"]["static"]:
                static_routes.append("-".join(route.values()))
            context["static_routes"] = ",".join(static_routes)

        
        if device_config["config"]["routing"].get("ospf"):
            form_init = device_config["config"]["routing"]["ospf"]
            form_init["advertise_networks"] = ",".join(form_init.get("advertise_networks"))
            form_init["passive_interfaces"] = ",".join(form_init.get("passive_interfaces"))
            if form_init.get("other_commands"):
                form_init["other_commands"] = ",".join(form_init["other_commands"])
            context["dynamic_routing"].append(("OSPF", OSPFConfigForm(initial=form_init)))

    if device_config["config"].get("acl"):
        acls = device_config["config"]["acl"]
        acl_types = (
            ("standard", StandardACLForm), 
            ("extended", ExtendedACLForm)
        )
        for acl_type, form in acl_types:
            if acls.get(acl_type):
                for acl_id, meta in acls[acl_type].items():
                    context["acl"][acl_type].append(
                        (acl_id, form(prefix=acl_id, initial=meta))
                    )
    
    if device_config["config"].get("dhcp"):
        dhcp_pools = device_config["config"]["dhcp"]
        for pool in dhcp_pools:
            name = pool["pool_name"]
            context["dhcp_pools"].append(
                (name, DHCPPoolForm(prefix=name, initial=pool))
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
        params = [request.POST.get(param) for param in [
            "mgmt_ip", "mgmt_port", "username", "password"
        ]]
        new_device = Utils.add_new_device(*params)
        return redirect(f"/devices/{new_device['hostname']}")
    else:
        return render(request, 'add-device.html', context=context)


def new_acl(request):
    acl_type = request.GET.get("acl_type")
    acl_name = request.GET.get("acl_name")
    acl_types = {
        "standard": StandardACLForm(prefix=acl_name),
        "extended": ExtendedACLForm(prefix=acl_name)
    }

    return JsonResponse({
        "acl_type": acl_type, 
        "form": acl_types[acl_type].as_table()
    })

def new_routing_protocol(request):
    protocol = request.GET.get("protocol")

    protocols = {
        "OSPF": OSPFConfigForm().as_table()
    }

    return JsonResponse({
        "form": protocols[protocol]
    })

def new_dhcp_pool(request):
    hostname = request.GET.get("hostname")
    pool_name = request.GET.get("pool_name")
    config = Utils.read_config(hostname)
    new_pool = {
        "pool_name": pool_name,
        "network": "",
        "default_gateway": "",
        "dns": ""
    }

    if config["config"].get("dhcp"): 
        config["config"]["dhcp"].append(new_pool)
    else:
        config["config"]["dhcp"] = [new_pool]

    Utils.write_config(hostname, config)    

    return JsonResponse({
        "form": DHCPPoolForm(
            prefix=pool_name,
            initial={"pool_name": pool_name}
        ).as_table()
    })


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
        response["cmd_outs"][cmd] = Utilities(connection).send_command(cmd)
    
    return JsonResponse(response, status=200)


