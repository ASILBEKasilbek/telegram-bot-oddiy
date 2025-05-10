from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from .languages import *
from config import ANIDUBLE
def choose_language_clbtn():
    cheker = InlineKeyboardMarkup()
    cheker.add(InlineKeyboardButton("🇺🇿 O'zbekcha",callback_data=f'select,uz'))
    return cheker
def hamkor_btn():
    cheker = InlineKeyboardMarkup()
    cheker.add(InlineKeyboardButton("Bot qo'shish",callback_data=f'hamkor_qoshish'),InlineKeyboardButton("Bot o'chirish",callback_data=f'hamkor_remove'))
    cheker.add(InlineKeyboardButton("Botlar ro'yxati",callback_data=f'hamkor_list'))
    cheker.add(InlineKeyboardButton("🔙Chiqish",callback_data=f'qaytish'))
    return cheker
def search_clbtn():
    cheker = InlineKeyboardMarkup()
    cheker.add(InlineKeyboardButton("🔍Nom va ID orqali qidirish",callback_data=f'search_id_name'),InlineKeyboardButton("🖼 Rasm orqali qidiruv",callback_data=f'search_rasm'))
    cheker.add(InlineKeyboardButton("🔄 Anime tavsiya",callback_data=f'search_teg'),InlineKeyboardButton("🎭 Janr orqali qidiruv",callback_data=f'search_anime_id'))
    cheker.add(InlineKeyboardButton("🌏 Eng ko'p ko'rilgan animelar",callback_data=f'search_top_10')) 
    return cheker

def vip_buying_clbtn():
    cheker = InlineKeyboardMarkup()
    cheker.add(InlineKeyboardButton("⚡️Sotib olish", callback_data='vip,vip'))
    cheker.add(InlineKeyboardButton("🆓 Tekin olish", callback_data='free'))
    return cheker



def which_vip_clbtn():
    cheker = InlineKeyboardMarkup()
    cheker.add(InlineKeyboardButton("⚡️AniPass",callback_data=f'which,vip'))
    return cheker

def vip_channel_clbtn():
    cheker = InlineKeyboardMarkup()
    cheker.add(InlineKeyboardButton("❤️1 oylik - 20.000💸",callback_data=f'vip,channel,1'),InlineKeyboardButton("❤️‍🔥2 oylik - 40.000💸",callback_data=f'vip,channel,2'))
    cheker.add(InlineKeyboardButton("🔥3 oylik - 60.000💸",callback_data=f'vip,channel,3'),InlineKeyboardButton("⚡️4 oylik - 80.000💸",callback_data=f'vip,channel,4'))
    return cheker

def post_watching_clbtn(anime_id,anime_list):
    cheker = InlineKeyboardMarkup(row_width=2)
    # a='ANIDUBLE_RASMIY_BOT'
    if len(anime_list.split(",")) > 1:
        num = 0
        for i in anime_list.split(","):
            num += 1
            cheker.insert(InlineKeyboardButton(f"⚡️{num} -Fasl⚡️",url=f"https://t.me/{ANIDUBLE}?start={i}"))
    else:
        cheker.add(InlineKeyboardButton(f"✨Tomosha qilish✨",url=f"https://t.me/{ANIDUBLE}?start={anime_id}"))
        
    return cheker

def create_channel_buttons(channels):
    keyboard = InlineKeyboardMarkup(row_width=1)
    for channel in channels:
        channel_name = channel[1]
        channel_link = channel[2] 
        button = InlineKeyboardButton(channel_name, callback_data=f"select_channel,{channel_link}")
        keyboard.add(button)
    return keyboard
def admin_check_clbtn(data1 = None,data2 = None,data3 = None):
    cheker = InlineKeyboardMarkup()
    cheker.add(InlineKeyboardButton("✅Ha",callback_data=f'select,yeah,{data1},{data2},{data3}'),InlineKeyboardButton("❌Yo'q",callback_data=f'select,nope,{data1},{data2},{data3}')) 
    return cheker

def admin_check_post_clbtn(data1 = None,data2 = None,data3 = None):
    cheker = InlineKeyboardMarkup()
    cheker.add(InlineKeyboardButton("✅Ha",callback_data=f'select,yeah,{data1},{data2},{data3}'),InlineKeyboardButton("❌Yo'q",callback_data=f'select,nope,{data1},{data2},{data3}')) 
    cheker.add(InlineKeyboardButton("➕Yana qo'shish",callback_data=f'select,add')) 
    return cheker

def vip_2nd_buying_clbtn():
    cheker = InlineKeyboardMarkup()
    cheker.add(InlineKeyboardButton("🔙Chiqish",callback_data=f'back'))
    return cheker


def vip_activate_clbtn(user_id):
    cheker = InlineKeyboardMarkup()
    cheker.add(InlineKeyboardButton("✅Tasdiqlash",callback_data=f'vip,activate,{user_id}'))
    cheker.add(InlineKeyboardButton("❌Bekor qilish",callback_data=f'vip,cancel,{user_id}'))
    return cheker

def lux_activate_clbtn(user_id):
    cheker = InlineKeyboardMarkup()
    cheker.add(InlineKeyboardButton("✅1 - oylik",callback_data=f'lux,1,{user_id}'),InlineKeyboardButton("✅2 - oylik",callback_data=f'lux,2,{user_id}'))
    cheker.add(InlineKeyboardButton("✅3 - oylik",callback_data=f'lux,3,{user_id}'),InlineKeyboardButton("✅4 - oylik",callback_data=f'lux,4,{user_id}'))
    cheker.add(InlineKeyboardButton("❌Bekor qilish",callback_data=f'lux,cancel,{user_id}'))
    return cheker

def are_you_sure_clbtn(call = None,anime_id = None,additional = None):
    if call == None:
        call = "None"
    cheker = InlineKeyboardMarkup()
    cheker.add(InlineKeyboardButton("✅Ha",callback_data=f'sure,yeah,{call},{anime_id},{additional}'),InlineKeyboardButton("❌Yo'q",callback_data=f'sure,nope,{call},{anime_id}'))
        
    return cheker

def staff_list_clbtn(staff_list):
    cheker = InlineKeyboardMarkup()
    for i in staff_list:
        cheker.add(InlineKeyboardButton(f"{i[1]}",callback_data=f'staff,{i[0]}'))
    cheker.add(InlineKeyboardButton(f"➕",callback_data=f'add'))
    cheker.add(InlineKeyboardButton(f"🔙Chiqish",callback_data=f'exit'))
    
    return cheker

def sponsor_list_clbtn(sponsor):
    cheker = InlineKeyboardMarkup()
    for i in sponsor:
        cheker.add(InlineKeyboardButton(f"{i[1]}",callback_data=f'sponsor,{i[0]}'))
    cheker.add(InlineKeyboardButton(f"➕",callback_data=f'add'))
    cheker.add(InlineKeyboardButton(f"🔙Chiqish",callback_data=f'exit'))
    
    return cheker

def anime_language_clbtn():
    
    cheker = InlineKeyboardMarkup()
    cheker.add(InlineKeyboardButton("🇺🇿O'zbekcha",callback_data=f'lang,uz'))
    cheker.add(InlineKeyboardButton("🔙Ortga",callback_data=f'lang,back'))
        
    return cheker

def type_content_clbtn():
    
    cheker = InlineKeyboardMarkup()
    cheker.add(InlineKeyboardButton("✨Anime",callback_data=f'type,anime'))
    cheker.add(InlineKeyboardButton("🎥Kino",callback_data=f'type,film'))
    cheker.add(InlineKeyboardButton("🔙Ortga",callback_data=f'type,back'))
        
    return cheker

def admin_searched_animes_clbtn(anime_list):
    cheker = InlineKeyboardMarkup()
    for i in anime_list:
        cheker.add(InlineKeyboardButton(f"{i[3]}",callback_data=f'search,{i[0]}'))
    cheker.add(InlineKeyboardButton(f"🔙Chiqish",callback_data=f'search,back'))
    return cheker

def tasodifiy_anime_clbtn(anime_list):
    cheker = InlineKeyboardMarkup()
    cheker.add(InlineKeyboardButton(f"{anime_list[3]}",callback_data=f'search,{anime_list[0]}'))
    cheker.add(InlineKeyboardButton(f"🔙Chiqish",callback_data=f'search,back'))
    return cheker

def sponsors_sub_lists(sponsor):
    cheker = InlineKeyboardMarkup()
    for i in sponsor:
        link = i[2]
        cheker.add(InlineKeyboardButton(f"{i[1]}",url=link))
    
    return cheker

def searched_series_list_clbtn(serie_list,num):
    cheker = InlineKeyboardMarkup()
    for i in serie_list:
        if num == int(i[2]):
            cheker.insert(InlineKeyboardButton(f"[ {i[2]} ]",callback_data=f'serie,{i[1]},{i[0]},now'))
        else:
            cheker.insert(InlineKeyboardButton(f"{i[2]}",callback_data=f'serie,{i[1]},{i[0]},{i[2]}'))

    cheker.add(InlineKeyboardButton(f"🔙Chiqish",callback_data=f'serie,{i[1]},{i[0]},back'))
    return cheker

def searched_series_edit_clbtn(serie_id,is_last,anime_id):
    cheker = InlineKeyboardMarkup()
    
    cheker.insert(InlineKeyboardButton(f"♻️Boshqa yuklash",callback_data=f'edit,{serie_id},new,{anime_id}'))
    if is_last == True:
        cheker.insert(InlineKeyboardButton(f"🗑O'chirish",callback_data=f'edit,{serie_id},delete,{anime_id}'))

    cheker.add(InlineKeyboardButton(f"🔙Ortga",callback_data=f'edit,{serie_id},back,{anime_id}'))
    return cheker

def anime_add_serie_clbtn(status,anime_id):
    
    cheker = InlineKeyboardMarkup()
    if status == "loading":
        cheker.add(InlineKeyboardButton("🎞Seriya qo'shish",callback_data=f'add,serie,{anime_id}'))
        cheker.add(InlineKeyboardButton("🟢Tugallash",callback_data=f'add,finish,{anime_id}'))
        cheker.add(InlineKeyboardButton("🔙Chiqish",callback_data=f'add,back,none'))
        
    else:
        cheker.add(InlineKeyboardButton("🔙Chiqish",callback_data=f'add,back'))
        
    return cheker

def edit_anime_clbtn(status,anime_id,is_about,is_vip = 0):
    
    cheker = InlineKeyboardMarkup()
    if is_about == True:
        cheker.add(InlineKeyboardButton("📋Asosiy ma'lumotlar",callback_data=f'edit,basic_view,{anime_id}'))
    else:
        cheker.add(InlineKeyboardButton("📄Anime haqida",callback_data=f'edit,about_view,{anime_id}'))
        
    cheker.add(InlineKeyboardButton("📝Haqidani tahrirlash",callback_data=f'edit,about,{anime_id}'),InlineKeyboardButton("🏷Nomni tahrirlash",callback_data=f'edit,name,{anime_id}'))
    cheker.add(InlineKeyboardButton("📑Janrini tahrirlash",callback_data=f'edit,genre,{anime_id}'),InlineKeyboardButton("🎙Fandub ni tahrirlash",callback_data=f'edit,dub,{anime_id}'))
    cheker.add(InlineKeyboardButton("💬Tilini tahrirlash",callback_data=f'edit,lang,{anime_id}'))
    cheker.add(InlineKeyboardButton("#️⃣Tegni tahrirlash",callback_data=f'edit,teg,{anime_id}'),InlineKeyboardButton("🗑Animeni o'chirish",callback_data=f'edit,delete,{anime_id}'))

    if is_vip == 1:
        cheker.add(InlineKeyboardButton("⚡️AniPass ni o'chirish",callback_data=f'edit,vip_off,{anime_id}'))
    else:
        cheker.add(InlineKeyboardButton("⚡️AniPass ni yoqish",callback_data=f'edit,vip_on,{anime_id}'))

    if status == "finished":   
        cheker.add(InlineKeyboardButton("🟡Aktivlashtrish",callback_data=f'edit,activate,{anime_id}'))
    elif status == "loading":   
        cheker.add(InlineKeyboardButton("🟢Tugallash",callback_data=f'edit,stop,{anime_id}'))

    cheker.add(InlineKeyboardButton("🔙Chiqish",callback_data=f'edit,exit,{anime_id}'))
    
    return cheker

def results_clbtn(link):
    cheker = InlineKeyboardMarkup()
    cheker.add(InlineKeyboardButton("🔍Natijalarni ko'rish",url=f"{link}"))
        
    return cheker

def back_button_user_clbtn(lang,call = "back"):
    cheker = InlineKeyboardMarkup()
    if lang == "uz":
        cheker.add(InlineKeyboardButton("🔙Ortga",callback_data=f'{call},back'))
    if lang == "ru":
        cheker.add(InlineKeyboardButton("🔙Назад",callback_data=f'{call},back'))
        
    return cheker

def anime_menu_clbtn(lang,anime_id,is_about,have_serie,is_vip):
    cheker = InlineKeyboardMarkup()
    if lang == "uz":
        if is_about == False:
            cheker.add(InlineKeyboardButton("📄Anime haqida",callback_data=f'anime,about,{anime_id}'))
        elif is_about == True:
            cheker.add(InlineKeyboardButton("📑Asosiy ma'lumotlar",callback_data=f'anime,main,{anime_id}'))
        if have_serie == False:
            pass
        elif have_serie == True:
            if is_vip == "0" or is_vip == 0:
                cheker.add(InlineKeyboardButton("🖥Tomosha qilish",callback_data=f'anime,watch,{anime_id},none'))
            else:
                cheker.add(InlineKeyboardButton("⚡️Tomosha qilish",callback_data=f'anime,watch,{anime_id},vip'))

        cheker.add(InlineKeyboardButton("🔙Ortga",callback_data=f'anime,back,{anime_id}'))
    elif lang == "ru":
        cheker.add(InlineKeyboardButton("🔙Назад",callback_data=f'anime,back'))
        
    return cheker

def film_menu_clbtn(lang,film_id,is_about,have_serie):
    cheker = InlineKeyboardMarkup()
    if lang == "uz":
        if is_about == False:
            cheker.add(InlineKeyboardButton("📄Film haqida",callback_data=f'film,about,{film_id}'))
        elif is_about == True:
            cheker.add(InlineKeyboardButton("📑Asosiy ma'lumotlar",callback_data=f'film,main,{film_id}'))
        if have_serie == False:
            pass
        elif have_serie == True:
            cheker.add(InlineKeyboardButton("🖥Tomosha qilish",callback_data=f'film,watch,{film_id}'))

        cheker.add(InlineKeyboardButton("🔙Ortga",callback_data=f'film,back,{film_id}'))
    elif lang == "ru":
        cheker.add(InlineKeyboardButton("🔙Назад",callback_data=f'film,back'))
        
    return cheker

def anime_series_clbtn(now_serie,series,page = 0):
    cheker = InlineKeyboardMarkup()
    
    count = 0
    counting = 0
    paging = page * 20 + 1
    last_serie = 0

    if paging == 0:
        paging = 1
        
    for i in series:
        counting += 1
        if i[2] >= paging:
            count += 1
            if count <= 20:
                if now_serie == i[2]:
                    cheker.insert(InlineKeyboardButton(f"💿 - [ {i[2]} ]",callback_data=f'watching,now')) 
                else:
                    cheker.insert(InlineKeyboardButton(f"{i[2]}",callback_data=f'watching,watch,{i[1]},{i[2]},{i[3]},{i[0]},{page}'))
                last_serie = i[2]
                anime_id = i[0]
            else:
                pass

    if counting <= 20:
        cheker.add(InlineKeyboardButton("🔙Ortga",callback_data=f'watching,back,{i[0]}'))

    else:
        if page == 0 and counting >= 5:
            cheker.add(InlineKeyboardButton("⏩",callback_data=f'watching,next,{page+1},{i[0]},{now_serie}'))
        elif counting > last_serie:
            cheker.add(InlineKeyboardButton("⏪",callback_data=f'watching,previous,{page-1},{i[0]},{now_serie}'),InlineKeyboardButton("⏩",callback_data=f'watching,next,{page+1},{i[0]},{now_serie}'))
        else:
            cheker.add(InlineKeyboardButton("⏪",callback_data=f'watching,previous,{page-1},{i[0]},{now_serie}'))

        cheker.add(InlineKeyboardButton("🔙Ortga",callback_data=f'watching,back,{anime_id}'))

    return cheker

def back_button_clbtn(call):
    if not call:
        call = "back"
    cheker = InlineKeyboardMarkup()
    cheker.add(InlineKeyboardButton("🔙Ortga",callback_data=f'{call},back'))
        
    return cheker

def serie_posting_action_clbtn():
    cheker = InlineKeyboardMarkup()
    cheker.add(InlineKeyboardButton("🖥Kanalga post qilish",callback_data=f'select,post'))
    cheker.add(InlineKeyboardButton("🔙Chiqish",callback_data=f'select,back'))
        
    return cheker

def serie_post_link_clbtn(anime_id):
    cheker = InlineKeyboardMarkup()
    # a='demo23454_bot';a1='ANIDUBLE_RASMIY_BOT'
    cheker.add(InlineKeyboardButton("✨Tomosha qilish✨",url=f"https://t.me/{ANIDUBLE}?start={anime_id}serie"))
        
    return cheker

def true_false_link_clbtn():
    cheker = InlineKeyboardMarkup()
    cheker.add(InlineKeyboardButton("✅️ Ha",callback_data=f'HA'),InlineKeyboardButton("❌️ Yo'q",callback_data=f"Keyinroq"))   
    return cheker