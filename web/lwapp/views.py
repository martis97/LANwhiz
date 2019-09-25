from django.shortcuts import render
from LANwhiz.utils import Utilities


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
    locals().update(request.GET)
    print(locals())
    # if request.GET.get("ip") and request.GET.get("port") \
        

    return render(request, 'add-device.html', context=context)


def connect_to_device(request):
    pass
 