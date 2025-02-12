from loader import db
from .chan_info import checksub
import random
from aiogram.fsm.context import FSMContext
import string

async def notsubbed(userid) -> list:
    channels = db.fetchall("SELECT title, chid, link FROM channel")
    new_chs = []
    for ch in channels:
        if not await checksub(userid, ch[1]):
            new_chs.append(ch)
    # for link in external_links:
    #     new_chs.append(link)
    return new_chs

def get_external_links():
    external_links = db.fetchall("SELECT title, link FROM external_links")
    ex = []
    for link in external_links:
        ex.append(link)
    return ex

def g_code():
    characters = string.ascii_letters + string.digits  # Letters and digits
    return ''.join(random.sample(characters, 6))

async def ber(state: FSMContext, key: str):
    data = await state.get_data()
    return data.get(key)