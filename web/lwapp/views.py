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
    if request.GET.get("hostname"):
        hostname = request.GET.get("hostname")
        context.update(Utilities.read_config(hostname))
        return render(request, 'device-details.html', context=context)
        
    context.update(Utilities.get_all_devices())
    return render(request, 'devices.html', context=context)


def add_device(request):
    """ Add Device page """    
    if request.GET:
        new_device = add_new_device(request)
        return redirect(f"/devices/?hostname={new_device['hostname']}")
    else:
        return render(request, 'add-device.html', context=context)


def add_new_device(request):
    """ Connect to device and create a JSON record of it """
    host = request.GET.get("host")
    port = request.GET.get("port")
    username = request.GET.get("username")
    password = request.GET.get("password")
   
    params = [host, port]

    if username and password:
        params += [username, password]

    connect_to = Connect()
    
    try:
        print("Connecting..")
        connection = connect_to.cisco_device(*params, telnet=True)
    except Exception as e:
            print("Connection failed.")
            print(f"Message: {e.args[0]}")

    utils = Utilities(connection)
    hostname = connection.find_prompt().rstrip("#")

    new_config = {
        "hostname": hostname,
        "mgmt_ip": host,
        "mgmt_port": port,
        "username": username if username else "",
        "password": password if password else "",    # Use Salting/Hashing/Secure Storage
        "config": utils.build_initial_config_template()
    }

    with open(
        f"{utils.home_path}routers/{hostname}.json", "w"
    ) as config_file:
        config_file.write(json.dumps(new_config, indent=4))

    return new_config