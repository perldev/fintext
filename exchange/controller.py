
from django.db.models.signals import post_save
from django.dispatch import receiver
from exchange.models import Invoice, CheckAml, Trans
from exchange.models import Orders, OperTele
from fintex import settings
from fintex.settings import NATIVE_CRYPTO_CURRENCY, CRYPTO_CURRENCY
import requests
from fintex.common import no_fail
import traceback

from exchange.models import CHECKOUT_STATUS_FREE
# module that works like a gathering all logic for provide deals
# SIGNALS HERE


def get_deal_status(order):

    obj = Orders.objects.get(id=order)
    last_status = obj.status
    payment2client_status = obj.trans.status
    if payment2client_status == "created":
        payment2client_status = "wait"

    invoice = None

    try:
        invoice = Invoice.objects.get(order=obj)
    except:
        error_var = traceback.format_exc()
        raise Exception(error_var)

    invoice_status = invoice.status

    invoice_check_status = "wait"
    if invoice_status == "created":
        invoice_status = "wait"

    if invoice_status == "processing":
        invoice_check_status = "processing"
        invoice_status = "processed"

    if invoice_status == "wait_secure":
        invoice_check_status = "aml_failed"
        invoice_status = "processed"

    if invoice_status == "payed":
        invoice_check_status = "processed"
        invoice_status = "processed"

    changing_status = "wait"
    if invoice_status == "processed" and invoice_check_status == "processed" and payment2client_status == "wait":
        changing_status = "processing"

    if invoice_status == "processed" and invoice_check_status == "processed" and payment2client_status != "wait":
        changing_status = "processed"

    return {"invoice_wait": invoice_status,
            "invoice_check": invoice_check_status,
            "changing": changing_status,
            "payment2client": changing_status,
            "last_status": last_status}


def common_tell(sender, instance, **kwargs):
    pass


@no_fail
def tell_invoice_check(sender, instance, **kwargs):
    print("tell invoice check ")
    print(sender)
    print(instance)
    print(kwargs)

    # if invoice is payed we check weather we change it on whitebit
    order = instance.order
    # in any case free the pool account if forgot about this in logic
    instance.crypto_payments_details.status = CHECKOUT_STATUS_FREE
    instance.crypto_payments_details.save()

    if instance.status == "processing":
        notify_dispetcher(order, "invoice_checking")
        return True

    if instance.status == "wait_secure":
        notify_dispetcher(order, "invoice_wait_secure")
        return True

    if instance.status == "payed":
        if order.give_currency.title in NATIVE_CRYPTO_CURRENCY:
            notify_dispetcher(order, "invoice_payed")
            pass
            # here will be command of andrey
        else:
            notify_dispetcher(order, "invoice_payed")
            # changing trans to client in processing for further working
            order.trans.status = "processing"
            order.trans.save()
        return True

    if instance.status in ("canceled", "expired"):
        instance.order.status = "canceled"
        instance.order.trans.status = "canceled"
        instance.order.trans.save()
        instance.order.save()
        notify_dispetcher(order, "invoice_unpayed")

    return True


@no_fail
def tell_aml_check(sender, instance, **kwargs):

    if instance.status == "processed":
        return notify_dispetcher(instance.trans.order, "aml_checked")

    if instance.status == "failed":
        return notify_dispetcher(instance.trans.order, "aml_error_request")


@no_fail
def tell_trans_check(sender, instance, **kwargs):

    if sender == "send_crypto_transes_deal":
        # auto make order processed
        if instance.status == "processed":
            order = Orders.objects.get(trans=instance)
            order.status == "processed"
            order.save()
            return tell_update_order("exchange_controller", order)

    if sender == "order_api_status_function":
        # auto make order processed
        if instance.debit_credit == "out" and instance.status == "processed":
            order = Orders.objects.get(trans=instance)
            order.status = "processed"
            order.save()
            return tell_update_order("exchange_controller", order)

    if instance.status == "failed":
        return notify_dispetcher(instance.order,
                                 "trans_out_failed",
                                 error=sender + " \n" + kwargs["error"],
                                 )

    if instance.debit_credit == "in":
        if instance.status == "wait_secure":
            # invoice should be put to wait_secure
            instance.order.invoice.status = "wait_secure"
            instance.order.invoice.save()
            return notify_dispetcher(instance.order, "trans_aml_failed")

        # here we are checking all incoming transes for invoice
        if instance.status == "processed" and instance.currency.title in CRYPTO_CURRENCY:
            # check all transes in for order
            for i in Trans.objects.filter(order=instance.order,
                                          debit_credit='in'):
                if not i.status == "processed":
                    print("wait another ones")
                    return True

            # all payed and checked
            invoice_of_order = Invoice.objects.get(order=instance.order)
            invoice_of_order.status = "payed"
            invoice_of_order.save()
            tell_invoice_check("exchange_controller", invoice_of_order)
            return True


# TODO move to background tasks
@no_fail
def notify_dispetcher(order, event, **kwargs):
    print("="*64)
    print("notify dispetcher")
    print(order)
    print(event)
    print(kwargs)
    # gather operators of subscribed
    oper_list = None
    if order.operator is not None:
        oper = OperTele.objects.get(user=order.operator)
        oper_list = [oper]
    else:
        oper_list = OperTele.objects.filter(status="processing")

    # create nice text of the deal
    txt = order.to_nice_text()
    error = kwargs.get("error", False)
    # if error existed finish here
    if error:
        msg = ""
        msg = msg + "\n Error during process operation %s" % event
        msg = msg + error + " \n\n" + txt
        return raw_send(oper_list, txt)



    events_keys = {
        "trans_aml_failed": "Транзакция по инвойсу не прошла aml проверку, провести в ручном режиме можно в кабинете",
        "invoice_checking": "Проверяем  входящии транзакции по сделке",
        "invoice_unpayed": "Транзакции по сделке не поступили к нам",
        "invoice_payed": "Входящий платеж получен и прошел проверку",
        "aml_checked": "Входящии платежи по сделке прошли проверку aml",
        "aml_failed": "Входящии платежи по сделке НЕ прошли проверку aml",
        "invoice_wait_secure": "Проверьте входящии платежи по сделке в кабинете оператора",
        "deal_processed": "Сделка завершена"
    }

    msg = None
    if event not in events_keys:
        msg = "Не расспознанное событие по сделке %s" % event
    else:
        msg = events_keys[event]

    txt = msg + " \n\n" + txt
    return raw_send(oper_list, txt)
    # if some operator took in work then list will contain only one element
    # in other case spam everybody


@no_fail
def tell_update_order(sender, instance, **kwargs):

    if instance.status == "processing":
        for oper in OperTele.objects.filter(status="processing"):
            tell_subscriber(oper, instance)

    if instance.status == "processed":
        notify_dispetcher(instance.order, "deal_processed")
        return True
        # notify dispetcher

    if instance.status == "canceled":
        # disable all operations
        Trans.objects.filter(order=instance,
                             status="created",
                             debit_credit='out').update(status="canceled")
        Invoice.objects.filter(order=instance).update(status="canceled")

        return True


def raw_send(oper_list, txt):
    for oper in oper_list:
        telegram_id = oper.tele_id
        resp = requests.post(settings.BOTAPI + "alert/%s" % str(telegram_id),
                             json={"text": txt})

        if resp.status_code != 200:
            print("something wrong during subsribing")

    return True


# TODO maybe rewritten in separate process
@no_fail
def tell_subscriber(oper, instance):

    telegram_id = oper.tele_id
    txt = u"Новая заявка: \n" + instance.to_nice_text()
    resp = requests.post(settings.BOTAPI+"alert/%s" % str(telegram_id),
                         json={"text": txt,
                               "actions": [{"text": u"подписаться",
                                            "url":
                                             settings.API_HOST + "getinwork/%i/%i" % (instance.id, oper.user_id)
                                            }]})
    if resp.status_code != 200:
        print("something wrong during subsribing")
