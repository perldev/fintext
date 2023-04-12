from django.shortcuts import render, reverse

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

from fintex.common import json_500false, json_true
# Create your views here.


@login_required(login_url="/oper/login/")
def index(request):
    return render(request, "oper/charts.html", context=None, content_type=None, status=None, using=None)


#TODO add IPs permissions
def login_page(request):
    return render(request, "oper/authentication-login.html", context=None, content_type=None, status=None, using=None)


def try_login(request):
    username = request.POST["username"]
    password = request.POST["password"]
    user = authenticate(request, username=username, password=password)
    if user is not None:
        login(request, user)
        return json_true(request, {"redirect": reverse(index)})

    else:
        # Return an 'invalid login' error message
        return json_500false(request, {"description": "invalid login"})


def logout_view(request):
    logout(request)
    return json_true(request, {"redirect": reverse(login_page)})


#TODO
def reset_pwd_request(req):
    pass


