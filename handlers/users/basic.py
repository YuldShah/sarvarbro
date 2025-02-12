import json
from aiogram import Router, types, F
from data import config, dict
from filters import IsUser, IsUserCallback, IsSubscriber, IsSubscriberCallback, CbData
from aiogram.filters import CommandStart, Command
from keyboards.keyb import user_markup
from keyboards.inline import mand_chans
from aiogram.fsm.context import FSMContext
from loader import db
from time import sleep
from utils.yau import notsubbed, get_external_links

user = Router()


user.message.filter(IsUser(), IsSubscriber())
user.callback_query.filter(IsUserCallback(), IsSubscriberCallback())

@user.message(CommandStart())
@user.message(F.text == dict.main_menu)
async def welcome(message: types.Message, state: FSMContext) -> None:
    await state.clear()
    print(message.from_user.mention_html)
    # alr = db.fetchone("SELECT * FROM users WHERE userid=?", (message.from_user.id,))
    # conv = db.fetchone("SELECT COUNT(idx) FROM chats WHERE userid=?", (message.from_user.id,))[0]
    response = f"👋 Salom, <b>{message.from_user.mention_html()}</b>. Botga xush kelibsiz!"
    await message.answer(response, reply_markup=user_markup)

@user.callback_query(CbData("main_menu"))
async def main_menu(callback: types.CallbackQuery) -> None:
    await callback.message.answer("Main menu", reply_markup=user_markup)
    await callback.message.delete()

@user.message(Command("help"))
@user.message(F.text == dict.help_txt)
async def helpme(message: types.Message, state: FSMContext) -> None:
    await state.clear()
    response = f"📚 Here is the help section."
    await message.answer(response)

@user.callback_query(CbData("check_subs_2"))
async def check_subs(callback: types.CallbackQuery) -> None:
    setting = db.get_message_setting("success_msg")
    if setting:
        msg_data = json.loads(setting[0])
        if msg_data["type"] == "text":
            await callback.message.answer(msg_data["content"], reply_markup=types.ReplyKeyboardRemove())
        elif msg_data["type"] == "photo":
            await callback.message.answer_photo(photo=msg_data["file_id"], caption=msg_data.get("caption", ""), reply_markup=types.ReplyKeyboardRemove())
        elif msg_data["type"] == "video":
            await callback.message.answer_video(video=msg_data["file_id"], caption=msg_data.get("caption", ""), reply_markup=types.ReplyKeyboardRemove())
        elif msg_data["type"] == "document":
            await callback.message.answer_document(document=msg_data["file_id"], caption=msg_data.get("caption", ""), reply_markup=types.ReplyKeyboardRemove())
        elif msg_data["type"] == "animation":
            await callback.message.answer_animation(animation=msg_data["file_id"], caption=msg_data.get("caption", ""), reply_markup=types.ReplyKeyboardRemove())
    else:
        await callback.message.answer("Thanks for joining the chats! You are now registered and can use all the functionalities of the bot!", reply_markup=types.ReplyKeyboardRemove())
    await callback.message.delete()

@user.callback_query(CbData("check_subs"))
async def check_subs(callback: types.CallbackQuery) -> None:
    channels = await notsubbed(callback.from_user.id)
    externals = get_external_links()
    response = "We have checked and you are not subscribed to the following required links:"
    kb = mand_chans(channels, externals)
    if not channels:
        for row in kb.inline_keyboard:
            for btn in row:
                btn.callback_data = "check_subs_1"
    try:
        await callback.message.edit_text(response, reply_markup=kb)
    except Exception as e:
        await callback.answer("Dont spam buttons")
        msg = await callback.message.answer("Don't spam buttons")    
        sleep(2)
        await msg.delete()

@user.callback_query(CbData("check_subs_1"))
async def check_subs_1(callback: types.CallbackQuery) -> None:
    channels = await notsubbed(callback.from_user.id)
    if channels:
        response = "We have checked again and you are still not subscribed to all required links."
        kb = mand_chans(channels, get_external_links())
        for row in kb.inline_keyboard:
            for btn in row:
                btn.callback_data = "check_subs_2"
        await callback.message.edit_text(response, reply_markup=kb)
        await callback.answer()
    else:
        db.query("UPDATE users SET subscribed = 1 WHERE userid = ?", (callback.from_user.id,))
        setting = db.get_message_setting("success_msg")
        if setting:
            msg_data = json.loads(setting[0])
            if msg_data["type"] == "text":
                await callback.message.answer(msg_data["content"], reply_markup=types.ReplyKeyboardRemove())
            elif msg_data["type"] == "photo":
                await callback.message.answer_photo(photo=msg_data["file_id"], caption=msg_data.get("caption", ""), reply_markup=types.ReplyKeyboardRemove())
            elif msg_data["type"] == "video":
                await callback.message.answer_video(video=msg_data["file_id"], caption=msg_data.get("caption", ""), reply_markup=types.ReplyKeyboardRemove())
            elif msg_data["type"] == "document":
                await callback.message.answer_document(document=msg_data["file_id"], caption=msg_data.get("caption", ""), reply_markup=types.ReplyKeyboardRemove())
            elif msg_data["type"] == "animation":
                await callback.message.answer_animation(animation=msg_data["file_id"], caption=msg_data.get("caption", ""), reply_markup=types.ReplyKeyboardRemove())
        else:
            await callback.message.answer("Thanks for joining the chats! You are now registered.", reply_markup=types.ReplyKeyboardRemove())
        await callback.message.delete()