from django.shortcuts import render


context = {
    "name" : "User",
}


def index(request):
    """ Index Page """

    return render(request, "templates/backbone.html", context=context)