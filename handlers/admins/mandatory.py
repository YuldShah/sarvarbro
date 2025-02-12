import re
from aiogram import Router, types, F
from filters import IsAdmin, IsAdminCallback, CbData, CbDataStartsWith
from data import dict, config
from aiogram.fsm.context import FSMContext
from states import mands, dels
from keyboards.inline import mandconfirm
from keyboards.keyb import back_key, adm_default, main_key
from .basic import pmands
from loader import bot, db
from aiogram import html
from time import sleep

mad = Router()

mad.message.filter(IsAdmin())
# mad.callback_query.filter(IsAdminCallback)

@mad.callback_query(CbData("add_chat"))
async def add_chat(callback: types.CallbackQuery, state: FSMContext) -> None:
    await state.set_state(mands.title)
    await callback.message.answer("Send the title of the chat to add", reply_markup=back_key)
    await callback.message.delete()

@mad.message(mands.title, F.text == dict.back)
async def back_to_main(message: types.Message, state: FSMContext) -> None:
    # msg = await message.reply(f"Back to menu: {dict.mands}", reply_markup=main_key)
    await pmands(message, state)

@mad.message(mands.title)
async def add_chat_title(message: types.Message, state: FSMContext) -> None:
    await state.update_data(title=message.text)
    await state.set_state(mands.link)
    await message.answer("Send the link of the chat to add in one of the following formats:\n\t\tUsername: <code>username</code>\n\t\tUsername with @: <code>@username</code>\n\t\tPublic link: <code>https://t.me/username</code>\n\t\tExternal link: <code>https://instagram.com/username</code> or <code>https://youtube.com/channel/username</code>\n\nOr forward a message from the chat to here (Better for private chats)", reply_markup=back_key)

@mad.message(mands.link, F.text == dict.back)
async def back_to_title(message: types.Message, state: FSMContext) -> None:
    await state.set_state(mands.title)
    await message.answer("Now send the right title", reply_markup=back_key)

@mad.message(mands.link)
async def getlink(message: types.Message, state: FSMContext) -> None:
    USERNAME_PATTERN = r"^[a-zA-Z][\w\d_]{4,31}$"  # Username (e.g., channelname)
    AT_USERNAME_PATTERN = r"^@[a-zA-Z][\w\d_]{4,31}$"  # Username starting with @
    PUBLIC_LINK_PATTERN = r"^https://t\.me/[a-zA-Z][\w\d_]{4,31}$"  # Public links (e.g., https://t.me/channelname)
    text = None
    lk = None
    chanid = None
    is_external = False
    # print(message.forward_from_chat)
    if message.forward_from_chat:
        chanid = message.forward_from_chat.id
        if message.forward_from_chat.username == None:
            try:
                lk = (await bot.create_chat_invite_link(chat_id=chanid, name=f"Join link by {config.bot_info.username}")).invite_link
            except Exception as e:
                print(e)
                await message.answer("Please, make sure to add the bot to the chat as an admin and try again")
                return
        else:
            lk = f"https://t.me/{message.forward_from_chat.username}"
    else:
        text = message.text 
        if re.match(USERNAME_PATTERN, text):
            # chanid = (await bot.get_chat("@"+text)).id
            uname = "@"+text
            lk = f"https://t.me/{text}"
        elif re.match(AT_USERNAME_PATTERN, text):
            uname = text
            # chanid = (await bot.get_chat(text)).id
            lk = f"https://t.me/{text[1:]}"
        elif re.match(PUBLIC_LINK_PATTERN, text):
            # chanid = (await bot.get_chat("@"+text[13])).id
            uname = "@"+text[13:]
            lk = text
        else:
            lk = text
            is_external = True
        try:
            if not is_external:
                chanid = (await bot.get_chat(uname)).id
        except:
            await message.answer("Chat not found, make sure chat exists and bot is an admin in the chat")
            return
    data = await state.get_data()
    title = data.get("title")
    if not is_external:
        try:
            channel_info = await bot.get_chat(chanid)
            mb_cnt = await bot.get_chat_member_count(chanid)
            mebot = await bot.get_chat_member(chat_id=chanid, user_id=config.bot_info.id)
        except Exception as e:
            print(e)
            print(lk)
            await message.answer("Please, make sure to add the bot to the chat as an admin, chat exists and try again")
            return
    # print(title, lk)
    await state.set_state(mands.confirm)
    await state.update_data(link=lk)
    await state.update_data(chid=chanid)
    if is_external:
        await message.answer(f"Check and confirm everything is correct\n\nChat Information:"
                f"\n\t\tTitle: {html.bold(title)}", reply_markup=mandconfirm((title, lk)), disable_web_page_preview=True)
    else:
        await message.answer(f"Check and confirm everything is correct\n\nChat Information:"
                f"\n\t\tTitle: {html.bold(channel_info.title)}"
                f"\n\t\tMembers count: {html.bold(mb_cnt)}"
                f"\n\t\tDescription: {html.blockquote(channel_info.description or 'No description')}", reply_markup=mandconfirm((title, lk)), disable_web_page_preview=True)

@mad.message(F.text == dict.back, mands.confirm)
async def back_to_link(message: types.Message, state: FSMContext) -> None:
    await state.set_state(mands.link)
    await message.answer("Now send the right link", reply_markup=back_key)

@mad.callback_query(mands.confirm)
async def confirm(callback: types.CallbackQuery, state: FSMContext) -> None:
    if callback.data == "cancel":
        await state.clear()
        await callback.answer("Cancelled")
        await pmands(callback.message, state)
        await callback.message.delete()
        return
    data = await state.get_data()
    chid = data.get("chid")
    title = data.get("title")
    link = data.get("link")
    chck = db.fetchone("SELECT title FROM channel WHERE chid = ?", (chid,))
    if chck:
        await callback.message.answer(f"This channel already has been added with the title <b>{chck[0]}</b>")
        await callback.answer("Cancelled")
        await pmands(callback.message, state)
        await callback.message.delete()
        return
    # channel_info = await bot.get_chat(link)
    if chid:
        db.query("INSERT INTO channel (chid, title, link) VALUES (?, ?, ?)", (chid, title, link))
    else:
        db.query("INSERT INTO external_links (title, link) VALUES (?, ?)", (title, link))
    await callback.answer(f"Successfully added")
    await pmands(callback.message, state)
    await callback.message.delete()
    await state.clear()

@mad.callback_query(CbDataStartsWith("delete_"))
async def delete_chat(callback: types.CallbackQuery, state: FSMContext) -> None:
    await state.set_state(dels.confirm)
    cnt = int(callback.data.split("_")[2])
    ty = callback.data.split("_")[1]
    if ty == "chat":
        channel = db.fetchone("SELECT idx, title, link FROM channel WHERE idx=?", (cnt,))
    else:
        channel = db.fetchone("SELECT idx, title, link FROM external_links WHERE idx=?", (cnt,))
    if not channel:
        await callback.answer("Channel not found")
        await callback.message.delete()
        return
    await state.update_data(idx=channel[0])
    await state.update_data(type=ty)
    await callback.message.answer(f"Are you sure you want to delete the chat?", reply_markup=mandconfirm((channel[1], channel[2])), disable_web_page_preview=True)
    await callback.message.delete()

@mad.callback_query(dels.confirm)
async def confirm_delete(callback: types.CallbackQuery, state: FSMContext) -> None:
    if callback.data == "cancel":
        await state.clear()
        await callback.answer("Cancelled")
        await pmands(callback.message, state)
        await callback.message.delete()
        return
    data = await state.get_data()
    idx = data.get("idx")
    if data.get("type") == "chat":
        db.query("DELETE FROM channel WHERE idx=?", (idx,))
    else:
        db.query("DELETE FROM external_links WHERE idx=?", (idx,))
    await callback.answer(f"Successfully deleted")
    await pmands(callback.message, state)
    await callback.message.delete()
    await state.clear()