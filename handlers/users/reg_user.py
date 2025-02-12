# can be used later to add phone numbers of the users later

from aiogram import types, Router
import json  # added import for JSON handling
from filters import IsNotRegistered, IsUser
from loader import db
from keyboards.inline import mand_chans
from utils.yau import notsubbed, get_external_links

reger = Router()

reger.message.filter(IsNotRegistered(), IsUser())

@reger.message()
async def process_command(message: types.Message) -> None:
    db.query("INSERT INTO users (userid, fullname, username) VALUES (?, ?, ?)", (message.from_user.id, message.from_user.full_name, message.from_user.username))

    # Get starting message similar to notsub.py
    setting = db.get_message_setting("start_msg")
    if setting:
        msg_data = json.loads(setting[0])
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
        response = f"👋 Heyy, <b>{message.from_user.first_name}</b>."
        await message.answer(response, reply_markup=types.ReplyKeyboardRemove())
    
    # Check subscription status and send further instructions
    channels = await notsubbed(message.from_user.id)
    if channels:
        response = "\n\n❕ You need to join the following chats to be able to use me."
        await message.answer(response, reply_markup=mand_chans(channels, get_external_links()))
    else:
        await message.answer("🎉 You are now registered!")