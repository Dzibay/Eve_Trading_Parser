import requests
from bs4 import BeautifulSoup as BS
import json


def find_id():
    url = f'https://evetycoon.com/api/v1/market/groups'
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"}
    src = requests.get(url, headers)
    text = BS(src.content, 'lxml').text
    groups = text.split('}')[:-1]

    new_id = []
    j = 0
    for group in groups:
        j+=1
        if 'parent' in group:
            group = group[18:]
            group_id = group[:group.find(',')]
            print(group_id, f'     {j} / {len(groups)}')

            url = f'https://evetycoon.com/api/v1/market/groups/{group_id}/types'
            data = requests.get(url, headers)
            data = BS(data.content, 'lxml').text

            if len(data) > 20:
                data = data.split('}')[:-1]
                for i in data:
                    id = i[11:]
                    id = int(id[:id.find(',')])
                    new_id.append(id)

    with open('valid_id.json', 'w') as f:
        json.dump(new_id, f)


def sort_array():
    with open('valid_id.json', 'r') as f:
        data = json.load(f)
    data = sorted(data)

    with open('valid_id.json', 'w') as f:
        json.dump(data, f)


def remove_blueprints():
    with open('valid_id.json', 'r') as f:
        data = json.load(f)

    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"}
    for i in data['id']:
        print(i)
        url = f'https://evetycoon.com/api/v1/market/orders/{i}'

        src = requests.get(url, headers)
        text = BS(src.content, 'lxml').text
        text = text[:150]
        if 'Blueprint' in text:
            print(text)


# sort_array()
with open('item_orders_data.json', 'r') as f:
    data = json.load(f)
    print(len(data))



