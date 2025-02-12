import json
from aiogram import Router, types
from aiogram.filters import Command
from filters import IsUser, IsUserCallback, IsNotSubscriber, IsNotSubscriberCallback, CbData
from keyboards.inline import mand_chans
from loader import db
from utils.yau import notsubbed, get_external_links
from time import sleep

nosub = Router()

nosub.message.filter(IsUser(), IsNotSubscriber())
nosub.callback_query.filter(IsUserCallback(), IsNotSubscriberCallback())

@nosub.message(Command("help"))
async def helpme(message: types.Message) -> None:
    response = "📚 Here is the help section. You can send a message only once!"
    await message.answer(response)

@nosub.message()
async def nuhuh(message: types.Message) -> None:
    # Remove any reply markup; get stored start message if exists
    setting = db.get_message_setting("start_msg")
    if setting:
        msg_data = json.loads(setting[0])
        # Send corresponding media without markup
        if msg_data["type"] == "text":
            await message.answer(msg_data["content"], reply_markup=types.ReplyKeyboardRemove())
        elif msg_data["type"] == "photo":
            await message.answer_photo(photo=msg_data["file_id"], caption=msg_data.get("caption", ""), reply_markup=types.ReplyKeyboardRemove())
        elif msg_data["type"] == "video":
            await message.answer_video(video=msg_data["file_id"], caption=msg_data.get("caption", ""), reply_markup=types.ReplyKeyboardRemove())
        elif msg_data["type"] == "document":
            await message.answer_document(document=msg_data["file_id"], caption=msg_data.get("caption", ""), reply_markup=types.ReplyKeyboardRemove())
        elif msg_data["type"] == "animation":
            await message.answer_animation(animation=msg_data["file_id"], caption=msg_data.get("caption", ""), reply_markup=types.ReplyKeyboardRemove())
    else:
        await message.answer("❗️ You need to join the following chats to be able to use me.", reply_markup=types.ReplyKeyboardRemove())
    response = "After joining all the chats provided, press the button below."
    channels = await notsubbed(message.from_user.id)
    if channels:
        await message.answer(response, reply_markup=mand_chans(channels, get_external_links()))
    else:
        await message.answer("Thanks for joining the chats! You are now registered!")


@nosub.callback_query()
async def nuhuh(callback: types.CallbackQuery) -> None:
    setting = db.get_message_setting("start_msg")
    if setting:
        msg_data = json.loads(setting[0])
        # Send corresponding media without markup
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
        await callback.message.answer("❗️ You need to join the following chats to be able to use me.", reply_markup=types.ReplyKeyboardRemove())
    response = "After joining all the chats provided, press the button below."
    channels = await notsubbed(callback.from_user.id)
    if channels:
        await callback.message.answer(response, reply_markup=mand_chans(channels, get_external_links()))
    else:
        await callback.message.answer("Thanks for joining the chats! You are now registered!")

# @nosub.callback_query(CbData("check_subs_2"))
# async def check_subs_2(callback: types.CallbackQuery) -> None:
#     db.query("UPDATE users SET subscribed = 1 WHERE userid = ?", (callback.from_user.id,))
#     setting = db.get_message_setting("success_msg")
#     if setting:
#         msg_data = json.loads(setting[0])
#         if msg_data["type"] == "text":
#             await callback.message.answer(msg_data["content"], reply_markup=types.ReplyKeyboardRemove())
#         elif msg_data["type"] == "photo":
#             await callback.message.answer_photo(photo=msg_data["file_id"], caption=msg_data.get("caption", ""), reply_markup=types.ReplyKeyboardRemove())
#         elif msg_data["type"] == "video":
#             await callback.message.answer_video(video=msg_data["file_id"], caption=msg_data.get("caption", ""), reply_markup=types.ReplyKeyboardRemove())
#         elif msg_data["type"] == "document":
#             await callback.message.answer_document(document=msg_data["file_id"], caption=msg_data.get("caption", ""), reply_markup=types.ReplyKeyboardRemove())
#         elif msg_data["type"] == "animation":
#             await callback.message.answer_animation(animation=msg_data["file_id"], caption=msg_data.get("caption", ""), reply_markup=types.ReplyKeyboardRemove())
#     else:
#         await callback.message.answer("Thanks for joining the chats! You are now registered.", reply_markup=types.ReplyKeyboardRemove())
#     await callback.message.delete()