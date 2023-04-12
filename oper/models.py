from django.db import models
from datetime import datetime
from fintex import settings
from exchange.models import Currency, STATUS_ORDER, Orders

# Create your models here.
class crypto_trans(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name="Клиент",
                             related_name="user_oper",
                             editable=False, on_delete=models.PROTECT,
                             null=True,
                             blank=True)
    status = models.CharField(max_length=40, choices=STATUS_ORDER, default='created', verbose_name="Статус")

    currency = models.ForeignKey("exchange.Currency", verbose_name="Currency",
                                      on_delete=models.PROTECT,
                                      related_name="currency_of_trans", )

    pub_date = models.DateTimeField(default=datetime.now, verbose_name="Дата публикации")

    processed_date = models.DateTimeField(auto_now=False, verbose_name="Дата валидности", editable=True, null=True,
                                          blank=True)

    amnt = models.DecimalField(decimal_places=20, max_digits=40, verbose_name="amnt give",
                               max_length=255, editable=True)

    operator = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name="Опертор",
                                related_name="user_issued",
                                editable=False, on_delete=models.PROTECT,
                                null=True,
                                blank=True)

    crypto_txid = models.CharField(verbose_name="crypto txid", null=True, blank=True, max_length=255)

    class Meta:
        verbose_name = 'крипто транзакция'
        verbose_name_plural = 'крипто транзакции'

    def __unicode__(o):
        return str(o.id) + " " + str(o.pub_date) + " " + o.currency + " " + o.amnt


class chat(models.Model):
    deal = models.ForeignKey("exchange.Orders",
                             verbose_name="заявка",
                             related_name="user_issued",
                             editable=False,
                             on_delete=models.PROTECT,
                             null=True,
                             blank=True)

    history = models.TextField(default="{}")