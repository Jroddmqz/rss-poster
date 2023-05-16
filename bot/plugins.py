import os
import asyncio
import logging
import time
import feedparser

from PIL import Image
from bot import Mclient


def resizer(_image_):
    with Image.open(_image_) as img:
        width, height = img.size
        img = img.convert("RGB")

    if width * height > 5242880 or width > 4096 or height > 4096:
        new_width, new_height = width, height
        while new_width * new_height > 5242880 or new_width > 4096 or new_height > 4096:
            new_width = int(new_width * 0.9)
            new_height = int(new_height * 0.9)

        resized_img = img.resize((new_width, new_height))
    else:
        resized_img = img

    path_, ext_ = os.path.splitext(_image_)
    newname = path_ + "lite" + ext_
    resized_img.save(newname)
    return newname


async def is_chat(client, item):
    try:
        chat_id = int(item)
        try:
            chat = await client.get_chat(chat_id)
        except:
            return None
        chat_id = chat.id
    except ValueError:
        if not item.startswith("@"):
            return None
        try:
            chat = await client.get_chat(item)
        except:
            return None
        chat_id = chat.id
    return chat_id


async def upload_file(client, file_path, chat_id, capy, ext_):
    _sent_ = None
    try:
        if ext_.lower() in {'.jpg', '.png', '.webp', '.jpeg'}:
            new_file = resizer(file_path)
            try:
                _sent_ = await client.send_photo(chat_id, photo=new_file, caption=str(capy))
                await asyncio.sleep(1)
                await client.send_document(chat_id, document=file_path)
            except:
                try:
                    _sent_ = await client.send_document(chat_id, document=file_path, caption=str(capy))
                except Exception as e:
                    logging.error("[RSSPOSTER] - Failed: " + f"{str(e)}")
            if os.path.exists(new_file):
                os.remove(new_file)
        elif ext_.lower() in {'.mp4', '.avi', '.mkv', '.mov'}:
            try:
                _sent_ = await client.send_video(chat_id, video=file_path, caption=str(capy))
                await asyncio.sleep(1)
            except:
                try:
                    _sent_ = await client.send_document(chat_id, document=file_path, caption=str(capy))
                except Exception as e:
                    logging.error("[RSSPOSTER] - Failed: " + f"{str(e)}")
        else:
            try:
                _sent_ = await client.send_document(chat_id, document=file_path, caption=str(capy))
            except Exception as e:
                logging.error("[RSSPOSTER] - Failed: " + f"{str(e)}")

        os.remove(file_path)

    except Exception as e:
        if "[420 FLOOD_WAIT_X]" in str(e):
            print(f"str(e)-{str(e)}-")
            print('Flood: Wait for', int(str(e).split()[5]), 'seconds')
            time.sleep(int(str(e).split()[5]))
        else:
            logging.error("[RSSPOSTER] - Failed: " + f"{str(e)}")


async def get_feed_entries(url):
    entries = []
    feed = feedparser.parse(url)

    for entry in feed.entries:
        try:
            entry_data = {
                "title": entry.title,
                "link": entry.link,
                "updated": entry.updated,
                "author": entry.author,
            }
            entries.append(entry_data)
        except:
            print("Error get feed entries ranked", entry)
            pass

    return entries
