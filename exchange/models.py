from django.db import models
import fintex.settings as settings
from datetime import datetime

import requests
from sdk.btc import get_current_height
import json


# imports for whitebit api calls
import base64
import hashlib
import hmac
import json
import time
from private_settings import WHITEBIT_API_KEY, WHITEBIT_SECRET_KEY


STATUS_INVOICE = (
    ("created", u"выставлен"),
    ("paid", u"оплачен"),
    ("processing", "в процессе"),
    ("wait_secure", "проверяется"),
    ("canceled", u"отменен"),
    ("expired", u"просрочен"),
)
DEBIT_CREDIT = (
    ("in", u"debit"),
    ("out", u"credit"),
)
CHECKOUT_STATUS_FREE = "wait_checkout"
CHECKOUT_STATUS_PROCESSING = "processing"

STATUS_ORDER = (
    ("wait_checkout", u"ожидает"),
    ("created", u"создана"),
    ("processing", u"в процессе"),
    ("processing2", u"в процессе отправки"),

    ("wait_secure", u"проверяется"),
    ("user_canceled", u"отменена клиентом"),
    ("canceled", u"отменена оператором"),
    ("processed", u"проведена"),
    ("failed", u"неуспешна"),
)

STATUS_WHITEBIT_EXCHANGE = (
    ("processing", u"в процессе"),
    ("processed", u"проведена"),
    ("failed", u"неуспешна"),
)


class OperTele(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name="Клиент",
                             related_name="user_tele_suggester",
                             editable=False, on_delete=models.PROTECT,
                             null=True,
                             blank=True,)

    tele_link = models.CharField(null=True, verbose_name="telegram temp link", max_length=255)

    token = models.CharField(null=True, verbose_name="telegram k", max_length=255)

    tele_id = models.IntegerField(null=True, blank=True, verbose_name="telegram id")

    tele_username = models.CharField(max_length=40, default='', verbose_name="")

    status = models.CharField(max_length=40, choices=STATUS_ORDER, default='created', verbose_name="Статус")


# Create your models here.
class Orders(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name="Клиент",
                             related_name="user_p2p_suggester",
                             editable=False, on_delete=models.PROTECT,
                             null=True,
                             blank=True,)
    status = models.CharField(max_length=40, choices=STATUS_ORDER, default='created', verbose_name="Статус")
    give_currency = models.ForeignKey("Currency", verbose_name="Give Currency",
                                      on_delete=models.PROTECT,
                                      related_name="give_currency", )
    provider_give = models.ForeignKey("CurrencyProvider", verbose_name="Provider Give Currency",
                                      related_name="povider_give", on_delete=models.PROTECT,)
    take_currency = models.ForeignKey("Currency",
                                      related_name="take_currency",
                                      verbose_name="Take currency", on_delete=models.PROTECT,)
    provider_take = models.ForeignKey("CurrencyProvider",
                                      related_name="provider_take",
                                      verbose_name="Provider take Currency",
                                                   on_delete=models.PROTECT,)

    pub_date = models.DateTimeField(default=datetime.now, verbose_name="Дата публикации")
    expire_date = models.DateTimeField(auto_now=False, verbose_name="Дата валидности",
                                       editable=True, null=True, blank=True)
    amnt_give = models.DecimalField(decimal_places=20, max_digits=40, verbose_name="amnt give",
                                    max_length=255, editable=True)
    amnt_take = models.DecimalField(decimal_places=10, max_digits=40, verbose_name="amnt take",
                                    max_length=255, editable=True)
    operator = models.ForeignKey(settings.AUTH_USER_MODEL,
                                 verbose_name="Оператор",
                                 related_name="user_open",
                                 editable=False, on_delete=models.PROTECT,
                                 null=True,
                                 blank=True)

    rate = models.DecimalField(decimal_places=10, max_digits=40, verbose_name="exchange rate",
                               max_length=255, editable=True)

    trans = models.ForeignKey("Trans", null=True, blank=True,verbose_name="транзакция выплаты",
                              on_delete=models.PROTECT, )

    class Meta:
        verbose_name = 'заявка на обмен'
        verbose_name_plural = 'заявки на обмен'

    def to_nice_text(o):
        invoice = Invoice.objects.get(order=o)
        return str(o.pub_date) + "\n" +\
               "\nПокупка: " + str(o.amnt_give) + " " + o.give_currency.title +\
               "\nПродажа:" + str(o.amnt_take) + " " + o.take_currency.title +\
               "\nОплата: "  + invoice.crypto_payments_details.address + " " + str(invoice.sum)


    def __unicode__(o):
        return str(o.id) + " " + str(o.pub_date) + " " + o.give_currency.title + " " + o.take_currency.title

    def __str__(self):
        return str(self.id)


# rates
class rate(models.Model):
    source = models.CharField(max_length=255, verbose_name="source of rate")
    give_currency = models.ForeignKey("Currency", verbose_name="Give Currency", related_name="currency_provided1",
                                      on_delete=models.PROTECT,)
    take_currency = models.ForeignKey("Currency", verbose_name="Take currency", related_name="currency_provided2",
                                      on_delete=models.PROTECT,)
    # DEFAULT its 1 = means system
    edit_user = models.ForeignKey(settings.AUTH_USER_MODEL,
                                  verbose_name="Опертор",
                                  related_name="user_provided_rate",
                                  editable=False, on_delete=models.PROTECT,
                                  null=True,
                                  blank=True)

    pub_date = models.DateTimeField(default=datetime.now, verbose_name="date of gathering")
    raw_data = models.TextField(blank=True, default="{}", editable=True)
    rate = models.DecimalField(decimal_places=20, max_digits=40, verbose_name="rate", max_length=255, editable=True)


# for cryptocurrency is native or in another networks for example binance
# for fiat bank transfer, cash or card
class CurrencyProvider(models.Model):
    title = models.CharField(max_length=255, verbose_name="Network Name")

    class Meta:
        verbose_name = u'Сеть проведения'
        verbose_name_plural = u'Сети проведения'

    def __unicode__(o):
        return o.title
    
    def __str__(self):
        return self.title


class Currency(models.Model):
    title = models.CharField(max_length=255, verbose_name="Currency Name")

    class Meta:
        verbose_name = u'валюта'
        verbose_name_plural = u'валюты'

    def __unicode__(o):
        return str(o.id) + " " + str(o.title)
    
    def __str__(self):
        return self.title
    

class CashPointLocation(models.Model):
    title = models.CharField(max_length=255, verbose_name="Сash point location")

    class Meta:
        verbose_name = u'Локация выдачи наличных'
        verbose_name_plural = u'Локации выдачи наличных'

    def __unicode__(o):
        return str(o.id) + " " + str(o.title)
    
    def __str__(self):
        return self.title


class Invoice(models.Model):
    currency = models.ForeignKey("Currency", 
                                 verbose_name="Invoice Currency",
                                 on_delete=models.PROTECT,
                                 related_name="invoice_currency", )
    status = models.CharField(max_length=40, 
                              choices=STATUS_ORDER, 
                              default='created', 
                              verbose_name="Статус")

    order = models.OneToOneField("Orders", 
                                 verbose_name="Order ID",
                                 on_delete=models.PROTECT,
                                 related_name="invoice_order")

    crypto_payments_details = models.ForeignKey("PoolAccounts",
                                 verbose_name="Crypto Address",
                                 on_delete=models.PROTECT,
                                 related_name="crypto_payments_details",
                                 null=True,
                                 blank=True)

    sum = models.DecimalField(decimal_places=20, 
                              max_digits=40, 
                              verbose_name="Сумма инвойса",
                              max_length=255, 
                              editable=True,
                              default=0)

    block_height = models.IntegerField(verbose_name="Высота блока",
                                       default=0)

    operator = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name="Опертор",
                                 related_name="user_checked",
                                 editable=False,
                                 on_delete=models.PROTECT,
                                 null=True,
                                 blank=True)

    pub_date = models.DateTimeField(default=datetime.now, verbose_name="Дата публикации")

    expire_date = models.DateTimeField(auto_now=False, verbose_name="Дата валидности", editable=True, null=True,
                                       blank=True)

    class Meta:
        verbose_name = u'инвойс'
        verbose_name_plural = u'инвойсы'

    def __unicode__(o):
        return str(o.id)
    
    def __str__(self):
        return str(self.id)


class PoolAccounts(models.Model):
    status = models.CharField(max_length=40,
                              choices=STATUS_ORDER,
                              default=CHECKOUT_STATUS_FREE)

    user = models.ForeignKey(settings.AUTH_USER_MODEL, 
                             blank=True, null=True, 
                             on_delete=models.PROTECT)

    currency = models.ForeignKey("Currency", 
                                 verbose_name="Валюта", 
                                 on_delete=models.PROTECT)

    pub_date = models.DateTimeField(default=datetime.now, 
                                    verbose_name="Дата публикации")

    ext_info = models.CharField(max_length=255,
                                blank=True,
                                null=True,
                               verbose_name="доп информации по нативной валюте, если это токен usdt")

    address = models.CharField(max_length=255,
                               unique=True,
                               verbose_name="Внешний ключ идентификации или кошелек криптовалюты")

    technical_info = models.CharField(max_length=255,
                                      default="",
                                      verbose_name="Техническая информация для обработки платежей, balance tokena")
    
    currency_provider = models.ForeignKey("CurrencyProvider", 
                                          verbose_name="Сеть", 
                                          blank=True,

                                          null=True, 
                                          on_delete=models.PROTECT)

    class Meta:
        verbose_name = u'Пул криптоадресов'
        verbose_name_plural = u'Пулы криптоадресов'
    
    def __str__(self):
        return self.address


class FiatAccounts(models.Model):
    card_number = models.CharField(max_length=32,
                                   unique=True,
                                   verbose_name="Номер карты")

    class Meta:
        verbose_name = u'Фиат реквизиты'
        verbose_name_plural = u'Фиат реквизиты'

    def __str__(self):
        return self.card_number


class CheckAml(models.Model):
    trans = models.ForeignKey("exchange.Trans",
                              verbose_name="транса на проверку",
                              on_delete=models.PROTECT,
                              related_name="currency_of_trans_check", )
    status = models.CharField(max_length=40, choices=STATUS_ORDER, default='created', verbose_name="Статус")
    aml_check = models.TextField(default={})
    pub_date = models.DateTimeField(default=datetime.now,
                                    verbose_name="Дата публикации")


class Trans(models.Model):
    account = models.CharField(verbose_name="account ",
                               max_length=255,
                               editable=True,
                               null=True,
                               blank=True)
    payment_id = models.CharField(verbose_name="payment id",
                                  max_length=255,
                                  editable=True,
                                  null=False,
                                  blank=False)

    status = models.CharField(max_length=40, choices=STATUS_ORDER, default='created', verbose_name="Статус")

    currency = models.ForeignKey("exchange.Currency",
                                 verbose_name="Currency",
                                 on_delete=models.PROTECT,
                                 related_name="currency_of_trans", )

    pub_date = models.DateTimeField(default=datetime.now,
                                    verbose_name="Дата публикации")

    processed_date = models.DateTimeField(auto_now=False,
                                          verbose_name="Дата валидности",
                                          editable=True,
                                          null=True,
                                          blank=True)
    
    debet_credit = models.CharField(max_length=255,
                                    choices=DEBIT_CREDIT,
                                    verbose_name="дебет/кредит",
                                    null=True,
                                    blank=True)

    amnt = models.DecimalField(decimal_places=20,
                               max_digits=40,
                               verbose_name="amnt give",
                               max_length=255, editable=True)

    operator = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name="Опертор",
                                related_name="user_issued",
                                editable=False, on_delete=models.PROTECT,
                                null=True,
                                blank=True)
    
    order = models.ForeignKey("Orders", 
                              verbose_name="Order",
                              on_delete=models.PROTECT,
                              related_name="trans_order",
                              null=True,
                              blank=True)

    txid = models.CharField(verbose_name="crypto txid", null=True, blank=True, max_length=255)

    currency_provider = models.ForeignKey("CurrencyProvider", 
                                          verbose_name="Сеть", 
                                          blank=True,
                                          null=True, 
                                          on_delete=models.PROTECT)

    tx_raw = models.TextField(default={})

    aml_check = models.TextField(default={})

    class Meta:
        verbose_name = 'Транзакция'
        verbose_name_plural = 'Транзакции'

    def __str__(self):
        return str(self.id)

    def unicode(o):
        return str(o.id) + " " + str(o.pub_date) + " " + o.currency + " " + o.amnt
    

class WhitebitDeals(models.Model):
    currency_give = models.CharField(max_length=255, verbose_name="Give Currency")
    currency_take = models.CharField(max_length=255, verbose_name="Take Currency")
    amnt_give = models.DecimalField(decimal_places=10, max_digits=40, verbose_name="Сумма продана",
                                   max_length=255, editable=True, blank=True, null=True)
    amnt_take = models.DecimalField(decimal_places=10, max_digits=40, verbose_name="Сумма получена",
                                   max_length=255, editable=True, blank=True, null=True)
    fee = models.DecimalField(decimal_places=10, max_digits=40, verbose_name="Комиссия биржи",
                                   max_length=255, editable=True, blank=True, null=True)
    price = models.DecimalField(decimal_places=10, max_digits=20, verbose_name="Цена продажи",
                                     max_length=255, editable=True, blank=True, null=True)
    timestamp = models.CharField(max_length=40, blank=True, null=True, verbose_name="Время выполнения сделки")
    client_order_id = models.CharField(max_length=255, 
                                       verbose_name="whitebit ID сделки", 
                                       blank=True, 
                                       null=True)
    order = models.ForeignKey("Orders", 
                              verbose_name="Order",
                              on_delete=models.PROTECT,
                              related_name="order",
                              null=True,
                              blank=True)
    trans = models.ForeignKey("Trans", 
                              verbose_name="Trans",
                              on_delete=models.PROTECT,
                              related_name="Trans",
                              null=True,
                              blank=True)
    status = models.CharField(max_length=40, choices=STATUS_WHITEBIT_EXCHANGE, default='processing',
                              verbose_name="Статус", blank=True, null=True)

    class Meta:
        verbose_name = u'Whitebit операция'
        verbose_name_plural = u'Whitebit операции'
    
    def __str__(self):
        return str(self.id)


