#!/usr/bin/python

import os
import sys
import time
import ccxt.async as ccxt
sys.path.append("..")
sys.path.append(os.getcwd())
sys.path.append(os.path.dirname(os.getcwd()))
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import bz_conf


def symbol_2_string(symbol):
    symbol_1 = symbol.split('/')[0]       # BTC
    symbol_2 = symbol.split('/')[1]       # USD
    s = symbol_1 + '_' + symbol_2
    return s

async def load_markets(exchange):
    err_timeout = 0
    err_ddos = 0
    err_auth = 0
    err_not_available = 0
    err_exchange = 0
    err_network = 0
    err = 0
    while True:
        try:
            await exchange.load_markets()
            return True
        except ccxt.RequestTimeout as e:
            err_timeout = err_timeout + 1
            print(exchange.id, type(e).__name__, '=', e.args, 'c=', err_timeout)
        except ccxt.DDoSProtection as e:
            err_ddos = err_ddos + 1
            print(exchange.id, type(e).__name__, '=', e.args, 'c=', err_ddos)
            time.sleep(10.0)
        except ccxt.AuthenticationError as e:
            err_auth = err_auth + 1
            print(exchange.id, type(e).__name__, '=', e.args, 'c=', err_auth)
            if err_auth > 5:
                return False
        except ccxt.ExchangeNotAvailable as e:
            print(exchange.id, type(e).__name__, '=', e.args)
            return False
        except ccxt.ExchangeError as e:
            print(exchange.id, type(e).__name__, '=', e.args)
        except ccxt.NetworkError as e:
            err_network = err_network + 1
            print(exchange.id, type(e).__name__, '=', e.args, 'c=', err_network)
            time.sleep(10.0)
        except Exception as e:
            err = err + 1
            print(exchange.id, type(e).__name__, '=', e.args)
            if err > 5:
                return False
    return False

async def is_support_symbol(exchange, symbol):
    await load_markets(exchange)
    if symbol in exchange.markets:
        return True
    return False

async def verify_symbol(exchange, symbol):
    if await is_support_symbol(exchange, symbol):
        return symbol
    # 不支持此 symbol
    symbol_1 = symbol.split('/')[0]       # BTC
    symbol_2 = symbol.split('/')[1]       # USD
    ret_s = ''
    # 没有 xxx/usd，只有 xxx/usdt
    if symbol_2 == 'USD':
        ret_s = symbol_1 + '/USDT'
        if await is_support_symbol(exchange, ret_s):
            return ret_s
    # 没有 DASH/xxx, 只有 DSH/xxx
    if symbol_1 == 'DASH':
        ret_s = 'DSH/' + symbol_2
        if await is_support_symbol(exchange, ret_s):
            return ret_s
    # 没有 IOTA/xxx, 只有 IOT/xxx
    if symbol_1 == 'IOTA':
        ret_s = 'IOT/' + symbol_2
        if await is_support_symbol(exchange, ret_s):
            return ret_s
    return ''


def init_spider(db, exchanges):
    list_exchanges = []
    for k in exchanges:
        db.create_table_exchange(k)
        exc = find_exchange_from_id(k)
        list_exchanges.append(exc)
    return list_exchanges

def find_exchange_from_id(exchange_id):
    k = exchange_id
    if k == bz_conf.acx.id:
        return bz_conf.acx
    if k == bz_conf.allcoin.id:
        return bz_conf.allcoin
    if k == bz_conf.anxpro.id:
        return bz_conf.anxpro
    if k == bz_conf.bibox.id:
        return bz_conf.bibox
    if k == bz_conf.binance.id:
        return bz_conf.binance
    if k == bz_conf.bit2c.id:
        return bz_conf.bit2c
    if k == bz_conf.bitbay.id:
        return bz_conf.bitbay
    if k == bz_conf.bitcoincoid.id:
        return bz_conf.bitcoincoid
    if k == bz_conf.bitfinex.id:
        return bz_conf.bitfinex
    if k == bz_conf.bitfinex2.id:
        return bz_conf.bitfinex2
    if k == bz_conf.bitflyer.id:
        return bz_conf.bitflyer
    if k == bz_conf.bithumb.id:
        return bz_conf.bithumb
    if k == bz_conf.bitlish.id:
        return bz_conf.bitlish
    if k == bz_conf.bitmarket.id:
        return bz_conf.bitmarket
    if k == bz_conf.bitmex.id:
        return bz_conf.bitmex
    if k == bz_conf.bitso.id:
        return bz_conf.bitso
    if k == bz_conf.bitstamp.id:
        return bz_conf.bitstamp
    if k == bz_conf.bitstamp1.id:
        return bz_conf.bitstamp1
    if k == bz_conf.bittrex.id:
        return bz_conf.bittrex
    if k == bz_conf.bitz.id:
        return bz_conf.bitz
    if k == bz_conf.bl3p.id:
        return bz_conf.bl3p
    if k == bz_conf.bleutrade.id:
        return bz_conf.bleutrade
    if k == bz_conf.braziliex.id:
        return bz_conf.braziliex
    if k == bz_conf.btcbox.id:
        return bz_conf.btcbox
    if k == bz_conf.btcchina.id:
        return bz_conf.btcchina
    if k == bz_conf.btcexchange.id:
        return bz_conf.btcexchange
    if k == bz_conf.btcmarkets.id:
        return bz_conf.btcmarkets
    if k == bz_conf.btctradeua.id:
        return bz_conf.btctradeua
    if k == bz_conf.btcturk.id:
        return bz_conf.btcturk
    if k == bz_conf.btcx.id:
        return bz_conf.btcx
    if k == bz_conf.bxinth.id:
        return bz_conf.bxinth
    if k == bz_conf.ccex.id:
        return bz_conf.ccex
    if k == bz_conf.cex.id:
        return bz_conf.cex
    if k == bz_conf.chbtc.id:
        return bz_conf.chbtc
    if k == bz_conf.chilebit.id:
        return bz_conf.chilebit
    if k == bz_conf.cobinhood.id:
        return bz_conf.cobinhood
    if k == bz_conf.coincheck.id:
        return bz_conf.coincheck
    if k == bz_conf.coinexchange.id:
        return bz_conf.coinexchange
    if k == bz_conf.coinfloor.id:
        return bz_conf.coinfloor
    if k == bz_conf.coingi.id:
        return bz_conf.coingi
    if k == bz_conf.coinmarketcap.id:
        return bz_conf.coinmarketcap
    if k == bz_conf.coinmate.id:
        return bz_conf.coinmate
    if k == bz_conf.coinsecure.id:
        return bz_conf.coinsecure
    if k == bz_conf.coinspot.id:
        return bz_conf.coinspot
    if k == bz_conf.cryptopia.id:
        return bz_conf.cryptopia
    if k == bz_conf.dsx.id:
        return bz_conf.dsx
    if k == bz_conf.exmo.id:
        return bz_conf.exmo
    if k == bz_conf.flowbtc.id:
        return bz_conf.flowbtc
    if k == bz_conf.foxbit.id:
        return bz_conf.foxbit
    if k == bz_conf.fybse.id:
        return bz_conf.fybse
    if k == bz_conf.fybsg.id:
        return bz_conf.fybsg
    if k == bz_conf.gatecoin.id:
        return bz_conf.gatecoin
    if k == bz_conf.gateio.id:
        return bz_conf.gateio
    if k == bz_conf.gdax.id:
        return bz_conf.gdax
    if k == bz_conf.gemini.id:
        return bz_conf.gemini
    if k == bz_conf.getbtc.id:
        return bz_conf.getbtc
    if k == bz_conf.hitbtc.id:
        return bz_conf.hitbtc
    if k == bz_conf.hitbtc2.id:
        return bz_conf.hitbtc2
    if k == bz_conf.huobi.id:
        return bz_conf.huobi
    if k == bz_conf.huobicny.id:
        return bz_conf.huobicny
    if k == bz_conf.huobipro.id:
        return bz_conf.huobipro
    if k == bz_conf.independentreserve.id:
        return bz_conf.independentreserve
    if k == bz_conf.itbit.id:
        return bz_conf.itbit
    if k == bz_conf.jubi.id:
        return bz_conf.jubi
    if k == bz_conf.kraken.id:
        return bz_conf.kraken
    if k == bz_conf.kucoin.id:
        return bz_conf.kucoin
    if k == bz_conf.kuna.id:
        return bz_conf.kuna
    if k == bz_conf.lakebtc.id:
        return bz_conf.lakebtc
    if k == bz_conf.liqui.id:
        return bz_conf.liqui
    if k == bz_conf.livecoin.id:
        return bz_conf.livecoin
    if k == bz_conf.luno.id:
        return bz_conf.luno
    if k == bz_conf.lykke.id:
        return bz_conf.lykke
    if k == bz_conf.mercado.id:
        return bz_conf.mercado
    if k == bz_conf.mixcoins.id:
        return bz_conf.mixcoins
    if k == bz_conf.nova.id:
        return bz_conf.nova
    if k == bz_conf.okcoincny.id:
        return bz_conf.okcoincny
    if k == bz_conf.okcoinusd.id:
        return bz_conf.okcoinusd
    if k == bz_conf.okex.id:
        return bz_conf.okex
    if k == bz_conf.paymium.id:
        return bz_conf.paymium
    if k == bz_conf.poloniex.id:
        return bz_conf.poloniex
    if k == bz_conf.qryptos.id:
        return bz_conf.qryptos
    if k == bz_conf.quadrigacx.id:
        return bz_conf.quadrigacx
    if k == bz_conf.quoinex.id:
        return bz_conf.quoinex
    if k == bz_conf.southxchange.id:
        return bz_conf.southxchange
    if k == bz_conf.surbitcoin.id:
        return bz_conf.surbitcoin
    if k == bz_conf.therock.id:
        return bz_conf.therock
    if k == bz_conf.tidex.id:
        return bz_conf.tidex
    if k == bz_conf.urdubit.id:
        return bz_conf.urdubit
    if k == bz_conf.vaultoro.id:
        return bz_conf.vaultoro
    if k == bz_conf.vbtc.id:
        return bz_conf.vbtc
    if k == bz_conf.virwox.id:
        return bz_conf.virwox
    if k == bz_conf.wex.id:
        return bz_conf.wex
    if k == bz_conf.xbtce.id:
        return bz_conf.xbtce
    if k == bz_conf.yobit.id:
        return bz_conf.yobit
    if k == bz_conf.yunbi.id:
        return bz_conf.yunbi
    if k == bz_conf.zaif.id:
        return bz_conf.zaif
    if k == bz_conf.zb.id:
        return bz_conf.zb
    return None
