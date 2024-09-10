import json
import asyncio
import aiohttp
import time

with open('valid_id.json', 'r') as f:
    data = f.read()
    ids = json.loads(data)

items_data = {}


def sort_append(array, item, inverse=False):
    if not inverse:
        a = False
        for i in range(len(array)):
            if item['price'] < array[i]['price']:
                array.insert(i, item)
                a = True
                break
        if not a:
            array.append(item)
    else:
        a = False
        for i in range(len(array)):
            if item['price'] > array[i]['price']:
                array.insert(i, item)
                a = True
                break
        if not a:
            array.append(item)


def find_orders(text):
    item_name = text[text.find('Name'):]
    item_name = item_name[:item_name.find(',')][7:][:-1]

    orders = text[text.find("orders"):][9:-2]
    orders = orders.split('{')[1:]
    if not orders:
        return item_name, [], []

    text_systems = text[text.find('"systems"'):][:text.find('}}')][11:].split('}')[:-2]
    systems = {}
    for j in text_systems:
        try:
            key = j[j.find('3'):][:8]
            value = j[j.find('Name'):][7:]
            name = value[:value.find(',')][:-1]
            security = float(value[value.find('security'):][10:]) // 0.1 / 10
            systems[key] = [name, security]
        except:
            pass

    text_stations = text[text.find('stationNames'):]
    text_stations = text_stations[:text_stations.find('},')][15:].split(',')
    stations = {}
    for m in text_stations:
        key = m[m.find('6'):][:8]
        value = m[m.find(':'):][2:][:-1]
        stations[key] = value

    sell_orders = []
    for i in orders:
        try:
            order = i.replace('"', ' ').strip().split(',')
            order_type = order[1][13:]
            if order_type == 'false':
                order = {'value': 0,
                         'total_price': int(float(order[6][8:]) * int(order[11][15:])),
                         'price': float(order[6][8:]),
                         'count': int(order[11][15:]),
                         'region': order[9][11:],
                         'system': systems[order[8][11:]][0],
                         'station': stations[order[3][13:]],
                         'security': systems[order[8][11:]][1]}
                if order['region'] in ['10000002', '10000033', '10000016', '10000069', '10000042']:
                    sort_append(sell_orders, order)
        except:
            pass

    return item_name, sell_orders


async def get_async_item_data(session, id):
    url = f'https://evetycoon.com/api/v1/market/orders/{id}'
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"}

    async with session.get(url=url, headers=headers) as response:
        text = await response.text()
        try:
            name, sell_orders = find_orders(text)
            items_data[name] = sell_orders
            print(id, name)
        except:
            pass


async def get_data():
    async with aiohttp.ClientSession() as session:
        tasks = []
        for i in ids:
            task = asyncio.create_task(get_async_item_data(session, i))
            tasks.append(task)
        await asyncio.gather(*tasks)


if __name__ == '__main__':
    start = time.time()
    asyncio.run(get_data())
    end = time.time()
    print(end - start)
    with open('items_orders.json', 'w') as file:
        json.dump(items_data, file)



