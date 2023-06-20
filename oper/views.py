from django.shortcuts import render, reverse, redirect
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core import serializers
from fintex.common import convert2time
from sdk.factory import CryptoFactory
from oper.models import rates_direction, context_vars, chat
from exchange.models import Currency, Orders, Invoice, Trans, OperTele, PoolAccounts
from fintex.common import json_500false, json_true, date_to_str, convert2time, get_telechat_link
from django.template.loader import render_to_string
from fintex.common import format_numbers10
from fintex.settings import BOTAPI, COMMON_PASSWORD, OPERTELEBOT, FIAT_CURRENCIES, CRYPTO_CURRENCY
import json
import requests
from datetime import datetime
from decimal import Decimal
# Create your views here.
import traceback
from wallet.models import CryptoAccounts

from exchange.controller import tell_update_order as tell_controller_update_order
from exchange.controller import tell_trans_check as tell_controller_trans_check
from exchange.controller import tell_invoice_check as tell_controller_invoice_check
from exchange.controller import tell_aml_check
from wallet.models import get_full_data

@login_required(login_url="/oper/login/")
def order_status(req, status, order_id):
    obj = get_object_or_404(Orders, pk=order_id)
    obj.operator = req.user

    if obj.status in ("canceled", "processed"):
        return json_500false(req)

    if obj.status in ("created", "processing"):
        obj.status = status
        obj.save()
        tell_controller_update_order("order_api_status_function", obj)

    return json_true(req)


@login_required(login_url="/oper/login/")
def settings(req):
    if not req.user.is_superuser:
        return json_500false(req)

    avalible_settings = {
        "riskbtc": True,
        "risketh": True,
        "riskerc20": True,
        "risktron": True,
        "riskusdt": True,
        "telegram_bot_token": True,
        "infura_key": True,
        "tron_key": True,
        "aml_access_id": True,
        "aml_access_token": True,
        "white_bit_api_key": True,
        "white_bit_api_private": True,
    }
    for i in avalible_settings.keys():
        obj, created = context_vars.objects.using("security").get_or_create(name=i)
        avalible_settings[i] = obj.value

    return render(req, "oper/settings.html", context={"vars": avalible_settings})


@login_required(login_url="/oper/login/")
def settings_edit(req):
    if not req.user.is_superuser:

        return json_500false(req)

    avalible_settings = {
        "riskbtc": True,
        "risketh": True,
        "riskerc20": True,
        "risktron": True,
        "riskusdt": True,
        "telegram_bot_token": True,
        "infura_key": True,
        "tron_key": True,
        "aml_access_id": True,
        "aml_access_token": True,
        "white_bit_api_key": True,
        "white_bit_api_private": True,
    }
    name = req.POST.get("name", False)
    value = req.POST.get("val", False)
    if name not in avalible_settings:
        return json_500false(req, {"description": "no name"})

    if not value:
        return json_500false(req, {"description": "no val"})

    context_vars.objects.using("security").filter(name=name).update(value=value)

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
        tell_controller_trans_check("order_api_status_function", obj)

    return json_true(req)


@login_required(login_url="/oper/login/")
def trans_page(req):
    return render(req, "oper/trans_page.html", context={"username": req.user.username},
                  content_type=None, status=None, using=None)


def process_item_trans(i):
    return {
            "pk": i.id,
            "id": i.id,
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
    for i in Trans.objects.all().order_by("id"):
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


@login_required(login_url="/oper/login/")
def wallets(req):
    wallets_title = [{"name": "BTC", "value": "BTC"},
                     {"name": "ETH", "value": "ETH"},
                     {"name": "Tron USDT", "value": "tron_usdt"},
                     {"name": "ERC USDT", "value": "erc_usdt"}]
    return render(req, "oper/wallets.html", context={"titles": wallets_title})


def process_wallet_item(item, factory=None):
    try:
        if len(item.technical_info) == 0:
            item.technical_info = factory.get_balance(item.address)
            item.save()
    except:
        traceback.print_exc()
        pass

    if factory.network != "native" and len(item.ext_info) == 0:
        item.ext_info = factory.native_balance(item.address)
        item.save()

    is_sweep = False
    if item.address == factory.default_address:
        item.ext_info = item.ext_info + ", Адрес выплат"
        is_sweep = True

    return {"id": item.id,
            "balance": format_numbers10(factory.amnt_to_human(item.technical_info)),
            "ext_info": item.ext_info,
            "is_sweep": is_sweep,
            "account": item.address,
            "status": item.status,
            "actions": render_to_string("oper/wallets_menu.html",
                                        context={"item": item})}


@csrf_exempt
@login_required(login_url="/oper/login/")
def wallets_list(req, chanel):
    wallets_title = {"BTC": lambda: PoolAccounts.objects.filter(currency__title="btc"),
                     "ETH": lambda: PoolAccounts.objects.filter(currency__title="eth"),
                     "tron_usdt": lambda: PoolAccounts.objects.filter(currency__title="usdt",
                                                                      currency_provider__title="tron"),
                     "erc_usdt": lambda: PoolAccounts.objects.filter(currency__title="usdt",
                                                                     currency_provider__title="erc20")}

    wallets_factories = {
                         "BTC": lambda: CryptoFactory("btc"),
                         "ETH": lambda: CryptoFactory("eth"),
                         "tron_usdt": lambda: CryptoFactory("usdt", network="tron"),
                         "erc_usdt": lambda: CryptoFactory("usdt", network="erc20"),
                         }

    if chanel not in wallets_title:
        return json_500false(req, {"description": "title not supported"})

    res = []
    factory = wallets_factories[chanel]()
    context_var, created = context_vars.objects.get_or_create(name=factory.currency + "_" + factory.network + "_forpayment")
    factory.set_default(context_var.value)

    for i in wallets_title[chanel]():
        res.append(process_wallet_item(i,  factory))

    return json_true(req, {"data": res})


@csrf_exempt
@login_required(login_url="/oper/login/")
def wallets_make_withdraw(req, wallet):
    obj = get_object_or_404(PoolAccounts, pk=wallet)
    context_obj, created = context_vars.objects.get_or_create(name=obj.currency.title + "_" + obj.currency_provider.title + "_forpayment")
    context_obj.value = obj.address
    context_obj.save()
    return json_true(req)


@login_required(login_url="/oper/login/")
def analytics(req):
    pass


def process_item_invoice(i):
    username = None
    if i.operator is not None:
        username = i.operator.username

    return {
            "id": i.id,
            "pk": i.id,
            "operator": username,
            "pub_date": i.pub_date,
            "expire_date": i.expire_date,
            "amnt": i.sum,
            "status": i.status,
            "currency": i.currency.title,
            "address": i.crypto_payments_details.address,
            "ext_info": i.crypto_payments_details.ext_info,
            "actions": render_to_string("oper/invoice_menu.html", context={"item": i})

    }


@login_required(login_url="/oper/login/")
def invoices_api(req, ):
    res = []
    for i in Invoice.objects.all().order_by("id"):
        res.append(process_item_invoice(i))

    return json_true(req, {"data": res})


# TODO add time_extending to invoice


@csrf_exempt
@login_required(login_url="/oper/login/")
def invoices_status(req, status, invoice_id):
    obj = get_object_or_404(Invoice, pk=invoice_id)

    if obj.currency.title in FIAT_CURRENCIES:
        if status in ("payed", "canceled") and obj.status in ("created",  ):
            obj.status = status
            obj.crypto_payments_details.status = "canceled"
            obj.crypto_payments_details.save()
            obj.save()
            tell_controller_invoice_check("oper_api_invoice_status", obj)
            return json_true(req)
        return json_500false(req, {"description": "Это действие уже невозможно"})

    if obj.currency.title in CRYPTO_CURRENCY:
        if status in ("payed", "canceled") and obj.status in ("wait_secure",):
            obj.status = status
            obj.save()

            tell_controller_invoice_check("oper_api_invoice_status", obj)
            return json_true(req)

        return json_500false(req, {"description": "Это действие уже невозможно"})


@csrf_exempt
@login_required(login_url="/oper/login/")
def get2work(req, order_id):
    obj = get_object_or_404(Orders, pk=order_id)
    if obj.operator is not None:
        return json_500false(req, {"description":
                                       "Это действие уже невозможно сделка в работу  у %s" % obj.operator.username})

    obj.operator = req.user
    obj.save()
    return json_true(req)


@csrf_exempt
@login_required(login_url="/oper/login/")
def wallets_sweep(req, wallet):
        obj = get_object_or_404(PoolAccounts, pk=wallet)
        factory = CryptoFactory(obj.currency.title,
                                obj.currency_provider.title)

        balance2send = factory.get_balance(obj.address)

        resp = get_full_data(obj.address)
        context_var = context_vars.objects.get(name=factory.currency + "_" + factory.network + "_forpayment")

        try:
            txid = factory.sweep_address_to(resp["key"], resp["address"], context_var.value, balance2send)
        except:
            return json_500false(req)

        balance2send = factory.get_balance(obj.address)
        obj.technical_info = balance2send
        obj.save()
        # TODO
        return json_true(req, {"txid": txid})


@csrf_exempt
@login_required(login_url="/oper/login/")
def wallets_update(req, wallet):
    obj = get_object_or_404(PoolAccounts, pk=wallet)
    factory = CryptoFactory(obj.currency.title,
                            obj.currency_provider.title)
    obj.technical_info = factory.get_balance(obj.address)

    if obj.currency_provider.title != "native":
        obj.ext_info = factory.native_balance(obj.address)

    obj.save()
    return json_true(req)


@csrf_exempt
@login_required(login_url="/oper/login/")
def wallets_info(req, wallet):
    # get the all info of wallet
    return json_true(req)


@csrf_exempt
@login_required(login_url="/oper/login/")
def wallets_status(req, status, wallet):
    obj = get_object_or_404(PoolAccounts, pk=wallet)
    obj.status = status
    obj.save()
    return json_true(req)


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
    try:
        d = chat.objects.get(deal=i)
        if d.telegram_id is None:
            connected = False
        connected = True
    except:
        traceback.print_exc()
        connected = False

    username = ""

    if i.operator is not None:
        username = i.operator.username

    invoice = Invoice.objects.get(order=i)

    return {"id": i.id,
            "pk": i.id,
            "buy": str(i.amnt_give) + " " + i.give_currency.title,
            "sell": str(i.amnt_take) + " " + i.take_currency.title,
            "pub_date": date_to_str(i.pub_date),
            "operator": username,
            "client_info": "Ukraine",
            # TODO add invoice of payment
            "invoice_id": invoice.id,
            "client_payed": invoice.status,
            "client_get": i.trans.status if i.trans else None,
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
def whole_oper_info(req, order_id):
    i = get_object_or_404(Orders, pk=order_id)
    connected = True
    d = None
    try:
        d = chat.objects.get(deal=i)
        if d.telegram_id is None:
            connected = False
        connected = True
    except:
        traceback.print_exc()
        connected = False

    username = ""

    if i.operator is not None:
        username = i.operator.username

    invoice = Invoice.objects.get(order=i)
    return json_true(req, {"order":
                               {"id": i.id,
                                "pk": i.id,
                                "buy": str(i.amnt_give) + " " + i.give_currency.title,
                                "sell": str(i.amnt_take) + " " + i.take_currency.title,
                                "pub_date": date_to_str(i.pub_date),
                                "operator": username,
                                "client_info": "Ukraine",
                                # TODO add invoice of payment
                                "client_payed": invoice.status,
                                "invoice_address": invoice.crypto_payments_details.address,
                                "trans_info": i.trans.account + " " + i.trans.payment_id if i.trans else None,
                                "client_get": i.trans.status if i.trans else None,
                                "client_telegram_connected": connected,
                                "status": i.status,
                                "rate": i.rate,
                                }
                           })


@login_required(login_url="/oper/login")
def show_payment(req, order_id):
    obj = get_object_or_404(Orders, pk=order_id)
    return json_true(req, {"trans": json.loads(serializers.serialize("json", [obj.trans]))})


@login_required(login_url="/oper/login/")
def oper_orders(request):

    res = []
    for i in Orders.objects.all().order_by("-id"):
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
                           "title": "Exchange Operator Cabinet",
                           "js_version": "5"},
                  content_type=None,
                  status=None,
                  using=None)


@login_required(login_url="/oper/login/")
def howto_page(request):
    return render(request, "oper/howto.html",
                  context={},
                  content_type=None,
                  status=None,
                  using=None)


# TODO add IPs permissions
def login_page(request):
    return render(request, "oper/authentication-login.html",
                  context=None, content_type=None, status=None, using=None)


@login_required
def test_rate(req):
    d = {}
    code4execute = req.body.decode('utf-8')
    for i in context_vars.objects.filter(name__startswith="context_"):
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


@login_required
def telegram_subscribe(req):
    link, created = OperTele.objects.get_or_create(user_id=req.user.id)
    if created:
        nw = datetime.now()
        k = str(convert2time(nw))
        link.tele_link = OPERTELEBOT + "subsribe_" + str(convert2time(nw))
        link.token = k

        link.save()

    return json_true(req, {"link": link.tele_link})


@csrf_exempt
def telegram_subscribe_callback(req, token):
    body_unicode = req.body.decode('utf-8')
    body = json.loads(body_unicode)
    obj = get_object_or_404(OperTele, token=token)
    tid = body["telegram_id"]
    username = body["username"]
    if obj.tele_id is not None:
        return json_500false(req)
    obj.tele_id = tid
    obj.tele_username = username
    obj.status = "processing"
    obj.save()
    return json_true(req, {"description": u"Хорошо мы вас подписали"})


def logout_view(request):
    logout(request)
    return redirect(reverse(login_page))


#TODO
def reset_pwd_request(req):
    pass


