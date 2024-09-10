import requests
from bs4 import BeautifulSoup as BS
import json

MIN_VALUE = 500000

region_names = {'10000044': ['Solitude', 30],
                '10000049': ['Khanid', 50],
                '10000043': ['Domain', 50],
                '10000001': ['Derelik', 32],
                '10000020': ['Tash-Murkon', 50],
                '10000052': ['Kador', 50],
                '10000036': ['Devoid', 40],
                '10000030': ['Heimatar', 15],
                '10000037': ['EveryShore', 15],
                '10000042': ['Metropolis', 15],
                '10000032': ['Sinq Laison', 15],
                '10000033': ['Citadel', 0],
                '10000067': ['Genesis', 20],
                '10000016': ['Lonetrek', 5],
                '10000054': ['Aridia', 60],
                '10000069': ['Black Rise', 10],
                '10000064': ['Essence', 15]}


def printtable(data):
    print('-' * 400)
    print('Регион       Прибыль     Затраты')
    for region in data:
        total_value = data[region]['total_value']
        total_price = data[region]['total_price']
        info = data[region]['info']
        region_name = region_names[region]
        print(region_name,
              ' ' * ((10 - len(str(total_value))) + (20 - len(region_name))), total_value,
              ' ' * (10 - len(str(total_price))), total_price)
        for item in info:
            print(' ' * 10, item, info[item]['total_value'], info[item]['total_price'])
            for order in info[item]['orders']:
                if order['value'] > 0:
                    print(' ' * 20, order)


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


def find_orders(id):
    url = f'https://evetycoon.com/api/v1/market/orders/{id}'
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"}
    src = requests.get(url, headers)
    text = BS(src.content, 'lxml').text

    item_name = text[text.find('Name'):]
    item_name = item_name[:item_name.find(',')][7:][:-1]

    orders = text[text.find("orders"):][9:-2]
    orders = orders.split('{')[1:]
    if not orders:
        return None

    text_systems = text[text.find('"systems"'):][:text.find('}}')][11:].split('}')[:-2]
    systems = {}
    for j in text_systems:
        key = j[j.find('3'):][:8]
        value = j[j.find('Name'):][7:]
        name = value[:value.find(',')][:-1]
        security = float(value[value.find('security'):][10:]) // 0.1 / 10
        systems[key] = [name, security]

    text_stations = text[text.find('stationNames'):]
    text_stations = text_stations[:text_stations.find('},')][15:].split(',')
    stations = {}
    for m in text_stations:
        key = m[m.find('6'):][:8]
        value = m[m.find(':'):][2:][:-1]
        stations[key] = value

    sell_orders = []
    buy_orders = []
    for i in orders:
        try:
            order = i.replace('"', ' ').strip().split(',')
            order_type = order[1][13:]
            order = {'value': 0,
                     'total_price': int(float(order[6][8:]) * int(order[11][15:])),
                     'price': float(order[6][8:]),
                     'count': int(order[11][15:]),
                     'region': order[9][11:],
                     'system': systems[order[8][11:]][0],
                     'station': stations[order[3][13:]],
                     'security': systems[order[8][11:]][1]}
            if order['security'] >= 0.5:
                if order_type == 'true':
                    if order['station'] == 'Jita IV - Moon 4 - Caldari Navy Assembly Plant':
                        sort_append(buy_orders, order, True)
                else:
                    sort_append(sell_orders, order)

        except:
            pass

    return item_name, sell_orders, buy_orders


def total_value_from_region(sell_orders, buy_orders):
    count = 0
    buy_price = 0
    for order in sell_orders:
        count += order['count']
        buy_price += order['price'] * order['count']
    value = 0
    stop = False
    while not stop:
        for buy_order in buy_orders:
            if stop:
                break
            if count > buy_order['count']:
                count -= buy_order['count']
                value += buy_order['count'] * buy_order['price']
            else:
                for _ in range(buy_order['count']):
                    count -= 1
                    value += buy_order['price']
                    if count <= 0:
                        stop = True
                        break
    return int(value - buy_price), int(buy_price)


def value_from_order(order, buy_orders):
    if len(buy_orders) == 0:
        return 0
    count = order['count']
    value = 0
    stop = False
    while not stop:
        for buy_order in buy_orders:
            if stop:
                break
            if count > buy_order['count']:
                count -= buy_order['count']
                value += buy_order['count'] * buy_order['price']
            else:
                for _ in range(buy_order['count']):
                    count -= 1
                    value += buy_order['price']
                    if count <= 0:
                        stop = True
                        break
    return int((0.92 * value) - order['total_price'])


def find_value(sell_orders, buy_orders):
    value_from_region = {
        order['region']: {'total_value': 0, 'total_price': 0, 'region_value': 0, 'orders_value': [], 'orders': []} for
        order in sell_orders}
    for order in sell_orders:
        value_from_region[order['region']]['orders'].append(order)

    for region in value_from_region:
        data = value_from_region[region]
        for order in data['orders']:
            value = value_from_order(order, buy_orders)
            if value > MIN_VALUE:
                data['orders_value'].append(value)
                order['value'] = value
            else:
                data['orders'].remove(order)
        if len(data['orders_value']) == 0:
            pass
        elif len(data['orders_value']) == 1:
            data['region_value'] = data['orders_value'][0]
            region_buy_price = data['orders'][0]['total_price']
            data['total_value'], data['total_price'] = data['region_value'], region_buy_price
        else:
            data['region_value'], region_buy_price = total_value_from_region(data['orders'], buy_orders)
            data['total_value'], data['total_price'] = max(data['orders_value']), region_buy_price

    result = {region: value_from_region[region] for region in value_from_region if
              value_from_region[region]['total_value'] > MIN_VALUE}

    for region in result:
        try:
            result[region]['orders'] = dict(sorted(result[region]['orders'], key=lambda x: x['value'], reverse=True))
        except:
            pass
    return result


def save_data_to_txt(data):
    file = open('orders.txt', 'w')
    file.write('Регион          Прибыль       Затраты')
    for region in data:
        total_value = data[region]['total_value']
        total_price = data[region]['total_price']
        info = data[region]['info']

        try:
            region_name = region_names[region][0]
            jumps = str(region_names[region][1])
        except:
            region_name = region
            jumps = '0'

        text = '\n' + region_name + ' ' + jumps + \
               ' ' * (20 - len(str(total_value)) - len(region_name)) + str(total_value) + \
               ' ' * (15 - len(str(total_price))) + str(total_price)
        file.write(text)

        for item in info:
            value = str(info[item]['total_value'])
            price = str(info[item]['total_price'])
            text2 = '\n' + ' ' * 40 + str(item) + \
                    ' ' * (25 - len(item)) + value + \
                    ' ' * 3 + price
            file.write(text2)

            for order in info[item]['orders']:
                if order['value'] > 0:
                    text3 = '\n' + ' ' * 90 + str(order)
                    file.write(text3)


def all_value(start):
    with open('valid_id.json', 'r') as f:
        data = f.read()
        data = json.loads(data)
    valid_id = data['id']

    total_value = {}
    for i in valid_id[start:]:
        print(i)
        try:
            name, sell, buy = find_orders(i)
            print(name)

            i_value = find_value(sell, buy)
            for region in i_value:
                if region in total_value:
                    total_value[region]['total_value'] += i_value[region]['total_value']
                    total_value[region]['total_price'] += i_value[region]['total_price']
                    total_value[region]['info'][name] = i_value[region]
                else:
                    total_value[region] = {'total_value': i_value[region]['total_value'],
                                           'total_price': i_value[region]['total_price'],
                                           'info': {name: i_value[region]}}

            total_value = dict(sorted(total_value.items(), key=lambda item: item[1]['total_value'], reverse=True))
            for region in total_value:
                total_value[region]['info'] = dict(
                    sorted(total_value[region]['info'].items(), key=lambda item: item[1]['total_value'],
                           reverse=True))
            # printtable(total_value)
            save_data_to_txt(total_value)
        except:
            print(i, 'Error')


all_value(0)

# name, sell, buy = find_orders(394)
# for i in buy:
#     print(i)

# i_value = find_value(sell, buy)
# for i in i_value:
#     print(i, i_value[i])
