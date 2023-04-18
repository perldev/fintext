from django.shortcuts import render, reverse

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

from oper.models import rates_direction, context_vars, chat, get_telechat_link
from exchange.models import Currency, Orders
from fintex.common import json_500false, json_true, date_to_str
from django.template.loader import render_to_string

from decimal import Decimal
# Create your views here.


def order_status(req, status, order):
    pass

def to_history(req, order):
    pass

def get_history(req, order):
    pass


def process_item(i):
    #    {
    #        "data": [
    #            {
    #                "id": "1",
    #                "name": "Tiger Nixon",
    #                "position": "System Architect",
    #                "salary": "$320,800",
    #                "start_date": "2011/04/25",
    #                "office": "Edinburgh",
    #                "extn": "5421"
    # rewrite this
    connected = True
    d = None
    d = chat.objects.get(deal=i)
    if d.telegram_id is None:
        connected = False
    connected = True

    return {"id": i.id,
            "buy": i.amnt_give + " " + i.give_currency.title,
            "sell": i.amnt_take + " " + i.give_take.title,
            "pub_date": date_to_str(i.pub_date),
            "operator": i.operator.username,
            "client_info": "Ukraine",
            # TODO add invoice of payment
            "client_payed": "not created",
            "client_get": "not_created",
            "client_telegram_connected": connected,
            "status": i.status,
            "actions": render_to_string("deals_menu.html", context={"item": i,
                                                                    "connected": connected,
                                                                    "chat_link": get_telechat_link(d) })
            }


@login_required(login_url="/oper/login/")
def oper_orders(request):

    res = []
    for i in Orders.objects.all().order_by("id"):
        result_dict = process_item(i)
        res.append(res)

    return json_true(request, {"data": res})


@login_required(login_url="/oper/login/")
def oper_home(request):

    return render(request, "oper/tables.html",
                  context={"title": "Exchange Operator Cabinet"},
                  content_type=None,
                  status=None,
                  using=None)


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


