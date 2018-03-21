import urllib.request
import json
import random
import os
import socket
import datetime

socket.setdefaulttimeout(5)




url = 'https://api.binance.com//api/v3/ticker/price'
response = urllib.request.urlopen(url)
page = response.read()
allcoin = json.loads(page)

# print(allcoin)
# print("代码----------价格")
btc_coin = dict()
eth_coin = dict()
for item in allcoin:
    coin = item["symbol"][:-3]
    quote = item["symbol"][-3:]
    if quote == "BTC":
        btc_coin[coin] = item
    if quote == "ETH":
        eth_coin[coin] = item

ethprice = float(btc_coin["ETH"]["price"])
# print("\nETH卖一价：",ethprice)
print("\n【三角套利】")
print (datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

# 3. 计算正向套利空间
print("币种------ETH记价---ETH/BTC价---转成BTC价---直接BTC价--价差比")
for k, v in btc_coin.items():
    if k in eth_coin:
    
        coin2btc = float(ethprice) * float(eth_coin[k]["price"])
        btcbuy  = float(btc_coin[k]["price"]) #BTC买一
        profit = round((btcbuy - coin2btc) * 1000 / coin2btc, 2)
        if profit > 6:
            print("%s\t%10.8f  %10.8f  %10.8f  %10.8f  %s‰"%(k, float(eth_coin[k]["price"]), round(ethprice,8), round(coin2btc, 8), btcbuy, ("\033[0;32;40m" + str(profit) + "\033[0m")))
        elif profit > 1:
            print("%s\t%10.8f  %10.8f  %10.8f  %10.8f  %s‰"%(k, float(eth_coin[k]["price"]), round(ethprice,8), round(coin2btc, 8), btcbuy, ("\033[0;33;40m" + str(profit) + "\033[0m")))
        elif profit > 0:
            print("%s\t%10.8f  %10.8f  %10.8f  %10.8f  %s‰"%(k, float(eth_coin[k]["price"]), round(ethprice,8), round(coin2btc, 8), btcbuy, profit))
        # else:
            # print("%s\t%10.8f  %10.8f  %10.8f  %10.8f  %3.4f"%(k, float(eth_coin[k]["price"]), round(ethprice,8), round(coin2btc, 8), btcbuy, profit))

