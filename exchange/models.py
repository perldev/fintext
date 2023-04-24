from django.db import models
import fintex.settings as settings
from datetime import datetime

from django.db.models.signals import post_save
from django.dispatch import receiver

from sdk.btc import get_current_height

STATUS_INVOICE = (
    ("created", u"выставлен"),
    ("paid", u"оплачен"),
    ("canceled", u"отменен"),
    ("expired", u"просрочен"),

);

CHECKOUT_STATUS_FREE = "wait_checkout"
CHECKOUT_STATUS_PROCESSING = "processing"

STATUS_ORDER = (
    ("created", u"создана"),
    ("processing", u"в процессе"),
    ("wait_secure", u"проверяется"),
    ("user_canceled", u"отменена клиентом"),
    ("canceled", u"отменена оператором"),
    ("processed", u"проведена"),
    ("failed", u"неуспешна"),
);


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
    expire_date = models.DateTimeField(auto_now=False, verbose_name="Дата валидности", editable=True, null=True, blank=True)
    amnt_give = models.DecimalField(decimal_places=20, max_digits=40, verbose_name="amnt give", max_length=255, editable=True)
    amnt_take = models.DecimalField(decimal_places=10, max_digits=40, verbose_name="amnt take", max_length=255, editable=True)
    operator = models.ForeignKey(settings.AUTH_USER_MODEL,
                                 verbose_name="Оператор",
                                 related_name="user_open",
                                 editable=False, on_delete=models.PROTECT,
                                 null=True,
                                 blank=True)

    trans = models.ForeignKey("Trans",
                              verbose_name="транзакция выплаты",
                              related_name="user_open",
                              editable=False, on_delete=models.PROTECT,
                              null=True,
                              blank=True
                              )

    rate = models.DecimalField(decimal_places=10, max_digits=40, verbose_name="exchange rate", max_length=255, editable=True)


    class Meta:
        verbose_name = 'заявка на обмен'
        verbose_name_plural = 'заявки на обмен'

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
    edit_user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name="Опертор",
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


class Invoice(models.Model):
    currency = models.ForeignKey("Currency", 
                                 verbose_name="Invoice Currency",
                                 on_delete=models.PROTECT,
                                 related_name="invoice_currency", )
    status = models.CharField(max_length=40, 
                              choices=STATUS_INVOICE, 
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
                              default='created')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, 
                             blank=True, null=True, 
                             on_delete=models.PROTECT)
    currency = models.ForeignKey("Currency", 
                                 verbose_name="Валюта", 
                                 on_delete=models.PROTECT)
    pub_date = models.DateTimeField(default=datetime.now, 
                                    verbose_name="Дата публикации")
    ext_info = models.CharField(max_length=255,
                               unique=True,
                               verbose_name="Внешний ключ идентификации")
    address = models.CharField(max_length=255,
                               unique=True,
                               verbose_name="Внешний ключ идентификации или кошелек криптовалюты")
    
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
    

class Trans(models.Model):
    account = models.CharField(verbose_name="account ",
                               max_length=255,
                               editable=False,
                               null=False,
                               blank=False)
    payment_id = models.CharField(verbose_name="payment id",
                                  max_length=255,
                                  editable=False,
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

    amnt = models.DecimalField(decimal_places=20,
                               max_digits=40,
                               verbose_name="amnt give",
                               max_length=255, editable=True)

    operator = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name="Опертор",
                                related_name="user_issued",
                                editable=False, on_delete=models.PROTECT,
                                null=True,
                                blank=True)

    txid = models.CharField(verbose_name="crypto txid", null=True, blank=True, max_length=255)

    class Meta:
        verbose_name = 'Транзакция'
        verbose_name_plural = 'Транзакции'

    def unicode(o):
        return str(o.id) + " " + str(o.pub_date) + " " + o.currency + " " + o.amnt