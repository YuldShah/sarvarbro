from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from data.dict import check_subs

def mand_chans(channels, external_links) -> InlineKeyboardMarkup:
    btns = []
    for name, idx, url in channels:
        btns.append([InlineKeyboardButton(text=name, url=url)])
    for title, url in external_links:
        btns.append([InlineKeyboardButton(text=title, url=url)])
    btns.append([InlineKeyboardButton(text=check_subs, callback_data="check_subs")])
    return InlineKeyboardMarkup(inline_keyboard=btns)