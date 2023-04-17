from django.shortcuts import render, reverse

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

from oper.models import rates_direction, context_vars
from exchange.models import Currency
from fintex.common import json_500false, json_true

from decimal import Decimal
# Create your views here.



@login_required(login_url="/oper/login/")
def oper_home(request):
    pass

@login_required(login_url="/oper/login/")
def rates_settings(request):
    directions = []
    curs = list(Currency.objects.all())
    for i in curs:
        for j in curs:
            if j.id == i.id:
                continue
            directions.append({"from": i.title, "to": j.title})

    return render(request, "oper/charts.html",
                  context={"directions": directions,
                           "title": "Exchange Operator Cabinet"},
                  content_type=None,
                  status=None,
                  using=None)


# TODO add IPs permissions
def login_page(request):
    return render(request, "oper/authentication-login.html", context=None, content_type=None, status=None, using=None)


@login_required
def test_rate(req):
    d = {}
    code4execute = req.body.decode('utf-8')

    for i in context_vars.objects.all():
        d[i.name] = float(i.value)

    # print(eval('sqrt(a)', {'__builtins__': None}, {'a': a, 'sqrt': sqrt}))
    d = eval(code4execute, {'__builtins__': None}, d)
    return json_true(req, {"result": d})


@login_required
def delete_rate(req, from_currency, to_currency):
    cur1 = Currency.objects.get(title=from_currency)
    cur2 = Currency.objects.get(title=to_currency)

    direction = rates_direction.objects.get(give_currency=cur1,
                                            take_currency=cur2)
    direction.delete()
    return json_true(req)


@login_required
def get_direction(req, from_currency, to_currency):

    cur1 = Currency.objects.get(title=from_currency)
    cur2 = Currency.objects.get(title=to_currency)

    direction, created = rates_direction.objects.get_or_create(give_currency=cur1,
                                                               take_currency=cur2)

    return json_true(req, {"raw_data": direction.raw_data})

@login_required
def save_rate(req,  from_currency, to_currency):

    cur1 = Currency.objects.get(title=from_currency)
    cur2 = Currency.objects.get(title=to_currency)

    direction, created = rates_direction.objects.get_or_create(give_currency=cur1,
                                                               take_currency=cur2)

    direction.raw_data = req.body.decode('utf-8')
    direction.save()
    return json_true(req, {"raw_data": direction.raw_data})


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


