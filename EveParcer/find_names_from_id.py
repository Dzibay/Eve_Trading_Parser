import asyncio
import json
import aiohttp

with open('valid_id.json', 'r') as f:
    data = f.read()
    ids = json.loads(data)


names_data = {}


def find_name(text):
    text = text[:200]
    text = text[text.find('Name'):][7:]
    text = text[:text.find(',')][:-1]
    return text


async def find_item_history(session, id):
    url = f'https://evetycoon.com/api/v1/market/orders/{id}'
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"}

    async with session.get(url=url, headers=headers) as response:
        text = await response.text()
        names_data[id] = find_name(text)


async def get_names_data():
    async with aiohttp.ClientSession() as session:
        tasks = []
        for id in ids:
            task = asyncio.create_task(find_item_history(session, id))
            tasks.append(task)
        await asyncio.gather(*tasks)

if __name__ == '__main__':
    asyncio.run(get_names_data())
    print(names_data)
    with open('names_data.json', 'w') as f:
        json.dump(names_data, f)
