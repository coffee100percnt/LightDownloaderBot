import re
import json
import os
import logging
import yt_dlp
from aiogram import Bot, Dispatcher, types, filters, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import InlineKeyboardMarkup as inmarkup
from aiogram.types import InlineKeyboardButton as inbutton
import localization as local

logging.basicConfig(level=logging.INFO)

API_TOKEN = "5626410964:AAFSaQJ07OHcCpY_KAGdx64OETJ1LhmLQbo"
ADMIN_ID = '1554852514'
#ADMIN_ID = '5229672176'

class Form(StatesGroup):
    nowad = State()

async def userbase_modifier_on_call(call):
    if call.data == "langen":
        f = open(f'{os.getcwd()}/users.json', 'r', 1,)
        s = json.loads(f.read())
        f.close()
        if call.from_user.id in s["en"]:pass
        else:
            try: 
                s["en"].append(call.from_user.id)
                result = json.dumps(s)
                f = open(f'{os.getcwd()}/users.json', 'w')
                f.write(result)
                f.close()
            finally:
                s["ru"].remove(call.from_user.id)
        await call.message.answer(local.welcome["en"])

    if call.data == "langru":
        f = open(f'{os.getcwd()}/users.json', 'r')
        s = json.loads(f.read())
        f.close()
        if call.from_user.id in s["ru"]:pass
        else:
            try: 
                s["ru"].append(call.from_user.id)
                result = json.dumps(s)
                f = open(f'{os.getcwd()}/users.json', 'w')
                f.write(result)
                f.close()
            finally:
                s["en"].remove(call.from_user.id)
        await call.message.answer(local.welcome["en"])

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())

class DownloadState(StatesGroup):
    waiting_for_video_url = State()

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
async def ask_for_ad(message: types.Message):
    await Form.nowad.set()
    await message.reply("Send the ad")

@dp.message_handler(state=Form.nowad, content_types=['any'])
async def select_userbase_ad(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        buttons = [inbutton(text="English", callback_data="aden"), inbutton(text="Русский", callback_data="adru")]
        keyboard_inline = inmarkup().add(buttons[0], buttons[1])
        await message.reply("Pick a userbase:", reply_markup=keyboard_inline)


@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message):
    # f = open(f'{os.getcwd()}/users.txt', 'r')
    # s = f.read().find(str(message.chat.id))
    # f.close()
    # print(message.chat.id)
    # if s != -1:
    #     pass

    # else:
    #     fi = open(f'{os.getcwd()}/users.txt', 'a')
    #     fi.write(f"{message.chat.id}\n")
    #     fi.close()
    # await message.reply("Hello! I'm a TikTok video downloader bot. Just send me a TikTok video link and I'll download it for you!")
    f = open(f'{os.getcwd()}/users.json', 'r')
    s = json.loads(f.read())
    f.close()
    if message.from_user.id in s["en"] or s["ru"]:
        if message.from_user.id in s["en"]:
            await message.reply(local.start["en"], "Markdown", None, False)
        elif message.from_user.id in s["ru"]:
            pass
    else:
        buttons = [inbutton(text="English", callback_data="langen"), inbutton(text="Русский", callback_data="langru")]
        keyboard_inline = inmarkup().add(buttons[0], buttons[1])
        await message.reply("Pick a language:", reply_markup=keyboard_inline)


@dp.message_handler()
@dp.message_handler(filters.Regexp(r'(https?://\S+)'))
async def handle_video(message: types.Message):
    video_url = re.findall(r'(https?://\S+)', message.text)
    try:   
        for i in range(len(video_url)):
            with yt_dlp.YoutubeDL({'outtmpl': '%(id)s.%(ext)s', 'cookiefile': f"{os.getcwd()}/insta.txt"}) as ydl:
                await bot.send_chat_action(message.chat.id, "upload_video")
                result = ydl.extract_info(video_url[i], download=True)
                filename = ydl.prepare_filename(result)
                await bot.send_video(chat_id=message.chat.id, video=open(filename, 'rb'), caption=f"🎥 {video_url[i]}\n\n@LightDownloaderBot")
                # asyncio.sleep(10)
                os.remove(f'{os.getcwd()}/{filename}')
    except yt_dlp.utils.DownloadError:
        await bot.send_message(message.chat.id, f"Oh no, an error occured! Please double check the link")

@dp.callback_query_handler(text=["langen", "langru"])
async def check_button_langs(call: types.CallbackQuery):
    # Checking which button is pressed and respond accordingly
    await userbase_modifier_on_call(call)
    await call.answer()
    send_welcome(message=call.message)

@dp.callback_query_handler(text=["aden", "adru"])
async def check_button_ad(call: types.CallbackQuery, state: FSMContext):
    if call.data == "aden":
        async with state.proxy() as data:
            f = open(f'{os.getcwd()}/users.json', 'r')
            s = json.loads(f.read())
            f.close()
            for i in s["en"]:
                await bot.copy_message(chat_id=i, from_chat_id=call.from_chat.id, message_id=data['nowad'].message_id)
            await call.message.answer("sent!")

    if call.data == "adru":
        async with state.proxy() as data:
            f = open(f'{os.getcwd()}/users.json', 'r')
            s = json.loads(f.read())
            f.close()
            for i in s["ru"]:
                await bot.copy_message(chat_id=i, from_chat_id=call.from_chat.id, message_id=data['nowad'].message_id)
            await call.message.answer(local.welcome["en"])
    await state.finish()

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
