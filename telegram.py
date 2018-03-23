# basic telegram bot
# https://www.codementor.io/garethdwyer/building-a-telegram-bot-using-python-part-1-goi5fncay
# https://github.com/sixhobbits/python-telegram-tutorial/blob/master/part1/echobot.py

import json 
import requests
import time
import urllib
import database_parser
from numpy.random import choice
import re
# python3: urllib.parse.quote_plus
# python2: urllib.pathname2url

TOKEN = "553617004:AAGFq_FMPlojaJcdn4dzrWgUmfnUU3gOyTs" # don't put this in your repo! (put in config, then import config)
URL = "https://api.telegram.org/bot{}/".format(TOKEN)

CHOICES = ["Waarom?","Ik snap het niet", "Hé?","Matthijs' haar zit altijd goed"]


Q = database_parser.Querier('Filmquotes.xml')


def get_url(url):
    response = requests.get(url)
    content = response.content.decode("utf8")
    return content


def get_json_from_url(url):
    content = get_url(url)
    js = json.loads(content)
    return js


def get_updates(offset=None):
    url = URL + "getUpdates?timeout=100"
    if offset:
        url += "&offset={}".format(offset)
    js = get_json_from_url(url)
    return js


def get_last_update_id(updates):
    update_ids = []
    for update in updates["result"]:
        update_ids.append(int(update["update_id"]))
    return max(update_ids)


def echo_all(updates):
    for update in updates["result"]:
        text = update["message"]["text"]
        chat = update["message"]["chat"]["id"]
        answer = ""
        if "quote" in text.lower():
            remq = re.compile(r'\s*quote|quote\s*')
            answer = Q.returnQuote(remq.sub('',text.lower()))
        elif "about" in text.lower():
            rema = re.compile(r'\s*about|about\s*')
            answer = Q.returnInfo(rema.sub('',text.lower()))
        else:
            answer = choice(CHOICES,1)[0]
        send_message(answer, chat)


def get_last_chat_id_and_text(updates):
    num_updates = len(updates["result"])
    last_update = num_updates - 1
    text = updates["result"][last_update]["message"]["text"]
    chat_id = updates["result"][last_update]["message"]["chat"]["id"]
    return (text, chat_id)


def send_message(text, chat_id):
    text = urllib.parse.quote_plus(text) # urllib.parse.quote_plus(text) # (python3)
    url = URL + "sendMessage?text={}&chat_id={}".format(text, chat_id)
    get_url(url)


def main():
    last_update_id = None
    while True:
        updates = get_updates(last_update_id)
        if len(updates["result"]) > 0:
            last_update_id = get_last_update_id(updates) + 1
            echo_all(updates)
        time.sleep(0.5)


if __name__ == '__main__':
    main()
