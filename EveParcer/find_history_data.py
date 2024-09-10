import asyncio
import json
import aiohttp

with open('names_data.json', 'r') as f:
    data = f.read()
    names_data = json.loads(data)


history_data = {}


def find_average(text):
    text = text.split('}')[-6:-1]
    total = 0
    for i in text:
        count = int(i[i.find('volume'):][8:])
        total += count
    return total // 5


async def find_item_history(session, id, name):
    url = f'https://evetycoon.com/api/v1/market/history/10000002/{id}'
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"}

    async with session.get(url=url, headers=headers) as response:
        text = await response.text()
        average = find_average(text)
        history_data[name] = average


async def get_history_data():
    async with aiohttp.ClientSession() as session:
        tasks = []
        for id in names_data:
            name = names_data[id]
            task = asyncio.create_task(find_item_history(session, id, name))
            tasks.append(task)
        await asyncio.gather(*tasks)


if __name__ == '__main__':
    asyncio.run(get_history_data())
    print(history_data)
    with open('history_data.json', 'w') as f:
        json.dump(history_data, f)
