from django.db import models
from datetime import datetime
from fintex import settings
from exchange.models import Currency, STATUS_ORDER, Orders

import uuid
import json

STATUS = (
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
    @property
    def get_telechat_link(self):
        return get_telechat_link(self)


class context_vars(models.Model):
    name = models.CharField(verbose_name="Name", unique=True, max_length=255)
    value = models.CharField(verbose_name="Value", blank=False, max_length=255)

    class Meta:
        verbose_name = 'контекстная перменная'
        verbose_name_plural = 'контекстные переменные'


def get_telechat_link(chat):
    return settings.TELEBOT + str(chat.uuid)


def create_task(name, params, key, status="processing"):
    task = simple_task(command_name=name, command_params=json.dumps(params),
                       ext_key=key, status=status)
    task.save()
    return task


class simple_task(models.Model):

    command_name = models.CharField(verbose_name="Name", unique=True, max_length=255)
    command_params = models.TextField(verbose_name="params", unique=True, max_length=255)
    status = models.CharField(max_length=40, choices=STATUS, default='created', verbose_name="Статус")
    history = models.TextField(default="")
    ext_key = models.CharField(max_length=255, unique=True, blank=False)

    class Meta:
        verbose_name = 'Задача на исполнение'
        verbose_name_plural = 'Задачи на исполнение'


def get_rate(from_currency, to_currency):
    cur1 = Currency.objects.get(title=from_currency)
    cur2 = Currency.objects.get(title=to_currency)
    direction = rates_direction.objects.get(give_currency=cur1, take_currency=cur2)
    code4execute = direction.raw_data
    d = {}
    for i in context_vars.objects.filter(name__startswith="context"):
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

