from django.db import models
from datetime import datetime
from fintex import settings
from exchange.models import Currency, STATUS_ORDER, Orders
import uuid

# TODO realize creating trans
class crypto_trans(models.Model):

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

    crypto_txid = models.CharField(verbose_name="crypto txid", null=True, blank=True, max_length=255)

    class Meta:
        verbose_name = 'крипто транзакция'
        verbose_name_plural = 'крипто транзакции'

    def __unicode__(o):
        return str(o.id) + " " + str(o.pub_date) + " " + o.currency + " " + o.amnt




class chat(models.Model):
    uuid = models.UUIDField(verbose_name="uuid of page for quick connect",
                            primary_key=True,
                            default=uuid.uuid4,
                            editable=False
                            )

    deal = models.ForeignKey("exchange.Orders",
                             verbose_name="заявка",
                             related_name="deal_issued",
                             editable=False,
                             on_delete=models.PROTECT,
                             null=True,
                             blank=True)

    telegram_id = models.CharField(max_length=255,
                                   null=True,
                                   blank=True)

    history = models.TextField(default="{}")


class context_vars(models.Model):
    name = models.CharField(verbose_name="Name", unique=True, max_length=255)
    value = models.CharField(verbose_name="Value", blank=False, max_length=255)

    class Meta:
        verbose_name = 'контекстная перменная'
        verbose_name_plural = 'контекстные переменные'


def get_telechat_link(chat):
    return settings.TELEBOT + chat.uuid

def get_rate(from_currency, to_currency):
    cur1 = Currency.objects.get(title=from_currency)
    cur2 = Currency.objects.get(title=to_currency)
    direction = rates_direction.objects.get(give_currency=cur1, take_currency=cur2)
    code4execute = direction.raw_data
    d = {}
    for i in context_vars.objects.all():
        d[i.name] = float(i.value)

    d = eval(code4execute, {'__builtins__': None}, d)
    return d


class rates_direction(models.Model):

        give_currency = models.ForeignKey("exchange.Currency", verbose_name="Give Currency",
                                          related_name="currency_give_wizzard",
                                          on_delete=models.PROTECT, )

        take_currency = models.ForeignKey("exchange.Currency", verbose_name="Take currency",
                                          related_name="currency_take_wizzard",
                                          on_delete=models.PROTECT, )

        raw_data = models.TextField(blank=True, default="0", editable=True)

        class Meta:
            verbose_name = 'направление обмена'
            verbose_name_plural = 'направления обменов'

