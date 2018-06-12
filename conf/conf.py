#!/usr/bin/python

import os
import sys

dir_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
dir_db = dir_root + '/db/'
dir_log = dir_root + '/logs/'
dir_conf = dir_root + '/conf/'

# ↓ The "proxy" property setting below is for CORS-proxying only!
# Do not use it if you don't know what a CORS proxy is.
# https://github.com/ccxt/ccxt/wiki/Install#cors-access-control-allow-origin
# You should only use the "proxy" setting if you're having a problem with Access-Control-Allow-Origin
# In Python you rarely need to use it, if ever at all.
proxies_cors = [
    '',  # no proxy by default
    'https://crossorigin.me/',
    'https://cors-anywhere.herokuapp.com/',
]

# ↓ The "aiohttp_proxy" setting is for HTTP(S)-proxying (SOCKS, etc...)
# It is a standard method of sending your requests through your proxies
# This gets passed to the `asyncio` and `aiohttp` implementation directly
# You can use this setting as documented here:
# https://docs.aiohttp.org/en/stable/client_advanced.html#proxy-support
# This is the setting you should be using with async version of ccxt in Python 3.5+
proxies_aiohttp = [
    'http://127.0.0.1:1080',
    #'http://proxy.com',
    #'http://user:pass@some.proxy.com',
    #'http://10.10.1.10:3128',
]

# ↓ On the other hand, the "proxies" setting is for HTTP(S)-proxying (SOCKS, etc...)
# It is a standard method of sending your requests through your proxies
# This gets passed to the `python-requests` implementation directly
# You can also enable this with environment variables, as described here:
# http://docs.python-requests.org/en/master/user/advanced/#proxies
# The environment variables should be set before importing ccxt (!)
# This is the setting you should be using with synchronous version of ccxt in Python 2 and 3
proxies_sync = {
    #'http': 'http://10.10.1.10:3128',
    #'https': 'http://10.10.1.10:1080',
}

conf_key = {
    "binance": {
        'apiKey': "kHgviPR8ijyNWn0PcltvzWkOqpr3nlDzGp6wY2ZEsQNa1F7k3ePhV0C7oOq8e6Cu",
        'secret': "aqdBURqQxxk29mE31mEMIpW6zI5QsA5PKw1wf8VI7XDGG1WxJrAFWkTwEnMOJQbB",
    },
    "bitmex": {
        "apiKey": "DPBrxuhRdVaBEUNiNaAlJOrw",
        "secret": "spMNDyhaRhEtCyQTGPSMKOwW9YIM8LYV0daWOm4ZiNSleRew",
    },
    "bitz": {
        "apiKey": "c1cf93a1182e5a38bb8a8c3458310396",
        "secret": "a7a55512ee789d6519fd005345644133",
    },
    "gdax": {
        'apiKey': "GnFmvkkPinzOXSWM",
        'secret': "",
        'password': 'zdmj8o7byla',
        'urls': {
            'api': 'https://api-public.sandbox.gdax.com',
        },
    },
    "hitbtc": {
        "apiKey": "00c576eec474fab35709aeb546dcf577",
        "secret": "568e6d454ea9897b183c4ba2ff4bf598",
    },
    "hitbtc2": {
        "apiKey": "00c576eec474fab35709aeb546dcf577",
        "secret": "568e6d454ea9897b183c4ba2ff4bf598",
    },
    "huobi": {
        "apiKey": "a3a1ee7f-2e64f1bb-925f3e37-3fe72",
        "secret": "05c371ab-0d9d012f-39d3f12d-a6c68",
    },
    "huobicny": {
        "apiKey": "a3a1ee7f-2e64f1bb-925f3e37-3fe72",
        "secret": "05c371ab-0d9d012f-39d3f12d-a6c68",
    },
    "huobipro": {
        "apiKey": "a3a1ee7f-2e64f1bb-925f3e37-3fe72",
        "secret": "05c371ab-0d9d012f-39d3f12d-a6c68",
    },
    "kucoin": {
        "apiKey": "5a92a5e003d644701f1a9c56",
        "secret": "400e8874-e3cf-43f1-8765-63e4b7f535a5",
    },
    "okcoincny": {
        "apiKey": "63f1b985-88fe-48c1-bb91-2f6f1f086ce5",
        "secret": "896AE910647BB0911BDF27949508E065",
    },
    "okcoinusd": {
        "apiKey": "63f1b985-88fe-48c1-bb91-2f6f1f086ce5",
        "secret": "896AE910647BB0911BDF27949508E065",
    },
    "okex": {
        "apiKey": "7f10be5e-afd4-41a9-9c3c-fa9602996447",
        "secret": "71B22F85C687D223954FE4432B2A61B9",
    },
    "poloniex": {
        "apiKey": "OQDZM5YM-OKX5QEUE-Z3IDJZG2-NEHLDQKS",
        "secret": "b36baf9613ab1fec64c549c2472e7b7c2b63b4f16667feb576a0601331fdd24bb1b22dda3c867e89b7beb5b2854cf66b6f2cd011d1adb8634ddeb3f7310337e1",
    },
    "zb": {
        "apiKey": "a6fad7d3-3830-400d-8326-b1f8b3fb68ec",
        "secret": "1c5f5e7e-1c37-4cac-9bd3-029292da681a",
    },
}



