import asyncio
import json


value = {}
MAX_BUY_PRICE = 300000000
MIN_VALUE_ISK = 10000000
MIN_HISTORY = 30
STATION_TO = 'Jita'

with open('history_data.json', 'r') as f:
    history_data = f.read()
    history_data = json.loads(history_data)


def load_data():
    with open('items_orders.json', 'r') as file:
        data = file.read()
        data = json.loads(data)
        return data


async def analyse(name, data):
    if data == [''] or 'Blueprint' in name:
        return 0, []
    else:
        sell = []
        buy = []
        for order in data:
            if STATION_TO in order['station']:
                sell.append(order)
            else:
                buy.append(order)
        if sell and buy:
            buy = sorted(buy, key=lambda x: x['price'])
            sell = sorted(sell, key=lambda x: x['price'])
            max_value = 0
            max_value_isk = 0
            max_value_order = None
            for order in buy:
                buy_price = order['price'] * order['count']
                sell_price = sell[0]['price'] * order['count']
                order_value = sell_price / buy_price
                order_value_isk = sell_price - buy_price
                if order_value_isk > max_value:
                    max_value = order_value
                    max_value_isk = order_value_isk
                    max_value_order = order
            if max_value_order and max_value_isk >= MIN_VALUE_ISK:
                value[name] = {'value': max_value,
                               'value_isk': max_value_isk,
                               'buy_price': max_value_order['price'] * max_value_order['count'],
                               'order': max_value_order}


async def main():
    tasks = []
    data = load_data()
    for item in data:
        task = analyse(item, data[item])
        tasks.append(task)
    await asyncio.gather(*tasks)

regions = {'10000002': 'Forge', '10000033': 'Citadel', '10000016': 'Lonetrek', '10000069': 'Black Rise', '10000042': 'Metropolis'}

if __name__ == '__main__':
    asyncio.run(main())
    value = dict(sorted(value.items(), key=lambda x: x[1]['value']))
    for name in value:
        if history_data[name] > MIN_HISTORY:
            if value[name]['buy_price'] <= MAX_BUY_PRICE:
                value_text = str(value[name]['value'] // 0.1 / 10)
                value_isk_text = str(int(value[name]['value_isk']))
                region = regions[value[name]['order']['region']]
                buy_price_text = str(int(value[name]['buy_price']))

                print(name,
                      ' ' * (60 - len(name)), value_text,
                      ' ' * (10 - len(value_text)), value_isk_text,
                      ' ' * (15 - len(value_isk_text)), buy_price_text,
                      ' ' * (15 - len(buy_price_text)), history_data[name],
                      ' ' * (15 - len(str(history_data[name]))), region,
                      ' ' * (30 - len(region)), value[name]['order']['price'],
                      ' ' * (15 - len(str(value[name]['order']['price']))), value[name]['order']['count'], )

