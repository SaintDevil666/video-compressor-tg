#!/usr/bin/python
# -*- coding: utf8 -*-
import config
import os
import sys
import requests
import random
from aiogram import Bot
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from aiogram.contrib.middlewares.logging import LoggingMiddleware

bot = Bot(config.TOKEN)
dp = Dispatcher(bot)
dp.middleware.setup(LoggingMiddleware())

os.system("mkdir videos animations")


class ErrorLogs(object):
    errs = []

    def flush(self):
        requests.post("https://api.telegram.org/bot" + config.TOKEN + "/sendMessage",
                      {"chat_id": 448741268, "text": "".join(self.errs)})
        self.errs = []

    def write(self, data):
        self.errs.append(str(data))


sys.stderr = ErrorLogs()


@dp.message_handler(commands=["compress"])
async def compress(message):
    if message.reply_to_message:
        if message.reply_to_message.video:
            file_id = message.reply_to_message.video.file_id
        elif message.reply_to_message.animation:
            file_id = message.reply_to_message.animation.file_id
        else:
            await bot.send_message(message.chat.id, "Ответь командой на видео или гифку!",
                                   reply_to_message_id=message.message_id)
            return
        text_split = message.text.split(" ")
        if len(text_split) == 2:
            try:
                level = int(text_split[1])
            except:
                await bot.send_message(message.chat.id, "Укажи аргументом целое число!",
                                       reply_to_message_id=message.message_id)
                return
        else:
            level = 5
        path = await download_file(file_id)
        new_path = "videos/r" + str(random.randrange(1000)) + ".mp4"
        os.system("ffmpeg -loglevel panic -i " + path + " -vf \"scale=trunc(iw/" + str(level * 2) + ")*2:trunc(ih/" + str(level*2) + ")*2\" " + new_path)
        await bot.send_video(message.chat.id, video=open(new_path, 'rb'))
        try:
            os.remove(path)
            os.remove(new_path)
        except:
            pass
    else:
        await bot.send_message(message.chat.id, "Ответь командой на видео или гифку!",
                               reply_to_message_id=message.message_id)


async def download_file(file_id):
    path = (await bot.get_file(file_id)).file_path
    url = "https://api.telegram.org/file/bot" + config.TOKEN + "/" + path
    os.system("touch " + path)
    open(path, "wb").write(requests.get(url).content)
    return path


executor.start_polling(dp)
