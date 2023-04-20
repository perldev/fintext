# -*- coding: utf-8 -*-
# This program is dedicated to the public domain under the CC0 license.
#
# THIS EXAMPLE HAS BEEN UPDATED TO WORK WITH THE BETA VERSION 12 OF PYTHON-TELEGRAM-BOT.
# If you're still using version 11.1.0, please see the examples at
# https://github.com/python-telegram-bot/python-telegram-bot/tree/v11.1.0/examples

"""
Basic example for a bot that uses inline keyboards.
"""

import logging
import sys
import time
import telepot
# from telepot.loop import MessageLoop
from telepot.aio.loop import MessageLoop
import asyncio

from telepot.namedtuple import InlineQueryResultArticle, InputTextMessageContent
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton
import decimal
from datetime import datetime, timedelta

import json
import requests
import uuid
import pickle
import traceback
import sys
import ssl
import os
import hashlib
import base64
import copy
from pymemcache.client.base import Client
## add chain of views


from decimal import Decimal
from celery import Celery
import re
from tornado.platform.asyncio import AsyncIOMainLoop
import tornado.web

if (not os.environ.get('PYTHONHTTPSVERIFY', '') and
        getattr(ssl, '_create_unverified_context', None)):
    ssl._create_default_https_context = ssl._create_unverified_context


# TODO move to settings
TEMP = {}
DATA = {}
FLOWS = {}


def make_cached_key(key, key_prefix, version):
    c = key_prefix + str(key)
    c = c.encode()
    hsh_md5 = hashlib.md5(c)
    return base64.b64encode(hsh_md5.digest())


cache = None
if False:
    cache_location = "127.0.0.1:11211"
    conn = cache_location.split(":")
    conn[1] = int(conn[1])
    cache = Client(tuple(conn))

# identify read token for user
API_HOST = "http://127.0.0.1:8000/oper/api/"
MARKETS = []


def format_date(d, timezone=None):
    if timezone is None:
        timezone = time.timezone * -1

    return datetime.utcfromtimestamp(int(d) + timezone).strftime('%Y-%m-%d %H:%M:%S')


def format_numbers(D, count=None):
    if count is None:
        return "%.5f" % (D)
    else:
        format_string = "%.%df" % count
        return format_string % D


bot_settings = {
  
}

api_headers = {"token": bot_settings["api_token"]}


user_settings = {}


def_settings = {
    "objects": None,
    "chat_id": None
}


bot = None
LOCALS = None
loop = None

CACHED_TAGS = []
ALL_MESSAGES = []
# TODO move this to memcached with limit of time
TEMP = {}
DATA = {}
FLOWS = {}

chat_state = "listen"
ret = None
verbose = True

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

lang_Seq = ["en", "ru", "ua"]
Lang = {"ru": {},
        "ua": {
               },
        "en": {
               },
        }

logger = logging.getLogger(__name__)
### HELPERS#####


def create_default_confirmation(context, yes_call):
    futurecall_data1 = createtempparams(
        {"call": "finish_current_flow", "params": [get_text(context, "Okey, i forgot what to do next"), True]})
    tmpbcallbackdata1 = '{"futurecall":"' + futurecall_data1 + '"}'

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text=get_text(context, "Yes"), callback_data=yes_call),
            InlineKeyboardButton(text=get_text(context, "No"), callback_data=tmpbcallbackdata1),
        ]
    ])
    return keyboard


def default_forgot(context, text_message=None):
    if text_message is None:
        text_message = "Or, Forgot and start from begining "
    futurecall_data1 = createtempparams(
        {"call": "finish_current_flow", "params": [get_text(context, "Okey, i forgot what to do next"), True]})
    tmpbcallbackdata1 = '{"futurecall":"' + futurecall_data1 + '"}'
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text=get_text(context, text_message), callback_data=tmpbcallbackdata1),
        ]
    ])
    return keyboard


async def send(context, msg, params=None):
    loop.create_task(bot.sendMessage(context["chat_id"],
                                     get_text(context, "Not avalible"),
                                     reply_markup=keyboard))


def default_reply(context):
    KEYBOARD4DEFAULT = [
        [
            InlineKeyboardButton(text=get_text(context, u"buy"), callback_data='{"call":"buy"}'),
            InlineKeyboardButton(text=get_text(context, u"sell"), callback_data='{"call":"sell"}'),
            InlineKeyboardButton(text=get_text(context, u"markets"), callback_data='{"call":"markets"}'),

        ],
        [
            InlineKeyboardButton(text=get_text(context, u"Monitor the market"),
                                 callback_data='{"call":"watch_the_market"}'),
            InlineKeyboardButton(text=get_text(context, u"Balance"), callback_data='{"call":"balance"}'),
            InlineKeyboardButton(text=get_text(context, u"My active orders"), callback_data='{"call":"my_orders"}'),
            InlineKeyboardButton(text=get_text(context, u"Deals"), callback_data='{"call":"my_deals"}'),

        ],
        [
            InlineKeyboardButton(text=get_text(context, u"Ask support"), callback_data='{"call":"new_request"}'),
            InlineKeyboardButton(text=get_text(context, u"To site"), callback_data='{"call":"dashboard"}'),
            InlineKeyboardButton(text=get_text(context, u"Change Language"), callback_data='{"call":"lang_change"}'),
        ],
        [
            InlineKeyboardButton(text=get_text(context, u"Deposit"), callback_data='{"call":"fillup"}'),
            InlineKeyboardButton(text=get_text(context, u"Withdraw"), callback_data='{"call":"send"}'),
            # InlineKeyboardButton(text="Создать инвойс на оплату", callback_data='{"call":"invoice"}'),
        ]
    ]

    return InlineKeyboardMarkup(inline_keyboard=KEYBOARD4DEFAULT)


class form_flow(object):
    flows = []

    def __init__(self, chain_calls, uid):
        self.__links = link
        self.__current = 0
        self.__len = len(chain_calls)

    def start_flow():
        pass

    @staticmethod
    def looking_flow(chat_id):
        return False

    def call_current(self, context, msg, params):
        self.__links[self.__current](context, msg, params)
        if ret:
            self.__current += 1

        if self.__current >= self.__len:
            finish_flow(self.uid)

        return ret


def make_table_from_list(chat_id, message, L):
    global loop
    keyboards = []
    tmp = []
    i, ki = (0, 0)
    for item in L:
        tmp.append(item)
        i += 1
        ki += 1
        if i > 2:
            keyboards.append(tmp)
            tmp = []
            i = 0
            if ki > 8:
                loop.create_task(
                    bot.sendMessage(chat_id, message, reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboards)))
                keyboards = []
                ki = 0

    if len(tmp) > 0:
        keyboards.append(tmp)

    loop.create_task(bot.sendMessage(chat_id, message, reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboards)))


def inline_answer(flow, chat_id, params):
    global FLOWS
    if chat_id in FLOWS:
        if verbose:
            print("there is another task for this chat %s " % FLOWS[chat_id])
        FLOWS[chat_id] = {"flow": flow, "params": params}
    else:
        FLOWS[chat_id] = {"flow": flow, "params": params}


def finish_flow(chat_id):
    global FLOWS
    if chat_id in FLOWS:
        del FLOWS[chat_id]


def receive_inline_answer(chat_id):
    try:
        tmp = FLOWS[chat_id]
        del FLOWS[chat_id]
        return tmp
    except:
        traceback.print_exc()
        return None


def get_text(context, t):
    if t in Lang[context["lang"]]:
        return Lang[context["lang"]][t]
    return t


def clean_oldtmp():
    if sys.getsizeof(TEMP) > 60000:
        print("is tooo biiggg")


def getfromtemp(key, delete=False):
    res = TEMP[key]
    if delete:
        del TEMP[key]

    return res["params2call"]


def createtempparams(params):
    d = str(uuid.uuid1())
    TEMP[d] = {"time": datetime.now(), "params2call": params}
    return d


def futurecall(context, msg, key):
    try:
        data = getfromtemp(key)
        print(data)

        if isinstance(data["call"], str):
            return LOCALS[data["call"]](context, msg, data["params"])
        return "unsupported call by future "
    except:
        traceback.print_exc()
        return "something going wrong try from the start:("


def setup_context_from_site(token, msg):
    print("setup context from site")
    print("=" * 64)

    chat_id = msg["id"]
    # TODO add auth token for request to auth api
    jreq = {
        "chat_id": chat_id,
        "token": token,
    }

    resp = requests.post(API_HOST + "chat_connect2deal",
                         header=api_headers,
                         params=jreq)
    if verbose:
        print(resp.text)

    res = resp.json()
    us = copy.deepcopy(def_settings)
    us["object"] = res
    us["chat_id"] = chat_id
    us["token"] = token
    us["from"] = msg["from"]
    us["last_update"] = datetime.now()
    user_settings[chat_id] = us
    return us


# should from local cache get user settings by chat id
def setup_context_from_history(chat_id, msg=None):
    global loop
    us = copy.deepcopy(def_settings)

    if verbose:
        print("setup context from history")
        print("=" * 64)
        print(chat_id)
        print(msg)

    nw = datetime.now()

    if chat_id in user_settings:
        print("found local")
        return user_settings[chat_id]
    else:
        print("call on btc trade ua")
        resp = requests.post(API_HOST + "/get_deal_from_chat", headers=api_headers, params={"chat_id": chat_id})
        res = resp.json()
        print("got response")
        print(res)
        if res["status"]:
            user_settings[chat_id] = us
            us["object"] = res
            us["chat_id"] = chat_id

            return us
        else:
            return None


async def coro(blocking_function):
    return blocking_function()


### HELPERS END#####

### VIEWS ####


async def ignore_this(context, msg, currency):
    context["ignore_list"].append(currency)
    loop.create_task(bot.sendMessage(context["chat_id"], get_text(context, "Done ") + currency))

async def new_request_submit(context, msg, prefix):
    if verbose:
        print("new_request_submit")
        print(msg)

    chat_id = context["chat_id"]
    raw_msg = prefix + "\n" + msg["text"]
    inline_answer("new_request_submit", chat_id, raw_msg)
    futurecall_data = createtempparams({"call": "send_ticket", "params": raw_msg})
    tmpbcallbackdata = '{"futurecall":"' + futurecall_data + '"}'

    futurecall_data1 = createtempparams(
        {"call": "finish_current_flow", "params": [get_text(context, "Okey, i forgot what to do next"), True]})
    tmpbcallbackdata1 = '{"futurecall":"' + futurecall_data1 + '"}'

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text=get_text(context, "Yes, send it"), callback_data=tmpbcallbackdata),
            InlineKeyboardButton(text=get_text(context, "Or, return "), callback_data=tmpbcallbackdata1),
        ]
    ])

    loop.create_task(bot.sendMessage(context["chat_id"], raw_msg, reply_markup=keyboard))


async def finish_current_flow(context, raw_telepot_msg, params):
    [forgotmessage, showmenu] = params
    chat_id = context["chat_id"]
    finish_flow(chat_id)
    if showmenu:
        loop.create_task(bot.sendMessage(context["chat_id"], forgotmessage, reply_markup=default_reply(context)))


async def send_ticket(context, raw_telepot_msg, messagefromchain):
    if verbose:
        print("send ticket to us")
        print(raw_telepot_msg)

    text_msg = messagefromchain
    username = context["username"]
    user_id = context["user_id"]
    chat_id = context["chat_id"]
    email = context["email"]

    celery_app = Celery(settings["TICKET_NAME_APP"], broker=settings["APP_BROKER"])
    meta = {"reply-to": "telegram", "chat_id": chat_id, "text": text_msg, "email": email}

    celery_app.send_task(settings["TICKET_NAME_APP"] + '.ticket_submit',
                         args=(user_id,
                               "telegram",
                               text_msg,
                               json.dumps(meta),
                               email,
                               ["telegram_chat"]),
                         serializer='json')

    finish_flow(chat_id)
    loop.create_task(bot.sendMessage(chat_id, get_text(context, "request submited")))


async def new_request(context, msg, params=None):
    if verbose:
        print("new_request")
        print(msg)
        print("===" * 12)

    chat_id = context["chat_id"]
    loop.create_task(bot.sendMessage(chat_id, u"Гаразд напишить будь ласка нам ваше питання"))
    inline_answer("new_request_submit", chat_id, "")


def start(msg=None):
    if verbose:
        print("start callback")
        print("=" * 64)

    content_type, chat_type, chat_id = telepot.glance(msg)
    if verbose:
        print(content_type, chat_type, chat_id, msg)

    # kicked member 'new_chat_member': {'user': {'id': 462458816, 'is_bot': True, 'first_name': 'Personal BTC TRADE UA', 'username': 'BTCTradeUaBot'}, 'status': 'kicked', 'until_date': 0}
    # new message {'message_id': 623, 'from': {'id': 188152510, 'is_bot': False, 'first_name': 'Bogdan', 'last_name': 'Chayka', 'username': 'zbaobab', 'language_code': 'en'}, 'chat': {'id': 188152510, 'first_name': 'Bogdan', 'last_name': 'Chayka', 'username': 'zbaobab', 'type': 'private'}, 'date': 1623584628, 'text': '/start', 'entities': [{'offset': 0, 'length': 6, 'type': 'bot_command'}]}

    if content_type == "new_chat_member":
        process_chat_member(content_type, chat_type, chat_id, msg)

    if content_type == "text":
        process_text(content_type, chat_type, chat_id, msg)


def process_chat_member(content_type, chat_type, chat_id, msg):
    if verbose:
        print("process new_chat_member")
    print(content_type, chat_type, chat_id, msg)


def process_text(content_type, chat_type, chat_id, msg):
    global loop, verbose
    if verbose:
        print("process text")

    # try to identify the user and save his profile
    text_msg = msg["text"]
    context = None
    if text_msg.startswith("/start"):
        # this also for first start
        try:
            m = re.match("/start ([^ ]+)", text_msg)
            if m:
                context = setup_context_from_site(m.group(1), msg["chat"])
            else:
                raise Exception("there is no token")
        except:
            traceback.print_exc()
            print("do not find token try find in history")
            context = setup_context_from_history(msg["chat"]["id"], msg["chat"])

    else:
        context = setup_context_from_history(msg["chat"]["id"], msg["chat"])

    if verbose:
        print(context)

    if context is None:
        loop.create_task(bot.sendMessage(chat_id, u"You have no right to access this bot"))
        return

    keyboard = None

    if chat_id in FLOWS:
        if verbose:
            print("flow")  # in flow of messages

        params = receive_inline_answer(chat_id)
        if verbose:
            print(params["flow"])
        loop.create_task(LOCALS[params["flow"]](context, msg, params["params"]))

    elif "reply_to_message" in msg and msg["reply_to_message"]["message_id"] in FLOWS:
        print("reply to ")  # reply to message
        params = receive_inline_answer(msg["reply_to_message"]["message_id"])
        loop.create_task(LOCALS[params["flow"]](context, msg, params["params"]))

    elif form_flow.looking_flow(chat_id):
        print("through linking")
        obj_flow = form_flow.looking_flow(chat_id)
        loop.create_task(obj_flow(context, msg))
    else:
        print("send message to us")
        send_message2us(context, msg)
        # default_menu(context, msg)

def send_message2us(context, msg):
    if verbose:
        print(msg)
    out_user = "%s ( %s %s )" % (context["from"]["username"],
                                 context["from"]["first_name"],
                                 context["from"]["last_name"])

    resp = requests.post(API_HOST+"message_income/"+context["token"],
                         params={"text": msg,
                                 "username": out_user})
    if verbose:
        print(resp.text)



def default_menu(context, msg, params=None):
    reply_markup = default_reply(context)
    chat_id = context["chat_id"]
    loop.create_task(bot.sendMessage(chat_id, u"Выберите что бы вы хотели сделать", reply_markup=reply_markup))


def on_callback_query(msg):
    if verbose:
        print("on_callback_query")

    global ret, chat_state, loop

    if verbose:
        print("=" * 64)

    query_id, from_id, query_data = telepot.glance(msg, flavor='callback_query')

    if verbose:
        print('Callback Query:', query_id, from_id, query_data, msg["data"])

    data = json.loads(msg["data"])

    if verbose:
        print("data to callback")
        print(data)

    context = setup_context_from_history(from_id, msg)
    if context is None:
        loop.create_task(bot.sendMessage(chat_id, u"You have no right to access this bot"))
        return

    logs = ""
    if "futurecall" in data:
        loop.create_task(futurecall(context, msg, data["futurecall"]))
    elif "call" in data and "params" in data:
        loop.create_task(LOCALS[data["call"]](context, msg, data["params"]))
    elif "call" in data:
        loop.create_task(LOCALS[data["call"]](context, msg))
    else:
        loop.create_task(
            bot.sendMessage(operator_chat_id, "some unexpected command please write us on support@btc-trade.com.ua"))
        return

## process this function
async def inline_await(list_subs):
    worked = {}
    work = True
    i = 1000
    while work and i > 0:
        print("processes subscribes")
        i -= 1
        await asyncio.sleep(2)
        work = False
        for item in list_subs:
            if item["task"].done():
                ret = item["task"].result()
                try:
                    print(ret)
                    print(item["call_object"])
                    if not ret["message_id"] in worked:
                        inline_answer("confirm_quick_answer", ret["message_id"], item["call_object"])
                        worked[ret["message_id"]] = True
                except:
                    traceback.print_exc()

            else:
                print("not finished")
                work = True


def noasno(msg, params):
    ticket_id = params["id"]
    ret = loop.create_task(bot.sendMessage(chat_id, 'NO as No.. but user wait'))


def quick_answer(msg, params):
    global CACHED_TAGS
    chat_id = params[1]
    ticket_id = params[0]
    # inline_answer("confirm_quick_answer", chat_id, params)
    messages = []
    keyboards = []
    tmp = []
    i = 0
    ki = 0
    resp = requests.post("%sdialogs" % (BOARD), data={"token": BOARDTOKEN})
    CACHED_TAGS = resp.json()
    for item in CACHED_TAGS["msgs"]:
        print(item)
        if "tags" in item:
            tags = item["tags"]
            for tag in tags.split("|"):
                if len(tag) > 0:
                    d = createtempparams(
                        {"call": "confirm_quick_answer", "params": [params[0], params[1], item["txt"]]})
                    tmpbcallbackdata = '{"futurecall":"' + d + '"}'
                    tmp.append(InlineKeyboardButton(text=tag,
                                                    callback_data=tmpbcallbackdata))
                    i += 1
                    ki += 1
                    if i > 2:
                        keyboards.append(tmp)
                        tmp = []
                        i = 0
                        if ki > 8:
                            loop.create_task(bot.sendMessage(chat_id=chat_id,
                                                             text="quick answers: ",
                                                             reply_markup=InlineKeyboardMarkup(
                                                                 inline_keyboard=keyboards)))
                            keyboards = []
                            ki = 0

    if len(tmp) > 0:
        keyboards.append(tmp)

    loop.create_task(bot.sendMessage(chat_id=chat_id,
                                     text="quick answers: ",
                                     reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboards)))


def confirm_quick_answer(msg, params):
    if verbose:
        print(params)
    text_message = None
    chat_id = params[1]
    if "text" in msg:
        text_message = msg["text"]
    else:
        text_message = params[2]
        loop.create_task(bot.sendMessage(chat_id=chat_id,
                                         text=text_message,
                                         ))

    d = createtempparams({"call": "answer", "params": {"id": params[0], "chat_id": params[1], "text": text_message}})
    d1 = createtempparams({"call": "noasno", "params": {"id": params[0], "chat_id": params[1]}})
    keyboard = [[InlineKeyboardButton(text="Send", callback_data='{"futurecall":"' + d + '"}'),
                 InlineKeyboardButton(text="No", callback_data='{"futurecall":"' + d1 + '"}')],
                ]
    reply_markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
    ticket = DATA[params[0]]

    tags = ticket["tags"]
    tags = tags.replace("__green__", "")  # remove formating from tags
    tags = tags.replace("_green_", "")  # remove formating from tags
    formated = u"Confirm this answer on this ticket \n %s,\n %s \n %s \n %s \n %s" % (
    ticket["pub_date"], tags, ticket.get("email", ""), ticket["subject"], ticket["txt"][:400])
    # TODO wrap such messages
    loop.create_task(bot.sendMessage(chat_id=chat_id,
                                     text=formated,
                                     reply_markup=reply_markup
                                     ))


def help(update, context):
    update.message.reply_text("Use /start to test this bot.")


def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def on_chosen_inline_result(msg):
    result_id, from_id, query_string = telepot.glance(msg, flavor='chosen_inline_result')
    print('Chosen Inline Result:', result_id, from_id, query_string)


def on_inline_query(msg):
    print("=" * 64)
    query_id, from_id, query_string = telepot.glance(msg, flavor='inline_query')

    print('Inline Query:', query_id, from_id, query_string)
    global loop

    articles = [InlineQueryResultArticle(
        id='abc',
        title=u"Are you alive",
        input_message_content=InputTextMessageContent(
            message_text='Т�~K жив?'
        )
    )]

    loop.create_task(bot.answerInlineQuery(query_id, articles))


class AnswerTicket(tornado.web.RequestHandler):

    def post(self):
        global loop, bot
        ticket = tornado.escape.json_decode(self.request.body)

        # [{"fields": {"status": "created", "group_id": 10, "tags": "", "raw_msg": "ticket", "user": 10, "has_attach": false, "txt": "site: https://btc-trade.com.ua/ \n phone: +380973426645 \n email: savemymind@gmail.com \n text: kzsklhdalkls alsd", "pub_date": "2020-09-24T14:15:28.523", "subject": "helpbox"}, "model": "main.ticket", "pk": 328987}]
        ## add reply id
        chat_id = ticket["chat_id"]
        txt = ticket["txt"]
        from_support = ticket["from"]
        context = setup_context_from_history(chat_id)
        # TODO check  weather  is it  too long
        ret = loop.create_task(bot.sendMessage(chat_id=chat_id,
                                               text=txt,
                                               ))
        # it's very danger
        # add handler on reply action in telegram
        # inline_answer("confirm_quick_answer", re  ,[str(ticket["id"]), chat_id])
        self.write({"status": True})


##it's should be one process
async def inline_await_possible_reply(ret):
    worked = {}
    work = True
    i = 100
    while work and i > 0:
        print("processes subscribes")
        i -= 1
        await asyncio.sleep(1)
        work = False
        if ret.done():
            ret = ret.result()
            try:
                if verbose:
                    print(ret)
                inline_answer("new_request_submit", ret["message_id"], "")
            except:
                traceback.print_exc()

        else:
            print("not finished")
            work = True

# {'chat': {'id': 188152510, 'first_name': 'Bogdan', 'last_name': 'Chayka', 'username': 'zbaobab', 'type': 'private'}, 'from': {'id': 188152510, 'is_bot': False, 'first_name': 'Bogdan', 'last_name': 'Chayka', 'username': 'zbaobab', 'language_code': 'en'}, 'date': 1623583179, 'old_chat_member': {'user': {'id': 462458816, 'is_bot': True, 'first_name': 'Personal BTC TRADE UA', 'username': 'BTCTradeUaBot'}, 'status': 'member'}, 'new_chat_member': {'user': {'id': 462458816, 'is_bot': True, 'first_name': 'Personal BTC TRADE UA', 'username': 'BTCTradeUaBot'}, 'status': 'kicked', 'until_date': 0}}
# seems not used
class NewTicket(tornado.web.RequestHandler):
    def post(self):
        global loop, bot
        args = tornado.escape.json_decode(self.request.body)

        self.write({"status": True})


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.write({})


class AlertHandle(tornado.web.RequestHandler):

    def post(self, chat_id):
        global loop, bot, user_settings
        msg = json.loads(self.request.body)
        loop.create_task(bot.sendMessage(chat_id=int(chat_id),
                                         text=msg["text"]),
                         )

        self.write("{\"status\": true}")


def make_app():
    return tornado.web.Application([
        (r"/", MainHandler),
        (r"/answer_to", AnswerTicket),
        (r"/alert/([\w]+)", AlertHandle),
        (r"/new_ticket", NewTicket),  ##Seems not used
    ])


print('starting ...')
LOCALS = locals()

if __name__ == "__main__":
    AsyncIOMainLoop().install()
    bot = telepot.aio.Bot(bot_settings["TOKEN"])
    msg_loop = MessageLoop(bot, {'chat': start,
                                 'callback_query': on_callback_query,
                                 'inline_query': on_inline_query,
                                 'chosen_inline_result': on_chosen_inline_result})
    app = make_app()
    app.listen(8881)
    loop = asyncio.get_event_loop()
    loop.create_task(msg_loop.run_forever())
    print('Listening ...')
    loop.run_forever()
