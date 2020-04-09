import json
from threading import Thread
from datetime import datetime

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
    print(request.POST)

    access_form_initial = {
        "hostname": device_config["hostname"],
        "mgmt_ip": device_config["mgmt_ip"],
        "mgmt_port": device_config["mgmt_port"],
        "username": device_config["username"],
        "password": device_config["password"]
    }

    print(AccessForm(request.POST, initial=access_form_initial).has_changed())   

    if device_config["config"].get("global_commands"):
        global_cmds = ",".join(device_config["config"]["global_commands"])
    else:
        global_cmds = ""

    context = {
        "hostname": device_config["hostname"],
        "access_form": AccessForm(initial=access_form_initial), 
        "last_modified": device_config["last_modified"],
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
        initial = FormInitials.interface_config(config)
        context["int_config"][interface] = InterfaceConfigForm(prefix=interface, initial=initial)

        if config.get("ipv4"): 
            net_addr, prefix = Utils.get_network_address(config["ipv4"])
            context["ospf_nets_to_advertise"].append(f"{net_addr}/{prefix}")

    if device_config["config"].get("lines"):
        
        for line, config in device_config["config"]["lines"].items():
            initial = FormInitials.line_config(config)
            context["line_config"][line] = LineConfigForm(prefix=line, initial=initial)

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
        
        for pool_name, config in dhcp_pools.items():
            config["pool_name"] = pool_name
            context["dhcp_pools"].append(
                (pool_name, DHCPPoolForm(prefix=pool_name, initial=config))
            )


    return render(request, 'device-details.html', context=context)

def merge_config(current, new):
    print("merge")
    for k, v in new.items():
        if isinstance(v, dict):
            current[k] = merge_config(current.get(k, {}), v)
        else:
            current[k] = v
    return current

def diff_config(request, hostname):
    form_diff = FormDiff(request.POST)
    current = Utils.read_config(hostname)["config"]
    changes = {
        "global_commands": [],
        "interfaces": form_diff.interface_config(current.get("interfaces")),
        "lines": form_diff.line_config(current.get("lines")),
        "routing": form_diff.routing(current.get("routing")),
        "acl": form_diff.acl(current.get("acl")),
        "dhcp": form_diff.dhcp(current.get("dhcp"))
    }

    global_cmds = request.POST.get("global_commands").split(",")

    if set(global_cmds) != set(current["global_commands"]):
        changes["global_commands"].append(
           [current['global_commands'], global_cmds]
        )

    print(json.dumps(changes, indent=4))
    # print(json.dumps(merge_config(current, changes), indent=4))
    if request.GET.get("save"):
        
        response = {}
    else:
        response = {"changed": [
            area.capitalize().replace("_", " ") \
                for area, values in changes.items() if values
        ]}

    return JsonResponse(response)


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
        "cmd_out": cmd_out.split("\n")[1:-1] if  cmd_out else None
    }

    return JsonResponse(response, status=200)


def add_device(request):
    """ Add Device page """    

    if request.POST:
        params = [request.POST.get(param) for param in [
            "mgmt_ip", "mgmt_port", "username", "password"
        ]]
        new_device = Utils.add_new_device(*params)
        return redirect(f"/devices/{new_device['hostname']}")
    else:
        return render(request, 'add-device.html')


def new_acl(request):
    acl_type = request.GET.get("acl_type")
    acl_name = request.GET.get("acl_name")
    hostname = request.GET.get("hostname")
    config = Utils.read_config(hostname)

    acl_types = {
        "standard": StandardACLForm(prefix=acl_name),
        "extended": ExtendedACLForm(prefix=acl_name)
    }

    if acl_type == "standard":
        acl_config = {
            "action": None,
            "source": ""
        }
    elif acl_type == "extended":
        acl_config = {
            "action": None,
            "protocol": "",
            "source": "",
            "destination": "",
            "port": ""
        }

    if config["config"].get("acl"):
        config["config"]["acl"][acl_type][acl_name] = acl_config
    else:
        config["config"]["acl"] = {
            "standard": {},
            "extended": {}
        }
        config["config"]["acl"][acl_type][acl_name] = acl_config
    
    Utils.write_config(hostname, config)

    return JsonResponse({
        "acl_type": acl_type, 
        "form": acl_types[acl_type].as_table()
    })

def remove_acl(request):
    acl_type = request.GET.get("acl_type")
    acl_name = request.GET.get("acl_name")
    hostname = request.GET.get("hostname")
    config = Utils.read_config(hostname)
    try:
        config["config"]["acl"][acl_type].pop(acl_name, None)
        Utils.write_config(hostname, config)
        return JsonResponse({
            "acl_name": acl_name,
            "acl_type": acl_type,
            "removed": True
        })
    except:
        return JsonResponse({"removed": False})


def new_routing_protocol(request):
    protocol = request.GET.get("protocol")
    hostname = request.GET.get("hostname")
    config = Utils.read_config(hostname)

    available_protocols = {
        "OSPF": OSPFConfigForm().as_table()
    }

    config["config"]["routing"][protocol] = {
        "instance_id": "",
        "router_id": "",
        "advertise_static": False,
        "advertise_networks": [],
        "passive_interfaces": []
    }

    Utils.write_config(hostname, config)

    return JsonResponse({
        "form": available_protocols[protocol]
    })

def dhcp_pool(request):
    hostname = request.GET.get("hostname")
    pool_name = request.GET.get("pool_name")
    config = Utils.read_config(hostname)

    if request.GET.get("action") == "remove":

        for i, pool in enumerate(config["config"]["dhcp"]):
            if pool["pool_name"] == pool_name:
                config["config"]["dhcp"].pop(i)

        Utils.write_config(hostname, config)

        return JsonResponse({"removed": True})

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

def new_loopback_interface(request):
    hostname = request.GET.get("hostname")
    config = Utils.read_config(hostname)
    number = request.GET.get("number")
    config["config"]["interfaces"][f"Loopback{number}"] = {
        "ipv4": "",
        "ipv6": "",
        "description": "",
        "acl": {
            "outbound": [],
            "inbound": []
        },
        "nat": "",
        "other_commands": []
    }

    Utils.write_config(hostname, config)

    return JsonResponse({
        "form": InterfaceConfigForm(prefix=f"Loopback{number}").as_table()
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


