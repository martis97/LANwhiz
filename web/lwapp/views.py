from django.shortcuts import render, redirect
from LANwhiz.utils import Utilities
from LANwhiz.connect import Connect


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
    print("home")
    if request.GET:
        connect_to_device(request)
        return redirect("/devices/")
    else:
        return render(request, 'add-device.html', context=context)


def connect_to_device(request):
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
        print("connecting..")
        connection = connect_to.cisco_device(*params, telnet=True)
    except Exception as e:
        print("Connection failed.")
        print(f"Message: {e.args[0]}")
 