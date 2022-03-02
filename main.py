#!/usr/bin/env python3
"""
                 .
                .;;:,.
                 ;iiii;:,.                                   .,:;.
                 :i;iiiiii:,                            .,:;;iiii.
                  ;iiiiiiiii;:.                    .,:;;iiiiii;i:
                   :iiiiiiiiiii:......,,,,,.....,:;iiiiiiiiiiii;
                    ,iiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiii:
                     .:iii;iiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiii;,
                       .:;;iiiiiiiiiiiiiiiiiiiiiiiiiii;;ii;,
                        :iiii;;iiiiiiiiiiiiiii;;iiiiiii;:.
                       ,iiii;1f:;iiiiiiiiiiii;if;:iiiiiii.
                      .iiiii:iL..iiiiiiiiiiii;:f: iiiiiiii.
                      ;iiiiii:.,;iiii;iiiiiiii:..:iiiiiiii:
                     .i;;;iiiiiiiiii;,,;iiiiiiiiiiii;;iiiii.
                     ::,,,,:iiiiiiiiiiiiiiiiiiiiii:,,,,:;ii:
                     ;,,,,,:iiiiiiii;;;;;;;iiiiii;,,,,,,;iii.
                     ;i;;;;iiiiiiii;:;;;;;:iiiiiii;::::;iiii:
                     ,iiiiiiiiiiiiii;;;;;;:iiiiiiiiiiiiiiiiii.
                      .iiiiiiiiiiiiii;;;;;iiiiiiiiiiiiiiiiiii:
                       .;iiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiii;
                        ;iiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiii.
                       .;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;,
"""
#retrieve the token
def token():
    with open("./stockage/Token", "r") as tf:
        token = tf.read()
        tf.close()
    return token

global tunes
tunes = 0
def je_possede_des_tunes():
    return tunes

#execute if main
if __name__ == "__main__":
    import discord
    from discord.ext import commands,tasks
    from itertools import cycle
    import json
    import os
    import sys
    sys.path.append('./utilities')
    from custom_indicators import CustomIndocators as ci
    from spot_ftx import SpotFtx
    import pandas as pd
    import ta
    import ccxt
    from datetime import datetime
    import time

    token = token()
    description = """un bot gérant un rpg tout simplement"""
    bot = discord.Client()
    os.chdir("./stockage")
    client = commands.Bot(command_prefix = "rpg ", description = description)


@client.event
async def on_ready():
    global status
    status = cycle([f"""{je_possede_des_tunes()}$"""])
    change_status.start()

    with open("version","r") as v:
        version = v.read()
        v.close
    version = version.replace(".","")
    version = int(version)
    version += 1
    version = str(version)
    while len(version) < 6:
        version = "0" + version
    new_version = ""
    for c in version:
        new_version += c
        if len(new_version) < 10:
            new_version += "."
    with open("version","w") as v:
        v.write(new_version)
        v.close()

    print("\n\n\n\n\n\nMy body is ready to burn some dragons")
    print(f"version: {new_version}")
    print("_______________________________________________\n\n\n\n")

@tasks.loop(seconds=10)
async def change_status():
    await client.change_presence(activity=discord.Game(next(status)))



@client.command()
async def start(ctx):


    ftx = SpotFtx(
            apiKey='W7wAYAev_e3ONda3Laa2T2l5A_5Vq0EJ1zbJHbyt',
            secret='AW6eeMWh7rJ3iYK_JxHGEZ9hK1HsAgv8B8stncUt',
            subAccountName='LeLoup'
        )

    pairList = [
        'BTC/USD',
        'ETH/USD',
        'BNB/USD',
        'LTC/USD',
        'DOGE/USD',
        'XRP/USD',
        'SOL/USD',
        'AVAX/USD',
        'SHIB/USD',
        'LINK/USD',
        'UNI/USD',
        'MATIC/USD',
        'AXS/USD',
        'CRO/USD',
        'FTT/USD',
        'TRX/USD',
        'BCH/USD',
        'FTM/USD',
        'GRT/USD',
        'AAVE/USD',
        'OMG/USD',
        'SUSHI/USD',
        'MANA/USD',
        'SRM/USD',
        'RUNE/USD',
        'SAND/USD',
        'CHZ/USD',
        'CRV/USD'
    ]

    timeframe = '1h'

    # -- Indicator variable --
    aoParam1 = 6
    aoParam2 = 22
    stochWindow = 14
    willWindow = 14

    # -- Hyper parameters --
    maxOpenPosition = 3
    stochOverBought = 0.8
    stochOverSold = 0.2
    willOverSold = -85
    willOverBought = -10
    TpPct = 0.15

    while True:
        try:
            now = datetime.now()
            await ctx.send(now.strftime("%d-%m %H:%M:%S"))
            dfList = {}
            for pair in pairList:
                # print(pair)
                df = ftx.get_last_historical(pair, timeframe, 210)
                dfList[pair.replace('/USD','')] = df

            for coin in dfList:
                # -- Drop all columns we do not need --
                dfList[coin].drop(columns=dfList[coin].columns.difference(['open','high','low','close','volume']), inplace=True)

                # -- Indicators, you can edit every value --
                dfList[coin]['AO']= ta.momentum.awesome_oscillator(dfList[coin]['high'],dfList[coin]['low'],window1=aoParam1,window2=aoParam2)
                dfList[coin]['STOCH_RSI'] = ta.momentum.stochrsi(close=dfList[coin]['close'], window=stochWindow)
                dfList[coin]['WillR'] = ta.momentum.williams_r(high=dfList[coin]['high'], low=dfList[coin]['low'], close=dfList[coin]['close'], lbp=willWindow)
                dfList[coin]['EMA100'] =ta.trend.ema_indicator(close=dfList[coin]['close'], window=100)
                dfList[coin]['EMA200'] =ta.trend.ema_indicator(close=dfList[coin]['close'], window=200)

            await ctx.send("Data and Indicators loaded 100%")

            # -- Condition to BUY market --
            def buyCondition(row, previousRow=None):
                if (
                    row['AO'] >= 0
                    and previousRow['AO'] > row['AO']
                    and row['WillR'] < willOverSold
                    and row['EMA100'] > row['EMA200']
                ):
                    return True
                else:
                    return False

            # -- Condition to SELL market --
            def sellCondition(row, previousRow=None):
                if (
                    (row['AO'] < 0
                    and row['STOCH_RSI'] > stochOverSold)
                    or row['WillR'] > willOverBought
                ):
                    return True
                else:
                    return False

            coinBalance = ftx.get_all_balance()
            coinInUsd = ftx.get_all_balance_in_usd()
            usdBalance = coinBalance['USD']
            del coinBalance['USD']
            del coinInUsd['USD']
            totalBalanceInUsd = usdBalance + sum(coinInUsd.values())
            tunes = totalBalanceInUsd
            await ctx.send(f"{tunes}$")
            coinPositionList = []
            for coin in coinInUsd:
                if coinInUsd[coin] > 0.05 * totalBalanceInUsd:
                    coinPositionList.append(coin)
            openPositions = len(coinPositionList)

            #Sell
            for coin in coinPositionList:
                    if sellCondition(dfList[coin].iloc[-2], dfList[coin].iloc[-3]) == True:
                        openPositions -= 1
                        symbol = coin+'/USD'
                        cancel = ftx.cancel_all_open_order(symbol)
                        time.sleep(1)
                        sell = ftx.place_market_order(symbol,'sell',coinBalance[coin])
                        await ctx.send(cancel)
                        await ctx.send(f"Sell, {coinBalance[coin]}, {coin}, {sell}")
                    else:
                        await ctx.send(f"Keep {coin}")

            #Buy
            if openPositions < maxOpenPosition:
                for coin in dfList:
                    if coin not in coinPositionList:
                        if buyCondition(dfList[coin].iloc[-2], dfList[coin].iloc[-3]) == True and openPositions < maxOpenPosition:
                            time.sleep(1)
                            usdBalance = ftx.get_balance_of_one_coin('USD')
                            symbol = coin+'/USD'

                            buyPrice = float(ftx.convert_price_to_precision(symbol, ftx.get_bid_ask_price(symbol)['ask'])) 
                            tpPrice = float(ftx.convert_price_to_precision(symbol, buyPrice + TpPct * buyPrice))
                            buyQuantityInUsd = usdBalance * 1/(maxOpenPosition-openPositions)

                            if openPositions == maxOpenPosition - 1:
                                buyQuantityInUsd = 0.95 * buyQuantityInUsd

                            buyAmount = ftx.convert_amount_to_precision(symbol, buyQuantityInUsd/buyPrice)

                            buy = ftx.place_market_order(symbol,'buy',buyAmount)
                            time.sleep(2)
                            tp = ftx.place_limit_order(symbol,'sell',buyAmount,tpPrice)
                            try:
                                tp["id"]
                            except:
                                time.sleep(2)
                                tp = ftx.place_limit_order(symbol,'sell',buyAmount,tpPrice)
                                pass
                            await ctx.send(f"Buy {buyAmount}, {coin} at {buyPrice}, {buy}")
                            await ctx.send(f"Place, {buyAmount}, {coin}, TP at, {tpPrice}, {tp}")

                            openPositions += 1

                    else:
                        await ctx.send("no opportunity")
            else:
                await ctx.send("hold on")

            await ctx.send(".\n.")
            time.sleep(60)

        except Exception as e:
            await ctx.send(f"Error: {e}")
            await ctx.send("_\n_")
            continue


"""
@client.event
async def on_message(message):
    author = message.author
    content = message.content
    guild = str(message.guild)
    channel = message.channel
    date = message.created_at
    global js


    fichier = os.listdir()
    if guild + ".json" not in fichier:
        with open(f"test.json", "r") as lol:
            js = json.load(lol)
        with open(f"{guild}.json","w") as fd:
            fd.dump(js, fd, indent=2)

    with open(f"{guild}.json","r") as fd:
        js = json.load(fd)

    js[channel][len(js[channel])] = {"author": author, "content": content, "date": date}
    print(js)
    with open(f"{guild}.json", "w") as fd:
        json.dump(js, fd, indent=2)
"""
@client.event
async def on_error(event, *args, **kwargs): #enregistre l'erreur
    with open("./errors.log","w+") as err:
        err.write(f"""{args[0]}\n""")
        log = err.read()
        print(log)

client.run(token)