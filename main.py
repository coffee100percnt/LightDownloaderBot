import asyncio
import os
import logging
import yt_dlp
import time
import re

from aiogram import Bot, Dispatcher, types, filters, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ParseMode
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

logging.basicConfig(level=logging.INFO)

API_TOKEN = '5626410964:AAFSaQJ07OHcCpY_KAGdx64OETJ1LhmLQbo'
ADMIN_ID = '1554852514'
#ADMIN_ID = '5229672176'
todays_ad = ""

class Form(StatesGroup):
    todayad = State()
    nowad = State()
    ays = State()

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())

class DownloadState(StatesGroup):
    waiting_for_video_url = State()

@dp.message_handler(filters.builtin.IDFilter(ADMIN_ID), commands=['comexec'])
async def command(message: types.Message):
    x = message.text.split()
    x.pop(0)
    a = ""
    for i in x:
        a = a + i + " "
    exec(a)

@dp.message_handler(state='*', commands=['cancel'])
async def cancel_handler(message: types.Message, state: FSMContext):
    """Allow user to cancel action via /cancel command"""

    current_state = await state.get_state()
    if current_state is None:
        # User is not in any state, ignoring
        return

    # Cancel state and inform user about it
    await state.finish()
    await message.reply('Cancelled.')

@dp.message_handler(filters.builtin.IDFilter(ADMIN_ID), commands=['send_ad'])
async def show_stats(message: types.Message):
    await Form.nowad.set()
    await message.reply("Send the ad")

@dp.message_handler(state=Form.nowad, content_types=['any'])
async def process_name(message: types.Message, state: FSMContext):
    await Form.next()
    async with state.proxy() as data:
        data['nowad'] = message
        await bot.copy_message(chat_id=message.chat.id, from_chat_id=message.chat.id, message_id=data['nowad'].message_id)
        await bot.send_message(message.chat.id, f"Are you sure you want to send this? (y/n)")
@dp.message_handler(state=Form.ays)
async def process(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        print(data)
        if message.text == "y":
            await message.reply("OK, sending...")
            f = open("users.txt")
            for i in f.read().split("\n"):
                await bot.copy_message(chat_id=i, from_chat_id=message.chat.id, message_id=data['nowad'].message_id)
            await bot.send_message(message.chat.id, "Sent!")
        else:
            await message.reply('OK, I won\'t send anything')
    await state.finish()

@dp.message_handler(filters.builtin.IDFilter(ADMIN_ID), commands=['set_ad'])
async def show_stats(message: types.Message):
    await Form.todayad.set()
    await message.reply("Send ad's text")

@dp.message_handler(state=Form.todayad)
async def process_name(message: types.Message, state: FSMContext):
    await state.finish()
    todays_ad = message.text
    await message.reply(f"Ok, I've set the ad text to {message.text}")


@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message):
    f = open(f'{os.getcwd()}/users.txt', 'r')
    s = f.read().find(str(message.chat.id))
    f.close()
    print(message.chat.id)
    if s != -1:
        pass

    else:
        fi = open(f'{os.getcwd()}/users.txt', 'a')
        fi.write(f"{message.chat.id}\n")
        fi.close()
    await message.reply("Hello! I'm a TikTok video downloader bot. Just send me a TikTok video link and I'll download it for you!")

@dp.message_handler(filters.Regexp(r'(https?://\S+)'))
async def handle_tiktok_video(message: types.Message):
    video_url = re.findall(r'(https?://\S+)', message.text)

    # Download the video using yt-dlp
    for i in range(len(video_url)):
        with yt_dlp.YoutubeDL({'outtmpl': '%(id)s.%(ext)s'}) as ydl:
            await bot.send_chat_action(message.chat.id, "upload_video")
            result = ydl.extract_info(video_url[i], download=True)
            filename = ydl.prepare_filename(result)
            await bot.send_video(chat_id=message.chat.id, video=open(filename, 'rb'), caption=f"🎥 {video_url[i]}\n\n@LightDownloaderBot")
            os.remove(f'{os.getcwd()}/{filename}')

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
