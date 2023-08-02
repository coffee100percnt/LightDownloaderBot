import re
import json
import os
import logging
import yt_dlp
from aiogram import Bot, Dispatcher, types, filters, executor, utils
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import InlineKeyboardMarkup as inmarkup
from aiogram.types import InlineKeyboardButton as inbutton
import localization as local
from contextlib import suppress


logging.basicConfig(level=logging.INFO)
API_TOKEN = "5626410964:AAFSaQJ07OHcCpY_KAGdx64OETJ1LhmLQbo"
ADMIN_ID = '1554852514'
#ADMIN_ID = '5229672176'
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())

#region Forms
class Form(StatesGroup):
    nowad = State()
class DownloadState(StatesGroup):
    waiting_for_video_url = State()
#endregion

#region Userbase tools
def search_userbase(base, id):
    if id in base["en"]:
        return "en"
    elif id in base["ru"]:
        return "ru"
    elif id in base["ua"]:
        return "ua"
    else:
        return False

async def userbase_modifier_on_call(call):
    if call.data == "langen":
        file = open(f'{os.getcwd()}/users.json', 'r', 1)
        userbase = json.loads(file.read())
        file.close()
        if search_userbase(userbase, call.from_user.id) == "en":pass
        elif search_userbase(userbase, call.from_user.id) == "ru":
            userbase["ru"].remove(call.from_user.id)
            userbase["en"].append(call.from_user.id)
            wrtu(userbase)
        elif search_userbase(userbase, call.from_user.id) == "ua":
            userbase["ua"].remove(call.from_user.id)
            userbase["en"].append(call.from_user.id)
            wrtu(userbase)
        else:
            userbase["en"].append(call.from_user.id)
            wrtu(userbase)
        await call.message.answer(local.welcome["en"])

    if call.data == "langru":
        file = open(f'{os.getcwd()}/users.json', 'r', 1)
        userbase = json.loads(file.read())
        file.close()
        if search_userbase(userbase, call.from_user.id) == "ru":pass
        elif search_userbase(userbase, call.from_user.id) == "en":
            userbase["en"].remove(call.from_user.id)
            userbase["ru"].append(call.from_user.id)
            wrtu(userbase)
        elif search_userbase(userbase, call.from_user.id) == "ua":
            userbase["ua"].remove(call.from_user.id)
            userbase["ru"].append(call.from_user.id)
            wrtu(userbase)
        else:
            userbase["ru"].append(call.from_user.id)
            wrtu(userbase)
        await call.message.answer(local.welcome["ru"])
        
        if call.data == "langua":
            file = open(f'{os.getcwd()}/users.json', 'r', 1)
            userbase = json.loads(file.read())
            file.close()
            if search_userbase(userbase, call.from_user.id) == "ua":pass
            elif search_userbase(userbase, call.from_user.id) == "ru":
                userbase["ru"].remove(call.from_user.id)
                userbase["ua"].append(call.from_user.id)
                wrtu(userbase)
            elif search_userbase(userbase, call.from_user.id) == "en":
                userbase["en"].remove(call.from_user.id)
                userbase["ua"].append(call.from_user.id)
                wrtu(userbase)
            else:
                userbase["ua"].append(call.from_user.id)
                wrtu(userbase)
            await call.message.answer(local.welcome["ua"])

def wrtu(userbase):
    result = json.dumps(userbase)
    file = open(f'{os.getcwd()}/users.json', 'w')
    file.write(result)
    file.close()
#endregion

#region Message handlers
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
    file = open(f'{os.getcwd()}/users.json', 'r')
    userbase = json.loads(file.read())
    file.close()
    with search_userbase(userbase, message.from_user.id) as sdb:
        if isinstance(sdb, str):
            await message.reply(local.start[sdb], "Markdown", None, False)
        else:
            buttons = [inbutton(text="English", callback_data="langen"),
                       inbutton(text="Русский", callback_data="langru"),
                       inbutton(text="Українська", callback_data="langua")]
            keyboard_inline = inmarkup().add(buttons[0], buttons[1])
            await message.reply("Pick a language:", reply_markup=keyboard_inline)

@dp.message_handler(filters.Regexp(r'(https?://\S+)'))
async def handle_video(message: types.Message):
    video_url = re.findall(r'(https?://\S+)', message.text)
    try:   
        for i in range(len(video_url)):
            with yt_dlp.YoutubeDL({'outtmpl': '%(id)s{0}.%(ext)s', 'cookiefile': f"{os.getcwd()}/insta.txt", "format": "mp4"}) as ydl:
                await bot.send_chat_action(message.chat.id, "upload_video")
                result = ydl.extract_info(video_url[i], download=True)
                videoname = ydl.prepare_filename(result)
                filename = videoname.format(message.chat.id)
                os.rename(videoname, filename)
                with suppress(utils.exceptions.BotBlocked):
                    if os.path.getsize(filename) <= 50000000:await bot.send_video(chat_id=message.chat.id, video=open(filename, 'rb'), caption=f"🎥 {video_url[i]}\n\n@LightDownloaderBot")
                    elif os.path.getsize(filename) > 50000000:
                        await bot.send_message(message.chat.id, f"The video too big in size!")
                    
                # asyncio.sleep(10)
                os.remove(f'{os.getcwd()}/{filename}')
    except yt_dlp.utils.DownloadError:
        await bot.send_message(message.chat.id, f"Oh no, an error occured! Please double check the link or report this error with the link to @lightdownload_feedback_bot")

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
            file = open(f'{os.getcwd()}/users.json', 'r')
            userbase = json.loads(file.read())
            file.close()
            for i in userbase["en"]:
                await bot.copy_message(chat_id=i, from_chat_id=call.from_chat.id, message_id=data['nowad'].message_id)
            await call.message.answer("sent!")

    if call.data == "adru":
        async with state.proxy() as data:
            file = open(f'{os.getcwd()}/users.json', 'r')
            userbase = json.loads(file.read())
            file.close()
            for i in userbase["ru"]:
                await bot.copy_message(chat_id=i, from_chat_id=call.from_chat.id, message_id=data['nowad'].message_id)
            await call.message.answer(local.welcome["en"])
    await state.finish()
#endregion

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
