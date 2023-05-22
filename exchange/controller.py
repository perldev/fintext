
from django.db.models.signals import post_save
from django.dispatch import receiver
from exchange.models import Invoice, CheckAml, Trans
from exchange.models import Orders, OperTele
from fintex import settings
from fintex.settings import NATIVE_CRYPTO_CURRENCY, CRYPTO_CURRENCY
import requests
from fintex.common import no_fail

# module that works like a gathering all logic for provide deals
# SIGNALS HERE


@receiver(post_save,
          sender=Invoice,
          dispatch_uid="controller_invoice")
def invoice_check(sender, instance, **kwargs):
    if kwargs.get("created", True):
        print("do nothing")
        return True
    else:
        # if invoice is payed we check weather we change it on whitebit
        order = instance.order
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

        if instance.status in ("canceled", "expired"):
            instance.order.status = "canceled"
            instance.order.save()
            notify_dispetcher(order, "invoice_unpayed")

        return True


@receiver(post_save, sender=CheckAml, dispatch_uid="controller_aml")
def aml_check(sender, instance, **kwargs):
    if kwargs.get("created", True):
        return True

    if instance.status == "processed":
        return notify_dispetcher(instance.trans.order, "aml_checked")

    if instance.status == "wait_secure":
        return notify_dispetcher(instance.trans.order, "aml_failed")


@receiver(post_save, sender=Trans, dispatch_uid="controller_trans")
def trans_check(sender, instance, **kwargs):
    if kwargs.get("created", True):
        return True

    if instance.status == "wait_secure":
        return notify_dispetcher(instance.order, "trans_aml_failed")

    # here we are checking all incoming transes for invoice
    if instance.status == "processed" \
            and instance.debit_credit == 'in'\
            and instance.currency.title in CRYPTO_CURRENCY:
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
        return True


# TODO move to background tasks
@no_fail
def notify_dispetcher(order, event):
    txt = order.to_nice_text()
    events_keys = {
        "trans_aml_failed": "Транзакция по инвойсу не прошла aml проверку, провести в ручном режиме можно в кабинете",
        "invoice_checking": "Проверяем  входящии транзакции по сделке",
        "invoice_unpayed": "Транзакции по сделке не поступили к нам",
        "invoice_payed": "Входящий платеж получен и прошел проверку",
        "aml_checked": "Входящии платежи по сделке прошли проверку aml",
        "aml_failed": "Входящии платежи по сделке НЕ прошли проверку aml",
        "invoice_wait_secure": "Проверьте входящии платежи по сделке в кабинете оператора",

    }
    msg = None
    if event not in events_keys:
        msg = "Не расспознанное событие по сделке %s" % event
    else:
        msg = events_keys[event]

    txt = msg + " \n\n" + txt
    oper_list = None

    if order.operator is not None:
        oper = OperTele.objects.get(user=order.operator)
        oper_list = [oper]
    else:
        oper_list =OperTele.objects.filter(status="processing")

    # if some operator took in work then list will contain only one element
    # in other case spam everybody

    for oper in oper_list:
        telegram_id = oper.telegram_id
        resp = requests.post(settings.BOTAPI + "alert/%s" % str(telegram_id),
                             json={"text": txt})

        if resp.status_code != 200:
            print("something wrong during subsribing")

    return True


@receiver(post_save, sender=Orders, dispatch_uid="tell_subscribers")
def update_stock(sender, instance, **kwargs):
    if kwargs.get("created", False):
        for oper in OperTele.objects.filter(status="processing"):
            tell_subscriber(oper, instance)

    if instance.status == "canceled":
        # disable all operations
        Trans.objects.filter(order=instance, status="created").update(status="canceled")
        Invoice.objects.filter(order=instance).update(status="canceled")

        return True


# TODO maybe rewritten in separate process
def tell_subscriber(oper, instance):

    telegram_id = oper.telegram_id
    txt = u"Новая заявка: \n" + instance.to_nice_text()
    resp = requests.post(settings.BOTAPI+"alert/%s" % str(telegram_id),
                         json={"text": txt,
                                "actions": [{"text": u"подписаться",
                                              "url":
                                              settings.API_HOST + "getinwork/%i/%i" % (instance.id, oper.user_id )
                                            }]})
    if resp.status_code != 200:
        print("something wrong during subsribing")
