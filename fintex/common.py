import simplejson as json

from django.shortcuts import render
from django.http import HttpResponse

import decimal
import datetime
import traceback
from django.core.cache import cache
from oper.models import get_telechat_link as oper_get_telechat_link, chat
import time
import fintex.settings
from decimal import Decimal

from uuid import UUID

def format_numbers10(D):

    if isinstance(D, str) or isinstance(D, float):
        D = Decimal(D)

    decimal_10 = 10**10
    D = int(Decimal(D) * decimal_10)/decimal_10
    return str(D)

def format_numbers4(D):

    if isinstance(D, str) or isinstance(D, float):
        D = Decimal(D)

    decimal_10 = 10**4
    D = int(Decimal(D) * decimal_10)/decimal_10
    return str(D)

def format_numbers_universal(D, decimals=8):

    if isinstance(D, str) or isinstance(D, float):
        D = Decimal(D)

    decimal_10 = 10**decimals
    D = int(Decimal(D) * decimal_10)/decimal_10
    return str(D)


def get_fromcache(k):
    return cache.get(k)


def put2cache(k, q, t=300):
    cache.set(k, q, t)


def to_time(t):
    return t.strftime("%H:%M:%S")


def to_date(t):
    return t.strftime("%d/%m/%Y")


def date_to_str(t):
    return t.strftime("%d/%m/%Y, %H:%M:%S")


def get_telechat_link(obj):
    c = chat.objects.get(deal=obj)
    return oper_get_telechat_link(c)


def json_true(req, dictt=None):
    d = {"status": True}
    resp = None
    if not dictt is None:
        resp = {**d, **dictt}
    else:
        resp = d
    resp = json_dumps(resp)
    if req.GET.get("html", ""):
        return render(req, "json.html", {"data": resp})

    return HttpResponse(resp, headers={"Content-Type": "application/json"})


def no_fail(function):
    def wrapper(*args, **kargs):
        if fintex.settings.DEBUG:
            try:
                return function(*args, **kargs)
            except:
                traceback.print_exc()
                return False
        else:
            return function(*args, **kargs)

    return wrapper

def convert2time(date):
    return int(time.mktime(date.timetuple()))


def json_500false(req, dicct):
    d = {"status": False}
    resp = None
    if not dicct is None:
        resp = {**d, **dicct}
    else:
        resp = d

    resp = json_dumps(resp)
    if req.GET.get("html", ""):
        return render(req, "json.html", {"data": resp})

    return HttpResponse(resp, status=500, headers={"Content-Type": "application/json"})


class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        print(o)
        if isinstance(o, decimal.Decimal):
            # wanted a simple yield str(o) in the next line,
            # but that would mean a yield on the line with super(...),
            # which wouldn't work (see my comment below), so...
            return (str(o) for o in [o])

        if isinstance(o, datetime.datetime):
            return (str(o) for o in [o])

        if isinstance(o, datetime.date):
            return (str(o) for o in [o])

        return super(DecimalEncoder, self).default(o)


def jsonencoder(o):
    if isinstance(o, datetime.datetime):
        return str(o)

    if isinstance(o, datetime.date):
        return str(o)

    if isinstance(o, UUID):
        return str(o)

    return json.JSONEncoder().default(o)



def json_dumps(diccc=None):
    if diccc is None:
        return "{}"  # ))
    # return json.dumps(diccc, cls=DecimalEncoder)
    return json.dumps(diccc, default=jsonencoder)


def dictfetchall(cursor):
    """
    Return all rows from a cursor as a dict.
    Assume the column names are unique.
    """
    columns = [col[0] for col in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]


