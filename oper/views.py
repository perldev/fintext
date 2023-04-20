from django.shortcuts import render, reverse


from django.shortcuts import get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

from oper.models import rates_direction, context_vars, chat, get_telechat_link
from exchange.models import Currency, Orders
from fintex.common import json_500false, json_true, date_to_str, convert2time
from django.template.loader import render_to_string

from fintex.settings import BOTAPI
import json
import requests
from datetime import datetime
from decimal import Decimal
# Create your views here.


@login_required(login_url="/oper/login/")
def order_status(req, status, order_id):
    obj = get_object_or_404(Orders, pk=order_id)

    if obj.status in ("canceled", "processed"):
        return json_500false(req)

    if obj.status in ("created", "processing"):
        obj.status = status
        obj.save()

    return json_true(req)


@login_required(login_url="/oper/login/")
def to_history_page(req, deal):
    obj = get_object_or_404(chat, deal_id=deal)
    return render(req,
                  "oper/chat_page.html", context={"chat_obj": obj,
                                                  "username": req.user.username},
                  content_type=None,
                  status=None, using=None)


# TODO add to cache
@login_required(login_url="/oper/login/")
def get_history(req, chat_id):
    last = int(req.GET.get("last", None))
    obj = get_object_or_404(chat, pk=chat_id)

    if last is None:
        return json_true(req, {"result": json.loads(obj.history)["msgs"]})
    else:
        res = json.loads(obj.history)
        result_list = []
        for i in res:
            if i["time"]>last:
                result_list.append(i)

        return json_true(req, {"result": result_list})


@login_required(login_url="/oper/login/")
def post_message(req, chat_id):
    obj = get_object_or_404(chat, pk=chat_id)
    txt = req.POST("txt", "")

    if len(txt) <= 1:
        return json_500false(req)

    resp = requests.post(BOTAPI+"alert/%s" % str(obj.telegram_id), json={"text": txt})
    if resp.status_code != 200:
        return json_500false(req)
    else:
        result = json.loads(obj.history)
        msgs = result["msgs"]
        n = datetime.now()
        nt = convert2time(n)
        msgs.append({"time": nt, "username": req.user.username, "text": txt})
        result["msgs"] = msgs
        obj.history = json.dumps(result)
        return json_true(req, {"time": nt})


# TODO add token auth
def message_income(req, chat_id):
    obj = get_object_or_404(chat, pk=chat_id)
    txt = req.POST("text", "")
    username = req.POST("username", "")
    result = json.loads(obj.history)
    msgs = result["msgs"]
    n = datetime.now()
    msgs.append({"time": nt, "username": req.user.username, "text": txt})
    result["msgs"] = msgs
    obj.history = json.dumps(result)
    return json_true(req, {"time": nt})


#TODO add token auth
def telegram2deal(req):
    uuid = req.POST("token", "")
    chat_id = req.POST("chat_id", "")
    obj = get_object_or_404(chat, pk=uuid)
    obj.telegram_id = chat_id
    obj.save()
    # TODO add welcome message through inner API
    return json_true(req)


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
    username = ""

    if i.operator is not None:
        username = i.operator.username

    return {"id": i.id,
            "buy": str(i.amnt_give) + " " + i.give_currency.title,
            "sell": str(i.amnt_take) + " " + i.take_currency.title,
            "pub_date": date_to_str(i.pub_date),
            "operator": username,
            "client_info": "Ukraine",
            # TODO add invoice of payment
            "client_payed": "not created",
            "client_get": "not_created",
            "client_telegram_connected": connected,
            "status": i.status,
            "rate": i.rate,
            "actions": render_to_string("oper/deals_menu.html",
                                        context={"item": i,
                                                 "connected": connected,
                                                 "chat_link": reverse("to_history_page", args=[i.id])})
            }


@login_required(login_url="/oper/login/")
def oper_orders(request):

    res = []
    for i in Orders.objects.all().order_by("id"):
        result_dict = process_item(i)
        res.append(result_dict)
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


