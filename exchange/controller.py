
from django.db.models.signals import post_save
from django.dispatch import receiver
from exchange.models import Invoice, CheckAml, Trans
from exchange.models import Orders, OperTele
from fintex import settings
from fintex.settings import NATIVE_CRYPTO_CURRENCY, CRYPTO_CURRENCY
import requests

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
                pass # here will be command of andrey
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
        notify_dispetcher(instance.trans.order, "aml_checked")

    if instance.status == "wait_secure":
        notify_dispetcher(instance.trans.order, "aml_failed")


@receiver(post_save, sender=Trans, dispatch_uid="controller_trans")
def trans_check(sender, instance, **kwargs):
    if kwargs.get("created", True):
        return True

    if instance.status == "wait_secure":
        notify_dispetcher(instance.order, "trans_aml_failed")

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
def notify_dispetcher(order, event):
    pass


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
