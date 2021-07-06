import websocket, pprint, json, talib, numpy, binance, config
from binance.enums import *
from binance.client import Client

client = Client(config.API_KEY, config.API_SECRET)

WEBSOCKET_URL = "wss://stream.binance.com:9443/ws/dogeusdt@kline_1m"
RSI_PERIOD = 14
RSI_OVERBOUGHT = 70
RSI_OVERSOLD = 30
QUANTITY = 50
TOKEN_PAIR = "DOGEUSDT"

closes = []
already_bought = False
last_bought_price = 10000000

def order(action):
    try:
        print("sending order")
        neworder = client.create_order(
        symbol=TOKEN_PAIR,
        side=action,
        type=ORDER_TYPE_MARKET,
        quantity=QUANTITY)
        print(neworder)
        return True
    except Exception as e:
        print("exception occured {}".format(e))
        return False

def on_open(ws):
    print("Connection opened...")

def on_error(ws, error):
    print(error)

def on_close(w):
    print("Connection closed...")

def on_message(ws, message):
    global closes, already_bought, last_bought_price
    message_dict = json.loads(message)
    candle = message_dict['k']
    print("Latest candle close is {}".format(candle['c']))
    if candle['x']:
        closes.append(float(candle['c']))
    
    if len(closes) > RSI_PERIOD and candle['x']:
        numpy_array = numpy.array(closes)
        rsi = talib.RSI(numpy_array, RSI_PERIOD)
        current_rsi = rsi[-1]
        print("RSI is {}".format(current_rsi))
        if current_rsi < RSI_OVERSOLD:
            print("We are oversold!! Lets try to buy")
            if not already_bought:
                neworder = order(SIDE_BUY)
                if neworder:
                    already_bought = True
                    last_bought_price = closes[-1]
                    print("last trading price was {}".format(last_bought_price))
            else:
                print("already bought")
        if current_rsi > RSI_OVERBOUGHT:
            print("We are overbought!! Lets try to sell")
            if already_bought:
                # sell only on profit
                print("Trying to sell. Last bought price {}, closed price {}, bool condition {}".format(last_bought_price, closes[-1], closes[-1] > last_bought_price))
                if closes[-1] > last_bought_price:
                    neworder = order(SIDE_SELL)
                    if neworder:
                        already_bought = False
                        last_bought_price = 10000000
                else:
                    print("We can't sell at a lower price than at what we bought")
            else:
                print("nothing to sell")

ws = websocket.WebSocketApp(WEBSOCKET_URL,
    on_open = on_open,
    on_close = on_close,
    on_message = on_message,
    on_error = on_error)

ws.run_forever()
