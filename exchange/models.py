from django.db import models
import fintex.settings as settings
from datetime import datetime

from django.db.models.signals import post_save
from django.dispatch import receiver

STATUS_INVOICE = (
    ("created", u"выставлен"),
    ("paid", u"оплачен"),
    ("canceled", u"отменен"),
);

STATUS_ORDER = (
    ("created", u"создана"),
    ("processing", u"в процессе"),
    ("wait_secure", u"проверяется"),
    ("user_canceled", u"отменена клиентом"),
    ("canceled", u"отменена оператором"),
    ("processed", u"проведена"),
    ("failed", u"неуспешна"),
);

# tuple for example purposes. it will be deleted
CRYPTO_WALLETS = (
    ("1231290o3dqwjlsanq0n", u"btc_wallet"),
    ("mgklf9304jhmvlfg8jmrtm", u"eth_wallet"),
);


# Create your models here.
class Orders(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name="Клиент",
                             related_name="user_p2p_suggester",
                             editable=False, on_delete=models.PROTECT,
                             null=True,
                             blank=True)
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

    rate = models.DecimalField(decimal_places=10, max_digits=40, verbose_name="exchange rate", max_length=255, editable=True)

    class Meta:
        verbose_name = 'заявка на обмен'
        verbose_name_plural = 'заявки на обмен'

    def __unicode__(o):
        return str(o.id) + " " + str(o.pub_date) + " " + o.give_currency.title + " " + o.take_currency.title

    def __str__(self):
        return str(self.id)
    

#rates
class rate(models.Model):
    source = models.CharField(max_length=255, verbose_name="source of rate")
    give_currency = models.ForeignKey("Currency", verbose_name="Give Currency", related_name="currency_provided1",
                                      on_delete=models.PROTECT,)
    take_currency = models.ForeignKey("Currency", verbose_name="Take currency", related_name="currency_provided2",
                                      on_delete=models.PROTECT,)
    #DEFAULT its 1 = means system
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
    currency = models.ForeignKey("Currency", verbose_name="Invoice Currency",
                                      on_delete=models.PROTECT,
                                      related_name="invoice_currency", )
    status = models.CharField(max_length=40, 
                              choices=STATUS_INVOICE, 
                              default='created', 
                              verbose_name="Статус")
    order = models.OneToOneField("Orders", verbose_name="Order ID",
                                    on_delete=models.PROTECT,
                                    related_name="invoice_order", )
    wallet = models.CharField(max_length=300, 
                              choices=CRYPTO_WALLETS, 
                              default='1231290o3dqwjlsanq0n',
                              verbose_name="номер кошелька")

    class Meta:
        verbose_name = u'инвойс'
        verbose_name_plural = u'инвойсы'

    def __unicode__(o):
        return str(o.id)
    
    def __str__(self):
        return str(self.id)
    

@receiver(post_save, sender=Orders)
def create_invoice(sender, instance, created, **kwargs):
    if created:
        new_invoice = Invoice(order=instance, currency_id=3)
        new_invoice.save()
