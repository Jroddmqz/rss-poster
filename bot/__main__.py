import asyncio
import logging
import os
import random
import string
from datetime import datetime

import requests

from bot import bot, Mclient, log_group
from bot.plugins import is_chat, upload_file, get_feed_entries
from bot.san import Bruteforce
from input import rss

temp = '.temp/'
if not os.path.exists(temp):
    os.makedirs(temp)

db = Mclient["rss"]


async def process(_item_):
    _url = _item_['rss_url']
    _chat_id = await is_chat(bot, _item_['channel'])
    _caption = _item_['caption']
    collection = db[f"{_chat_id}"]

    b = Bruteforce()

    entries = []
    entries_temp = await get_feed_entries(_url)
    for x in entries_temp:
        try:
            item = {"title": x['title'], "link": x['link'], "updated": x['updated'], "author": x['author']}
            exist = collection.find_one({"link": x["link"]})
            if not exist:
                collection.insert_one(item)
                entries.append(x)
        except Exception as e:
            logging.error("[RSSPOSTER] -1 Failed: " + f"{str(e)}")
            continue
    inverted_entries = entries[::-1]
    for entry in inverted_entries:
        capy = f"{entry['title']}\n{_caption}"
        try:
            if 'danbooru' in entry['link']:
                archive = b.danbooru(entry['link'])
            elif 'lolibooru' in entry['link']:
                archive = b.booru(entry['link'], site="lolibooru")
                archive = archive.replace(" ", "%20")
            elif 'konachan' in entry['link']:
                archive = b.konachan(entry['link'])
                archive = archive.replace(" ", "%20")
            elif 'yande.re' in entry['link']:
                archive = b.booru(entry['link'], site='yandere')
            elif 'allthefallen' in entry['link']:
                archive = b.booru(entry['link'], site='allthefallen')
            elif 'rule34' in entry['link']:
                archive = b.booru(entry['link'], site='rule34')
                capy = ""
            else:
                continue
        except Exception as e:
            logging.error("[RSsPOSTER] -2 Failed: " + f"{str(e)}")
            continue

        response = requests.get(archive)
        if response.status_code == 200:
            # filename = os.path.basename(archive)
            path_, ext_ = os.path.splitext(archive)
            now = datetime.now()
            date_time = now.strftime("%y%m%d_%H%M%S")
            random_chars = ''.join(random.choices(string.ascii_letters + string.digits, k=2))
            filename = f"{date_time}{random_chars}{ext_}"
            with open(os.path.join(temp, filename), "wb") as f:
                f.write(response.content)
            file_path = f"{temp}{filename}"

            await upload_file(bot, file_path, _chat_id, capy, ext_)
        else:
            print("Error al descargar la imagen.")


async def run():
    ruta_actual = os.getcwd()
    print(ruta_actual)

    await bot.start()
    bot.me = await bot.get_me()

    now_ = datetime.now()
    date_time = now_.strftime("%y%m%d %H.%M.%S")

    regi = f"`{date_time} - Ejecutando rss:`"
    for r in rss:
        regi = regi + f"\n`{r['rss_url']}` "
    await bot.send_message(log_group, regi)

    while True:
        tasks = [asyncio.create_task(process(rule)) for rule in rss]
        await asyncio.gather(*tasks)
        await asyncio.sleep(60)
    # await pyrogram.idle()


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    bot.loop.run_until_complete(run())
