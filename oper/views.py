from django.shortcuts import render, reverse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core import serializers

from oper.models import rates_direction, context_vars, chat
from exchange.models import Currency, Orders, Invoice, Trans
from fintex.common import json_500false, json_true, date_to_str, convert2time, get_telechat_link
from django.template.loader import render_to_string

from fintex.settings import BOTAPI, COMMON_PASSWORD
import json
import requests
from datetime import datetime
from decimal import Decimal
# Create your views here.
import traceback


@login_required(login_url="/oper/login/")
def order_status(req, status, order_id):
    obj = get_object_or_404(Orders, pk=order_id)
    obj.operator = req.user

    if obj.status in ("canceled", "processed"):
        return json_500false(req)

    if obj.status in ("created", "processing"):
        obj.status = status
        obj.save()


    return json_true(req)


@login_required(login_url="/oper/login/")
def trans_status(req, status, trans_id):
    obj = get_object_or_404(Trans, pk=trans_id)
    obj.operator = req.user
    if obj.status in ("processed", ):
        # final status could not be reverted
        return json_500false(req)

    if obj.status in ("created", "processing"):
        obj.status = status
        obj.save()

    return json_true(req)


@login_required(login_url="/oper/login/")
def trans_page(req):
    return render(req, "oper/trans_page.html", context={"username": req.user.username},
                  content_type=None, status=None, using=None)


def process_item_trans(i):
    return {"id": i.id,
            "amnt": str(i.amnt),
            "account": i.account,
            "currency": i.currency.title,
            "pub_date": date_to_str(i.pub_date),
            "processed_date": date_to_str(i.processed_date) if i.processed_date else "",
            "operator": i.operator.username if i.operator else "",
            "payment_id": i.payment_id,
            "txid": i.txid,
            "status": i.status,
            "actions": render_to_string("oper/trans_menu.html",
                                        context={"item": i})
            }


@login_required(login_url="/oper/login/")
def trans(req):
    res = []
    for i in Trans.objects.all().order_by("-pub_date"):
        res.append(process_item_trans(i))

    return json_true(req, {"data": res})


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

    try:
        last = int(req.GET.get("last", None))
    except:
        last = 0

    obj = get_object_or_404(chat, pk=chat_id)

    if last is None:
        return json_true(req, {"result": json.loads(obj.history)["msgs"]})
    else:
        res = json.loads(obj.history)
        result_list = []
        if "msgs" in res:
            for i in res["msgs"]:
                if i["time"] > last:
                    result_list.append(i)

        return json_true(req, {"result": result_list})


@login_required(login_url="/oper/login/")
@csrf_exempt
def post_message(req, chat_id):
    obj = get_object_or_404(chat, pk=chat_id)
    txt = req.POST.get("txt", "")

    if len(txt) <= 1:
        return json_500false(req, {})

    resp = requests.post(BOTAPI+"alert/%s" % str(obj.telegram_id), json={"text": txt})
    if resp.status_code != 200:
        return json_500false(req, {})
    else:
        result = json.loads(obj.history)
        msgs = result["msgs"]
        n = datetime.now()
        nt = convert2time(n)
        msgs.append({"time": nt, "username": req.user.username, "text": txt})
        result["msgs"] = msgs
        obj.history = json.dumps(result)
        obj.save()
        return json_true(req, {"time": nt})


# TODO add token auth
@csrf_exempt
def message_income(req, chat_id):
    body_unicode = req.body.decode('utf-8')
    body = json.loads(body_unicode)
    obj = get_object_or_404(chat, pk=chat_id)
    txt = body.get("text", "")
    username = body.get("username", "")
    result = json.loads(obj.history)
    print(result)
    if "msgs" not in result:
        result["msgs"] = []
    msgs = result["msgs"]
    nt = datetime.now()
    msgs.append({"time": convert2time(nt), "username": username, "text": txt})
    result["msgs"] = msgs
    obj.history = json.dumps(result)
    obj.save()
    return json_true(req, {"time": nt})


# TODO add token auth
@csrf_exempt
def deal2telegram(req):
    chat_id = req.GET.get("chat_id", "")
    obj = chat.objects.filter(telegram_id=chat_id).first()
    deal = Orders.objects.filter(user=obj.deal.user, status__in=["processing", "created"]).last()
    obj = chat.objects.get(deal=deal)
    # TODO add welcome message through inner API
    res_dict = {"token": str(obj.uuid), "deal": json.loads(serializers.serialize("json", [deal]))}
    print(res_dict)
    return json_true(req, res_dict)


# TODO add token auth
@csrf_exempt
def telegram2deal(req):

    body_unicode = req.body.decode('utf-8')
    body = json.loads(body_unicode)
    userf = body["from"]
    uuid = body["token"]
    chat_id = body["chat_id"]
    obj = get_object_or_404(chat, pk=uuid)
    obj.telegram_id = chat_id
    obj.save()
    user = None
    try:
        user = User.objects.get(username=userf["username"])
    except User.DoesNotExist:
        user = User.objects.create_user(userf["username"],
                                        "%s@t.me" % userf["username"],
                                        COMMON_PASSWORD)

        user.first_name = userf["first_name"]
        user.last_name = userf["last_name"]
        user.save()
    finally:
        obj.deal.user = user
        obj.deal.save()

    # TODO add welcome message through inner API
    return json_true(req, {"deal": json.loads(serializers.serialize("json", [obj.deal]))})


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

    invoice = Invoice.objects.get(order=i)

    return {"id": i.id,
            "buy": str(i.amnt_give) + " " + i.give_currency.title,
            "sell": str(i.amnt_take) + " " + i.take_currency.title,
            "pub_date": date_to_str(i.pub_date),
            "operator": username,
            "client_info": "Ukraine",
            # TODO add invoice of payment
            "client_payed": invoice.status,
            "client_get": i.trans.status,
            "client_telegram_connected": connected,
            "status": i.status,
            "rate": i.rate,
            "actions": render_to_string("oper/deals_menu.html",
                                        context={"item": i,
                                                 "connected": connected,
                                                 "telechat_link": get_telechat_link(i),
                                                 "chat_link": reverse("to_history_page", args=[i.id])})
            }


@login_required(login_url="/oper/login")
def show_payment(req, order_id):
    obj = get_object_or_404(Orders, pk=order_id)

    return json_true(req, {"trans": json.loads(serializers.serialize("json", [obj.trans]))})


@login_required(login_url="/oper/login/")
def oper_orders(request):

    res = []
    for i in Orders.objects.all().order_by("id"):
        try:
            result_dict = process_item(i)
        except:
            traceback.print_exc()
            continue
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
        return json_true(request, {"redirect": reverse(oper_home)})

    else:
        # Return an 'invalid login' error message
        return json_500false(request, {"description": "invalid login"})


def logout_view(request):
    logout(request)
    return json_true(request, {"redirect": reverse(login_page)})

#TODO
def reset_pwd_request(req):
    pass


