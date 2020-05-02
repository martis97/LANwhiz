import json
import re
from threading import Thread
from time import strftime, localtime
from copy import deepcopy

from django.shortcuts import render, redirect, HttpResponse
from django.http import JsonResponse

from LANwhiz.utils import Utilities as Utils
from LANwhiz.connect import Connect
from LANwhiz.web.lwapp.forms import *
from LANwhiz.main import LANwhizMain

connections = Connect()

def output_capture(request):
    """ Index Page """
    
    devices = Utils.get_all_devices()["devices"]

    context = {
        "capture_output_cmds": [
            "show ip route",
            "show ip protocols",
            "show ip interface brief",
            "show running-config",
            "show startup-config"
        ],
        "devices": devices
    }

    return render(request, 'output-capture.html', context=context)


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
        global_cmds = None

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
            pattern = re.compile(
                r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b\/\d{1,2}"
            )
            if re.match(pattern, config["ipv4"]):
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
            else:
                form_init["other_commands"] = ""
            
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
            context["dhcp_pools"].append(
                (pool_name, DHCPPoolForm(prefix=pool_name, initial=config))
            )


    return render(request, 'device-details.html', context=context)

def merge_config(current, new):
    for k, v in new.items():
        if isinstance(v, dict):
            current[k] = merge_config(current.get(k, {}), v)
        else:
            current[k] = v
    return current

def diff_config(request, hostname):
    form_diff = FormDiff(request.POST)
    current_template = Utils.read_config(hostname)
    new_template = deepcopy(current_template)
    current = current_template["config"]
    # print(current)
    changes = {
        "global_commands": [],
        "interfaces": form_diff.interface_config(current.get("interfaces")),
        "lines": form_diff.line_config(current.get("lines")),
        "routing": form_diff.routing(current.get("routing")),
        "acl": form_diff.acl(current.get("acl")),
        "dhcp": form_diff.dhcp(current.get("dhcp"))
    }
    if request.POST.get("global_commands"):
        global_cmds = request.POST.get("global_commands").split(",")
    else:
        global_cmds = []

    # if the device contains any global commands, compare them
    if current.get("global_commands"):
        if set(global_cmds) != set(current["global_commands"]):
            changes["global_commands"] = global_cmds
    # otherwise, apply the input from the UI
    else:
        changes["global_commands"] = global_cmds

    changes = {k:v for k, v in changes.items() if v}
    print(json.dumps(changes, indent=4))

    if request.GET.get("save"):
        new_template["config"] = merge_config(current, changes)
        new_template["last_modified"] = strftime("%d/%m/%Y %H:%M:%S", localtime())
        Utils.write_config(hostname, new_template)

        response = {
            "saved": True,
            "time_updated": new_template["last_modified"]
        }

        thread = Thread(
            target=LANwhizMain.update_cisco_device, 
            kwargs={
                "hostname": hostname,
                "update": changes.keys()
            }
        )

        thread.start()

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
    if cmd:
        cmd_out = Utils(connection).send_command(cmd, web=True).split("\n")
        if len(cmd_out) > 1:
            if not "Invalid input" in cmd_out[1]:
                cmd_out = cmd_out[1:-1]
            
    else:
        cmd_out = None 
    response = {
        "prompt": cmd_out[-1],
        "cmd_out": cmd_out if  cmd_out else None
    }

    return JsonResponse(response, status=200)


def add_device(request):
    """ Add Device page """    

    if request.POST:
        form = AddDeviceForm(request.POST)
        if form.is_valid():
            params = {param: form.cleaned_data.get(param) for param in [
                "mgmt_ip", "mgmt_port", "username", "password"
            ]}
            new_hostname = request.GET.get("new_hostname")
            new_device = Utils.add_new_device(**params, new_hostname=new_hostname)
            return redirect(f"/devices/{new_device['hostname']}")
        else:
            print(form.errors)
            return JsonResponse({})
    else:
        return render(request, 'add-device.html', context={"form": AddDeviceForm()})


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
            "action": "",
            "source": ""
        }
    elif acl_type == "extended":
        acl_config = {
            "action": "",
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
    print(json.dumps(config, indent=4))

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
    protocol = request.GET.get("protocol").lower()
    hostname = request.GET.get("hostname")
    config = Utils.read_config(hostname)

    available_protocols = {
        "ospf": OSPFConfigForm().as_table()
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
        del config["config"]["dhcp"][pool_name]
        Utils.write_config(hostname, config)

        return JsonResponse({"removed": True})

    new_pool = {
        "network": "",
        "default_gateway": "",
        "dns": ""
    }

    config["config"]["dhcp"][pool_name] = new_pool

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
    

def capture_cmd_outputs(request, hostname):
    response = {
        "device": hostname,
        "cmd_outs": {}
    }
    cmds = dict(request.POST)["cmds[]"]
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
        except Exception:
            JsonResponse({"error": f"Could not connect to {hostname}"}, status=200)

    for cmd in cmds:
        response["cmd_outs"][cmd] = Utilities(connection).send_command(cmd)
    
    return JsonResponse(response, status=200)


