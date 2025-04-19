from aiogram import types
from users_base import *
from dispatcher import dp
from aiogram.dispatcher import FSMContext
from .buttons import *
from .languages import *
from .callbacks import *
from aiogram.dispatcher.filters.state import State, StatesGroup
import asyncio
import shutil
from .image_maker import image_making
import os
from aiogram.types import InputFile

anime_treller_chat = -1001990975355
anime_series_chat = -1002076256295
vip_buying_chat = -1002099276344

class Add_staff(StatesGroup):
    adding = State()

class Admin(StatesGroup):
    menu = State()
    
    send_message = State()
    send_message_to_one = State()
    sending_to_one = State()
    
    subscribe = State()
    
    sure = State()

class Add_anime(StatesGroup):
    type = State()
    language = State()
    treller = State()
    name = State()
    about = State()
    genre = State()
    teg = State()
    dub = State()

class Add_serie(StatesGroup):
    type = State()
    search = State()
    actions = State()

    add_serie = State()
    add_film = State()
    finish_anime =State()
    
class Edit_anime(StatesGroup):
    type = State()
    search = State()
    editing_menu = State()
    
    edit_about = State()

class Edit_serie(StatesGroup):
    type = State()
    search = State()
    series_menu = State()
    editing_menu = State()

    upload_new = State()
    delete_serie = State()

class Posting(StatesGroup):
    search = State()
    video = State()
    check = State()
    add_anime = State()
    qismli_post = State()
    select_anime = State()
    select_series = State()
    select_channel = State()

class PostingSerie(StatesGroup):
    search = State()
    photo = State()
    action = State()

class Add_sponser(StatesGroup):
    menu = State()
    adding = State()
    add =   State()
    remove = State()

# Qismli post boshlash
# @dp.message_handler(lambda msg: msg.text == "Qismli post", state="*")
# async def qismli_post_start(msg: types.Message, state: FSMContext):
#     await state.finish()
#     await Posting.select_anime.set()
#     await msg.answer("Qaysi animeni qismini post qilamiz?", reply_markup=back_button_btn())

# Anime tanlash
@dp.message_handler(content_types=["text"], state=Posting.select_anime)
async def select_anime_for_post(msg: types.Message, state: FSMContext):
    anime_name = msg.text.strip()
    if anime_name == "🔙Ortga":
        await state.finish()
        await msg.answer("Bosh menyuga qaytildi.", reply_markup=admin_button_btn())
        return
    
    # Animenni bazadan izlash
    anime_data = search_anime_base(anime_name)
    if not anime_data:
        await msg.answer("Bunday anime topilmadi. Iltimos, boshqa nom kiriting yoki tekshiring.", reply_markup=back_button_btn())
        return
    # Birinchi topilgan animeni olamiz
    anime = anime_data[0]
    anime_id = anime[0]  # anime_id
    await state.update_data(anime_id=anime_id, anime_name=anime[3])  # anime nomini saqlaymiz
    
    # Animenning seriyalarini olish
    series = get_anime_series_base(anime_id)
    if not series:
        await msg.answer(f"'{anime[3]}' uchun seriyalar topilmadi.", reply_markup=back_button_btn())
        await state.finish()
        return
    
    # Inline buttonlar bilan seriyalar ro‘yxatini yaratish
    series_buttons = InlineKeyboardMarkup(row_width=3)
    for serie in series:
        serie_num = serie[2]  # serie_num
        series_buttons.add(InlineKeyboardButton(text=f"{serie_num}-qism", callback_data=f"serie_{serie[1]}"))  # serie_id
    series_buttons.add(InlineKeyboardButton(text="🔙Ortga", callback_data="back_to_anime"))

    await Posting.select_series.set()
    await msg.answer(f"'{anime[3]}' animening qaysi qismini post qilamiz?", reply_markup=series_buttons)

# Seriya tanlash
@dp.callback_query_handler(state=Posting.select_series)
async def select_series_for_post(call: types.CallbackQuery, state: FSMContext):
    if call.data == "back_to_anime":
        await Posting.select_anime.set()
        await call.message.edit_text("Qaysi animeni qismini post qilamiz?", reply_markup=back_button_btn())
        return
    
    serie_id = int(call.data.split("_")[1])
    serie_num = get_id_to_num_serie_base(serie_id)
    await state.update_data(serie_id=serie_id, serie_num=serie_num)
    
    # Kanallarni olish
    channels = get_channels()
    if not channels:
        await call.message.edit_text("Hozirda hech qanday kanal qo‘shilmagan. Iltimos, avval kanal qo‘shing.", reply_markup=back_button_btn())
        await state.finish()
        return
    
    # Inline buttonlar bilan kanallar ro‘yxatini yaratish
    channel_buttons = InlineKeyboardMarkup(row_width=2)
    for channel in channels:
        channel_name = channel[1]  # name
        channel_buttons.add(InlineKeyboardButton(text=channel_name, callback_data=f"channel_{channel[0]}"))
    channel_buttons.add(InlineKeyboardButton(text="🔙Ortga", callback_data="back_to_series"))

    await Posting.select_channel.set()
    user_data = await state.get_data()
    await call.message.edit_text(f"'{user_data['anime_name']}' animening {serie_num}-qismini qaysi kanalga post qilamiz?", reply_markup=channel_buttons)

# # Kanal tanlash
# def format_post_text(anime_id, serie_id, serie_num, selected_channel):
#     # Anime ma'lumotlarini olish
#     anime_data = get_anime_base(anime_id)
#     if not anime_data:
#         return None, "Anime ma'lumotlari topilmadi."
    
#     anime = anime_data[0]
#     anime_name = anime[3]  # name
#     genre = anime[5]       # genre
#     about = anime[4]       # about (qisqartiriladi)
    
#     # Seriya ma'lumotlarini olish
#     series = get_anime_series_base(anime_id)
#     quality = None
#     for serie in series:
#         if serie[1] == serie_id:  # serie_id
#             quality = serie[3]    # quality
#             break
    
#     # About matnini qisqartirish (agar uzun bo‘lsa)
#     about = (about[:100] + "...") if len(about) > 100 else about
    
#     # Post matnini formatlash
#     post_text = f"""
# 🎬 *{anime_name}* - {serie_num}-qism
# 🌟 *Janr*: {genre}
# 📜 *Tavsif*: {about}
# {'📽 *Sifat*: ' + quality if quality else ''}

# 📺 *Kanal*: {selected_channel[1]}
# 🔗 {selected_channel[2]}
# """
#     return post_text, None

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from aiogram import types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def back_button_inline():
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton(text="🔙 Ortga", callback_data="back_to_menu"))
    return markup



@dp.callback_query_handler(state=Posting.select_channel)
async def select_channel_for_post(call: types.CallbackQuery, state: FSMContext):
    # Orqaga qaytish (seriyalarni qayta ko‘rsatish)
    if call.data == "back_to_series":
        user_data = await state.get_data()
        anime_id = user_data.get("anime_id")
        anime_name = user_data.get("anime_name")
        
        series = get_anime_series_base(anime_id)
        series_buttons = InlineKeyboardMarkup(row_width=3)
        for serie in series:
            serie_num = serie[2]
            series_buttons.add(InlineKeyboardButton(text=f"{serie_num}-qism", callback_data=f"serie_{serie[1]}"))
        series_buttons.add(InlineKeyboardButton(text="🔙 Ortga", callback_data="back_to_anime"))

        await Posting.select_series.set()
        await call.message.edit_text(f"'{anime_name}' animening qaysi qismini post qilamiz?", reply_markup=series_buttons)
        return
    
    # Kanal ID sini olish
    channel_id = int(call.data.split("_")[1])
    channels = get_channels()
    selected_channel = None
    for channel in channels:
        if channel[0] == channel_id:
            selected_channel = channel
            break
    
    if not selected_channel:
        await call.message.edit_text("Kanal topilmadi, qayta urinib ko‘r! 😕", reply_markup=back_button_inline())
        await state.finish()
        return
    
    # Anime va seriya ma'lumotlarini olish
    user_data = await state.get_data()
    anime_id = user_data.get("anime_id")
    # print(anime_id)
    anime_name = user_data.get("anime_name")
    serie_num = user_data.get("serie_num")
    anime_data = get_anime_base(anime_id)
    anime_id=get_seria_id(anime_id,serie_num)
    print(anime_id)
    
    # Anime ma'lumotlarini bazadan olish
    
    # print(anime_data)
    if not anime_data:
        await call.message.edit_text("Anime ma'lumotlari topilmadi! 😕", reply_markup=back_button_inline())
        await state.finish()
        return
    
    anime = anime_data[0]
    anime_lang = anime[1]  # lang
    anime_genre = anime[5]  # genre
    anime_teg = anime[6]  # teg
    anime_dub = anime[7]  # dub
    anime_serie = anime[8]  # series
    anime_film = anime[9]  # films
    anime_status = anime[11]  # status
    anime_views = anime[12]  # views
    
    # Status va tilni formatlash
    if anime_status == "loading":
        status = "OnGoing"
    elif anime_status == "finished":
        status = "Tugallangan"
    else:
        status = anime_status
    
    if anime_lang == "uz":
        lang = "O‘zbekcha"
    elif anime_lang == "ru":
        lang = "Ruscha"
    elif anime_lang == "jp":
        lang = "Yaponcha"
    elif anime_lang == "en":
        lang = "Inglizcha"
    else:
        lang = anime_lang
    
    # Postni tayyorlash (kanal nomisiz va linksiz, chotki)
    post_text = f"""
📥  *{anime_name}* - {serie_num}-qism 🔥 @AniDuble
"""
    
    # Postni kanalga yuborish (inline knopka bilan)
    try:
        await call.bot.send_message(
            chat_id=selected_channel[2],
            text=post_text,
            parse_mode="Markdown",
            reply_markup=serie_post_link_clbtn(anime_id)
        )
        await call.message.edit_text(
            f"✅ '{anime_name}' {serie_num}-qismi zo'r yuborildi! 🚀",
            reply_markup=back_button_inline()
        )
    except types.exceptions.ChatNotFound:
        await call.message.edit_text(
            "Kanal topilmadi yoki bot yozolmaydi! 😕",
            reply_markup=back_button_inline()
        )
    except types.exceptions.BotKicked:
        await call.message.edit_text(
            f"Bot {selected_channel[1]} dan bloklangan! 😡",
            reply_markup=back_button_inline()
        )
    except Exception as e:
        await call.message.edit_text(
            f"Xato: {str(e)} 😞",
            reply_markup=back_button_inline()
        )
    
    await state.finish()

# @dp.message_handler(lambda msg: msg.text == "🔙Ortga", state="*")
# async def back_to_start(msg: types.Message, state: FSMContext):
#     await state.finish()
#     await msg.answer("Bosh menyuga qaytildi.", reply_markup=admin_button_btn())


@dp.message_handler(commands="admin",state="*")
async def start(msg:types.Message ,state : FSMContext):

    if str(msg.chat.id)[0] == "-":
          pass
    else:
        user_id = msg.from_user.id
        user = get_user_base(user_id)
        
        if user[0][7] == True or user[0][8] == True:
            await state.finish()
            await Admin.menu.set()
            await msg.answer("✅Admin panelga hush kelibsiz !",reply_markup=admin_button_btn())
        else:
            await msg.answer("❌",reply_markup=user_button_btn(user[0][2],"False"))

@dp.message_handler(content_types=["text"],state=Admin.menu)
async def start(msg:types.Message ,state : FSMContext):
    text = msg.text
    
    if text == "🆕Anime qo'shish":
        await state.finish()
        await Add_anime.language.set()
        a = await msg.answer(". . .",reply_markup=admin_button_btn())
        await a.delete()
        await msg.answer("<b>🆕Yangi anime uchun til tanlang</b>",reply_markup=anime_language_clbtn())
        
    elif text == "➕Seriya qo'shish":
        await state.finish()
        await Add_serie.search.set()
        a = await msg.answer(". . .",reply_markup=admin_button_btn())
        await a.delete()
        await msg.answer("<b>➕Seria qo'shishlishi kerak bo'lganan anime nomini yuboring !</b>",reply_markup=back_button_btn())
    
    elif text == "👁‍🗨Post qilish":
        await state.finish()
        await Posting.search.set()
        await msg.answer("<b>🔍Kanalga post qilinishi kerak bo'lgan animeni nomini kiriting</b>",reply_markup=back_button_btn())
    elif text == "🎞Seriani post qilish":
        await state.finish()
        await PostingSerie.search.set()
        await msg.answer("<b>🔍Yangi qism qo'shilganligi haqida post qilinishi kerak bo'lgan animeni nomini kiriting</b>",reply_markup=back_button_btn())
    elif text == "Kanal qo'shish":
        await state.finish()
        await Add_sponser.add.set()
        await msg.answer("Qo'shmoqchi bo'lgan kanal linkini yuboring",reply_markup=back_button_btn())
    elif text == "Kanal o'chirish":
        await state.finish()
        await Add_sponser.remove.set()
        await msg.answer("O'chirmoqchi bo'lgan kanal linkini yuboring",reply_markup=back_button_btn())
    elif text == "Kanallar":
        await state.finish()  # Stateni tugatish
        channels = get_channels()
        if not channels:
            await msg.answer("Hozircha hech qanday kanal qo'shilmagan.")
            return
        # Har bir kanalni chiroyli qilib formatlaymiz
        text = "📢 *Kanallar ro'yxati:*\n\n"
        for ch in channels:
            text += f"🔹 *Nomi:* {ch[1]}\n🔗 *Havola:* {ch[2]}\n🕒 *Qo'shilgan sana:* {ch[4]}\n\n"

        await msg.answer(text, parse_mode="Markdown")
    
    elif text == "Qismli post":
        await state.finish()
        await Posting.select_anime.set()
        await msg.answer("Qaysi animeni qismini post qilamiz",reply_markup=back_button_btn())

    elif text == "✏️Animeni tahrirlash":
        await state.finish()
        a = await msg.answer(". . .",reply_markup=admin_button_btn())
        await a.delete()
        await Edit_anime.search.set()
        await msg.answer("<b>📝Tahrirlanishi kerak bo'lgan animeni nomini yuboring !</b>",reply_markup=back_button_btn())

    elif text == "✏️Seriani tahrirlash":
        await state.finish()
        await Edit_serie.search.set()
        await msg.answer("<b>📝Seriasi tahrirlanishi kerak bo'lgan anime nomini kiriting</b>",reply_markup=back_button_btn())
        
    elif text == "💬Xabar yuborish":
        user = get_user_is_admin_base(msg.from_user.id)[0][0]
        if user == True:
            await Admin.send_message.set()
            await msg.answer("<b>💬Botdagi foydalanuvchilarga yuborish uchun xabar kiriting !</b>",reply_markup=back_button_btn())
        else:
            await msg.answer("🙁<b>Bu faqat adminlar uchun !</b>",reply_markup=admin_button_btn())

    elif text == "👤Alohida xabar":
        await Admin.send_message_to_one.set()
        await msg.answer("💬<b>Xabar yuborish uchun foydalanuvchi ID sini yoki Usernamesini kiriting !</b>",reply_markup=back_button_btn())
        
    elif text == "🔐Majburiy a'zo":
        user = get_user_is_admin_base(msg.from_user.id)[0][0]
        if user == True: 
            await Admin.subscribe.set()
            sponsor = get_sponsor_base()
            await state.finish()
            if not sponsor:
                await Add_sponser.adding.set()
                await msg.answer("🔒<b>Majburiy a'zo qo'shish</b> uchun majburiy a'zoga qo'shilishi kerak bo'lgan <b>kanaldan istalgan habarni botga ulashing</b>\n❗️Bot siz <b>majbury a'zo qilmoqchi bo'lgan kanalda</b> admin etib tayinlangan bo'lishi zarur !",reply_markup=back_button_btn())
            else:
                await Add_sponser.menu.set()
                a = await msg.answer("⏳",reply_markup=back_button_btn())
                await a.delete()
                await msg.answer("🔒<b>Sponsorlikdan chiqarilishi</b> kerak bo'lgan <b>Kanalni tanlang</b> yoki ➕ <b>orqali yana qo'shing</b> ",reply_markup=sponsor_list_clbtn(sponsor))
        else:
            await msg.answer("😕<b>Bu faqat Adminlar uchun</b>")
    elif text == "👔Staff qo'shish":
        user = get_user_is_admin_base(msg.from_user.id)[0][0]
        if user == True: 
            staff = get_staff_base()
            a = await msg.answer("⏳",reply_markup=back_button_btn())
            await a.delete()
            await Add_staff.adding.set()
            if not staff:
                await msg.answer("👔<b>Staff User</b> qo'shish uchun <b>Foydalanuvchi ID sini</b> yuboring !",reply_markup=back_button_btn())
            else:
                await msg.answer("❗️<b>Bo'shatilishi</b> kerak bo'lgan <b>staff ni tanlang</b>\n Yoki ➕ orqali <b>yangi staff qo'shing</b>",reply_markup=staff_list_clbtn(staff))
        else:
            await msg.answer("😕<b>Bu faqat Adminlar uchun</b>")
    elif text == "📊Statik ma'lumotlar":
        statistics = get_all_statistics()
        if statistics:
            bot_users, vip_users, free_users, total_anime, anime_views, series_count, active_users, new_users, most_watched_anime, most_active_user = statistics

            text = f"""
    <b>📊AniDuble botining statistikasi :</b>
    -----------------------------------------------------
    👥<b>Jami foydalanuvchilar soni :</b> {bot_users}
    🔒<b>VIP foydalanuvchilar soni :</b> {vip_users-free_users}
    ⭐<b>Tekin vip olgan foydalanuvchilar soni :</b> {free_users}
    🖥<b>Jami animelar soni :</b> {total_anime}
    👀<b>Jami tomoshalar soni :</b> {anime_views}
    📺<b>Jami seriyalar soni :</b> {series_count}
    ➕<b>Oxirgi 24 soatda yangi foydalanuvchilar :</b> {new_users}
    🎬<b>Eng ko'p tomosha qilingan anime :</b> {most_watched_anime if most_watched_anime else "Ma'lumot yo'q"}
    -----------------------------------------------------
    """

            await msg.answer(text, parse_mode='HTML')
        else:
            text = "<b>Statistika ma'lumotlari topilmadi!</b>"
            await msg.answer(text, parse_mode='HTML')
    elif text == "🔙Chiqish":
        await state.finish()  # State ni tugatish
        a = await msg.answer("⌛️", reply_markup=back_button_btn())  # Yuklanayotgan xabar
        await a.delete()  # Yuklanayotgan xabarni o'chirish
        await msg.answer("/start ni bosing ✅")  # Asosiy menyuga qaytish


@dp.message_handler(content_types=['text'], state=Add_sponser.add)
async def qosh(msg: types.Message, state: FSMContext):
    text = msg.text.strip()

    if text == "🔙Ortga":
        await state.finish()
        await Admin.menu.set()
        await msg.answer("👔<b>Admin panel</b>", reply_markup=admin_button_btn())
        return

    try:
        if msg.forward_from_chat:
            chat = msg.forward_from_chat
        elif text.startswith("@"):
            chat = await msg.bot.get_chat(text)
        else:
            await msg.answer("❗️Iltimos, kanal xabarini forward qiling yoki @username yuboring.")
            return

        # Bot kanalga adminmi?
        await msg.bot.get_chat_administrators(chat.id)

        name = chat.title
        link = chat.invite_link or f"https://t.me/{chat.username}" if chat.username else "Havola mavjud emas"
        added_by = msg.from_user.id
        date_added = datetime.now().strftime("%Y-%m-%d")
        asab="@"+chat.username
        add_channels_base(name,asab, added_by, date_added)

        await state.finish()
        await Admin.menu.set()
        await msg.answer(f"✅ <b>{name}</b> kanali muvaffaqiyatli qo‘shildi!", reply_markup=admin_button_btn())

    except Exception as e:
        print(f"[Kanal qo‘shish xatosi] {e}")
        await msg.answer("❗️Kanalni qo‘shib bo‘lmadi. Bot kanalga admin ekanligini tekshiring.")
@dp.message_handler(content_types=['text'], state=Add_sponser.remove)
async def ochirish(msg: types.Message, state: FSMContext):
    text = msg.text.strip()

    if text == "🔙Ortga":
        await state.finish()
        await Admin.menu.set()
        await msg.answer("👔<b>Admin panel</b>", reply_markup=admin_button_btn())
        return

    try:
        username = text.lstrip("@")
        success = remove_channel_base(username)

        if success:
            await msg.answer(f"❌ <b>@{username}</b> kanali bazadan o‘chirildi.")
        else:
            await msg.answer(f"❗️@{username} kanali topilmadi yoki allaqachon o‘chirilgan.")

        await state.finish()
        await Admin.menu.set()
        await msg.answer("👔<b>Admin panel</b>", reply_markup=admin_button_btn())

    except Exception as e:
        print(f"[Kanal o‘chirish xatosi] {e}")
        await msg.answer("❗️Kanalni o‘chirishda xatolik yuz berdi.")

@dp.message_handler(content_types=["text"],state=Posting.search)
async def start(msg:types.Message ,state : FSMContext):

    data = await state.get_data()
    is_adding = data.get("is_adding")
    
    text = msg.text

    if text != "🔙Ortga":
        anime = search_anime_base(text)
        
        if not anime:
            await msg.answer(f"🙁<b><i>{text}</i> nomi anime topilmadi ! Qayta urinib ko'ring.</b>")
            
        else:
            count = len(anime)
            if count == 1:
                
                await dp.bot.forward_message(chat_id=msg.from_user.id,from_chat_id=anime_treller_chat,message_id=anime[0][2])

                anime_id = anime[0][0]
                anime_lang = anime[0][1]
                anime_name = anime[0][3]
                anime_genre = anime[0][5]
                anime_teg = anime[0][6]
                anime_dub = anime[0][7]
                anime_serie = anime[0][8]
                anime_film = anime[0][9]
                anime_status = anime[0][11]
                anime_views = anime[0][12]
                
                if anime_status == "loading":
                    status = "OnGoing"
                elif anime_status == "finished":
                    status = "Tugallangan"
                    
                if anime_lang == "uz":
                    lang = "Ozbekcha"
                    
                elif anime_lang == "ru":
                    lang = "Ruscha"

                text = f"""
🆔 : {anime_id}
-------------------
🏷<b>Nomi : </b>{anime_name}
📑<b>Janri : </b>{anime_genre}
🎙<b>Ovoz beruvchi : </b>{anime_dub}
-------------------
🎞<b>Seriyalar soni : </b>{anime_serie}
🎥<b>Filmlar soni : </b>{anime_film}
-------------------
💬<b>Tili : </b>{lang}
-------------------
#️⃣<b>Teg : </b>{anime_teg}
📉<b>Status : </b>{status}
👁‍🗨<b>Ko'rishlar : </b>{anime_views}
"""             
                if is_adding == "True":
                    data = await state.get_data()
                    anime_list = data.get("anime_list")

                    anime_list = f"{anime_list},{anime_id}"

                    async with state.proxy() as data:
                        data["anime_list"] = anime_list

                    text = "✅<b>Anime qo'shildi</b>\n-\n<b>♻️Post qilinadigan animelar :</b>\n"
                    num = 0
                    for i in anime_list.split(","):
                        num += 1
                        name = get_anime_base(int(i))[0][3]
                        text += f"{num}.{name}\n"

                    await Posting.check.set()
                    await msg.answer(text,reply_markup=admin_check_post_clbtn())


                else:
                    await msg.answer(text)
                    await Posting.video.set()
                    async with state.proxy() as data:
                        data["anime_id"] = anime_id
                    await msg.answer("<b>🌅Animega tegishli bo'lgan video yuboring </b>",reply_markup=back_button_btn())

            else:
                a = await msg.answer("⏳",reply_markup=back_button_btn())
                await a.delete()
                await msg.answer("🗂<b>Kerakligini tanlang !</b>",reply_markup=admin_searched_animes_clbtn(anime))
            
    else:
        await state.finish()
        await Admin.menu.set()
        await msg.answer("👔<b>Admin panel</b>",reply_markup=admin_button_btn())

@dp.callback_query_handler(text_contains = "search",state=Posting.search)
async def qosh(call: types.CallbackQuery,state : FSMContext):

    anime_id = int(call.data.split(",")[1])
    data = await state.get_data()
    is_adding = data.get("is_adding")

    await call.message.delete()
    if anime_id != "back":
        
        anime = get_anime_base(anime_id)

        anime_lang = anime[0][1]
        anime_name = anime[0][3]
        anime_genre = anime[0][5]
        anime_teg = anime[0][6]
        anime_dub = anime[0][7]
        anime_serie = anime[0][8]
        anime_film = anime[0][9]
        anime_status = anime[0][11]
        anime_views = anime[0][12]
        
        if anime_status == "loading":
            status = "OnGoing"
        elif anime_status == "finished":
            status = "Tugallangan"
            
        if anime_lang == "uz":
            lang = "Ozbekcha"
            
        elif anime_lang == "ru":
            lang = "Ruscha"

        text = f"""
🆔 : {anime_id}
-------------------
🏷<b>Nomi : </b>{anime_name}
📑<b>Janri : </b>{anime_genre}
🎙<b>Ovoz beruvchi : </b>{anime_dub}
-------------------
🎞<b>Seriyalar soni : </b>{anime_serie}
🎥<b>Filmlar soni : </b>{anime_film}
-------------------
💬<b>Tili : </b>{lang}
-------------------
#️⃣<b>Teg : </b>{anime_teg}
📉<b>Status : </b>{status}
👁‍🗨<b>Ko'rishlar : </b>{anime_views}
"""     
        if is_adding == "True":
            data = await state.get_data()
            anime_list = data.get("anime_list")

            anime_list = f"{anime_list},{anime_id}"

            async with state.proxy() as data:
                data["anime_list"] = anime_list

            text = "✅<b>Anime qo'shildi</b>\n-\n<b>♻️Post qilinadigan animelar :</b>\n"
            num = 0
            for i in anime_list.split(","):
                num += 1
                name = get_anime_base(int(i))[0][3]
                text += f"{num}.{name}\n"

            await Posting.check.set()
            await call.message.answer(text,reply_markup=admin_check_post_clbtn())

        else:
            await dp.bot.forward_message(chat_id=call.from_user.id,from_chat_id=anime_treller_chat,message_id=anime[0][2])
            await call.message.answer(text)
            await Posting.video.set()

            async with state.proxy() as data:
                data["anime_id"] = anime_id

            await call.message.answer("<b>🌅Animega tegishli bo'lgan video yuboring </b>",reply_markup=back_button_btn())

    else:
        await state.finish()
        await Admin.menu.set()
        await call.message.answer("👔<b>Admin panel</b>",reply_markup=admin_button_btn())

@dp.message_handler(content_types=["text"],state=PostingSerie.search)
async def start(msg:types.Message ,state : FSMContext):

    text = msg.text

    if text != "🔙Ortga":
        anime = search_anime_base(text)
        
        if not anime:
            await msg.answer(f"🙁<b><i>{text}</i> nomi anime topilmadi ! Qayta urinib ko'ring.</b>")
            
        else:
            count = len(anime)
            if count == 1:
                
                try:
                    await dp.bot.forward_message(chat_id=msg.from_user.id,from_chat_id=anime_treller_chat,message_id=anime[0][2])
                except:
                    pass
                anime_id = anime[0][0]
                anime_lang = anime[0][1]
                anime_name = anime[0][3]
                anime_genre = anime[0][5]
                anime_teg = anime[0][6]
                anime_dub = anime[0][7]
                anime_serie = anime[0][8]
                anime_film = anime[0][9]
                anime_status = anime[0][11]
                anime_views = anime[0][12]
                
                if anime_status == "loading":
                    status = "OnGoing"
                elif anime_status == "finished":
                    status = "Tugallangan"
                    
                if anime_lang == "uz":
                    lang = "Ozbekcha"
                    
                elif anime_lang == "ru":
                    lang = "Ruscha"

                text = f"""
🆔 : {anime_id}
-------------------
🏷<b>Nomi : </b>{anime_name}
📑<b>Janri : </b>{anime_genre}
🎙<b>Ovoz beruvchi : </b>{anime_dub}
-------------------
🎞<b>Seriyalar soni : </b>{anime_serie}
🎥<b>Filmlar soni : </b>{anime_film}
-------------------
💬<b>Tili : </b>{lang}
-------------------
#️⃣<b>Teg : </b>{anime_teg}
📉<b>Status : </b>{status}
👁‍🗨<b>Ko'rishlar : </b>{anime_views}
"""             
                await msg.answer(text)
                await PostingSerie.photo.set()
                async with state.proxy() as data:
                    data["anime_id"] = anime_id
                await msg.answer("<b>🌅Animega tegishli bo'lgan rasm yuboring </b>",reply_markup=back_button_btn())

            else:
                a = await msg.answer("⏳",reply_markup=back_button_btn())
                await a.delete()
                await msg.answer("🗂<b>Kerakligini tanlang !</b>",reply_markup=admin_searched_animes_clbtn(anime))
            
    else:
        await state.finish()
        await Admin.menu.set()
        await msg.answer("👔<b>Admin panel</b>",reply_markup=admin_button_btn())

@dp.callback_query_handler(text_contains = "search",state=PostingSerie.search)
async def qosh(call: types.CallbackQuery,state : FSMContext):

    anime_id = int(call.data.split(",")[1])

    await call.message.delete()
    if anime_id != "back":
        
        anime = get_anime_base(anime_id)

        anime_lang = anime[0][1]
        anime_name = anime[0][3]
        anime_genre = anime[0][5]
        anime_teg = anime[0][6]
        anime_dub = anime[0][7]
        anime_serie = anime[0][8]
        anime_film = anime[0][9]
        anime_status = anime[0][11]
        anime_views = anime[0][12]
        
        if anime_status == "loading":
            status = "OnGoing"
        elif anime_status == "finished":
            status = "Tugallangan"
            
        if anime_lang == "uz":
            lang = "Ozbekcha"
            
        elif anime_lang == "ru":
            lang = "Ruscha"

        text = f"""
🆔 : {anime_id}
-------------------
🏷<b>Nomi : </b>{anime_name}
📑<b>Janri : </b>{anime_genre}
🎙<b>Ovoz beruvchi : </b>{anime_dub}
-------------------
🎞<b>Seriyalar soni : </b>{anime_serie}
🎥<b>Filmlar soni : </b>{anime_film}
-------------------
💬<b>Tili : </b>{lang}
-------------------
#️⃣<b>Teg : </b>{anime_teg}
📉<b>Status : </b>{status}
👁‍🗨<b>Ko'rishlar : </b>{anime_views}
"""     
        
        try:
            await dp.bot.forward_message(chat_id=call.from_user.id,from_chat_id=anime_treller_chat,message_id=anime[0][2])
        except:
            pass
        await call.message.answer(text)
        await PostingSerie.photo.set()

        async with state.proxy() as data:
            data["anime_id"] = anime_id

        await call.message.answer("<b>🌅Animega tegishli bo'lgan rasm yuboring </b>",reply_markup=back_button_btn())

    else:
        await state.finish()
        await Admin.menu.set()
        await call.message.answer("👔<b>Admin panel</b>",reply_markup=admin_button_btn())

@dp.message_handler(content_types=["text"],state=PostingSerie.photo)
async def start(msg:types.Message ,state : FSMContext):

    text = msg.text

    if text == "🔙Ortga":
        await state.finish()
        await Admin.menu.set()
        await msg.answer("👔<b>Admin panel</b>",reply_markup=admin_button_btn())

    else:
        pass

@dp.message_handler(content_types=["photo"],state=PostingSerie.photo)
async def start(msg:types.Message ,state : FSMContext):


    data = await state.get_data()
    anime_id = int(data.get("anime_id"))

    a = await msg.answer(". . .",reply_markup=back_button_btn())
    await a.delete()

    path = f"handlers/post_media/anime.jpg"
    a = await msg.answer("♻️<b>Serverga yuklanmoqda</b> . . .")

    anime = get_anime_base(anime_id)
    name = anime[0][3]
    serie = anime[0][8]
    genre = f"""#{anime[0][5].replace(","," #")}"""
    language = anime[0][1]
    if language == "uz":
        language = "🇺🇿O'zbekcha"
    else:
        language = "🇷🇺Ruscha"

    await msg.photo[-1].download(destination_file=path)
    await asyncio.sleep(1)

    a = await a.edit_text("♻️<b>Post uchun rasm yasalmoqda</b> . . .")
    path_output = image_making()
    await asyncio.sleep(1)
    a = await a.edit_text("♻️<b>Keraksiz fayllar o'chirilmoqda</b> . . .")
    await asyncio.sleep(1)
    a = await a.edit_text("♻️<b>Yuklanmoqda</b> . . .")

    await msg.answer_chat_action(action="upload_photo")

    caption = f"""
🔍<b>Yangi qism qo'shildi</b>
°•───────────────────°
🏷️ <b>Nomi :</b> {name}
🎞 <b>Qism :</b> {serie}
📑 <b>Janri :</b> {genre}
🌐 <b>Tili :</b> {language}
"""

    await PostingSerie.action.set()
    photo = InputFile(path_output)
    await msg.answer_photo(photo=photo,caption=caption,reply_markup=serie_posting_action_clbtn())

@dp.message_handler(content_types=["any"],state=Posting.video)
async def start(msg:types.Message ,state : FSMContext):
    
    text = msg.text
    data = await state.get_data()
    anime_id = int(data.get("anime_id"))
    anime_list = data.get("anime_list")

    if not anime_list:
        anime_list = f"{anime_id}"
        
    else:
        anime_list = f"{anime_list},{anime_id}"

    if text != "🔙Ortga":

        if msg.video.file_size < 30000000:
            await msg.answer("🖼<b>Video serverga yuklanyapti kutib turing !</b>")

            try:
                await msg.video.download(destination_file=f"post_{msg.from_user.id}/video.mp4")
                await Posting.check.set()
                a = await msg.reply(". . .",reply_markup=back_button_btn())
                await a.delete()

                async with state.proxy() as data:
                    data["anime_list"] = anime_list

                await msg.reply("📤<b>Post qilishni tasdiqlaysizmi ?</b>",reply_markup=admin_check_post_clbtn())
            except:
                shutil.rmtree(f"post_{msg.from_user.id}")
                await msg.answer("🖼<b>Xatolik yuz berdi. Boshqa video yuborib ko'ring !</b>")        
        else:
            await msg.answer("🖼<b>Video hajmi 30mb dan kam bo'lishi kerak !</b>")
            
    else:
        await state.finish()
        await Admin.menu.set()
        await msg.answer("✅<b>Bekor qilindi</b>",reply_markup=admin_button_btn())

@dp.message_handler(content_types=["any"],state=Posting.check)
async def start(msg:types.Message ,state : FSMContext):
    await msg.delete()

@dp.callback_query_handler(text_contains = "select",state=PostingSerie.action)
async def qosh(call: types.CallbackQuery,state : FSMContext):

    command = call.data.split(",")[1]

    data = await state.get_data()
    anime_id = int(data.get("anime_id"))

    await call.message.delete()

    if command == "post":
        a = await call.message.answer("<b>♻️Post qilinmoqda</b>")

        anime = get_anime_base(anime_id)
        name = anime[0][3]
        serie = anime[0][8]
        genre = f"""#{anime[0][5].replace(","," #")}"""
        language = anime[0][1]
        if language == "uz":
            language = "🇺🇿O'zbekcha"
        else:
            language = "🇷🇺Ruscha"

        caption = f"""
🔍<b>Yangi qism qo'shildi</b>
°•───────────────────°
🏷️ <b>Nomi :</b> {name}
🎞 <b>Qism :</b> {serie}
📑 <b>Janri :</b> {genre}
🌐 <b>Tili :</b> {language}
"""

        photo = InputFile("handlers/post_media/output.jpg")
        a=-1002023259288

        await dp.bot.send_photo(chat_id=a,photo=photo,caption=caption,reply_markup=serie_post_link_clbtn(anime_id))
        os.remove("handlers/post_media/output.jpg")

        await a.delete()
        await state.finish()
        await Admin.menu.set()
        await call.message.answer("<b>✅Post qilindi</b>",reply_markup=admin_button_btn())


    else:
        await state.finish()
        await Admin.menu.set()
        await call.message.answer("<b>✅Bekor qilindi</b>",reply_markup=admin_button_btn())

@dp.callback_query_handler(text_contains = "select",state=Posting.check)
async def qosh(call: types.CallbackQuery,state : FSMContext):

    command = call.data.split(",")[1]

    if command == "yeah":
        data = await state.get_data()
        anime_id = int(data.get("anime_id"))
        anime_list = data.get("anime_list")
        await call.answer("♻️Anime post qilinishga tayyorlanyapti !")

        anime = get_anime_base(anime_id)

        anime_lang = anime[0][1]
        anime_name = anime[0][3]
        anime_genre = anime[0][5]
        anime_dub = anime[0][7]
        anime_serie = anime[0][8]
        anime_status = anime[0][11]

        if anime_status == "finished":
            anime_status = "🟢Tugallangan"
        elif anime_status == "loading":
            anime_status = "🟡OnGoing"
        
        if anime_lang == "uz":
            lang = "Ozbekcha"
            
        elif anime_lang == "ru":
            lang = "Ruscha"

        text = f"""
°•────────•✨•────────•°
🏷<b>Nomi :</b> {anime_name}
°•───────────────────
📑<b>Janri :</b> #{anime_genre.replace("#","").replace(","," #")}
🎙<b>Ovoz beruvchi :</b> {anime_dub}
°•───────────────────
🎞<b>Seriyalar soni :</b> {anime_serie}
°•───────────────────
💬<b>Tili :</b> {lang}
°•───────────────────
📉<b>Status :</b> {anime_status}
""" 
        

        a = await dp.bot.send_video(chat_id=-1002023259288,video=open(f"post_{call.from_user.id}/video.mp4","rb"),caption=text,reply_markup=post_watching_clbtn(anime[0][0],anime_list))
        message_id = a.message_id
        await call.message.delete()
        await state.finish()
        await Admin.menu.set()
        shutil.rmtree(f"post_{call.from_user.id}")
        await call.message.answer(f"✅<b>Muvaffaqiyatli post qilindi</b>. <a href='https://t.me/Aniduble/{message_id}'>👁‍🗨Postni ko'rish</a>",reply_markup=admin_button_btn(),disable_web_page_preview=True)

    elif command == "add":
        await Posting.search.set()
        await call.message.delete()
        async with state.proxy() as data:
            data["is_adding"] = "True"
        await call.message.answer("<b>➕Qo'shish uchun anime nomini yuboring</b>",reply_markup=back_button_btn())

    else:
        await call.message.delete()
        await state.finish()
        await Admin.menu.set()
        shutil.rmtree(f"post_{call.from_user.id}")
        await call.message.answer("✅<b>Bekor qilindi</b>",reply_markup=admin_button_btn())

@dp.callback_query_handler(text_contains = "type",state=Edit_serie.type)
async def qosh(call: types.CallbackQuery,state : FSMContext):
    
    type = call.data.split(",")[1]
    
    if type == "back":
        await call.message.delete()
        await state.finish()
        await Admin.menu.set()
        await call.message.answer("✅<b>Bekor qilindi</b>",reply_markup=admin_button_btn())

    else:
        await call.message.delete()
        await call.message.answer("<b>📝Seriasi tahrirlanishi kerak bo'lgan anime nomini kiriting</b>",reply_markup=back_button_btn())
        await Edit_serie.search.set()

@dp.message_handler(content_types=["video"],state=Add_anime.treller)
async def start(msg:types.Message ,state : FSMContext):
    caption = msg.caption 
    is_forwarded = [msg.forward_from_chat,msg.forward_from]

    if caption != None:
        await msg.answer("❗️<b>Yuborgan videoingizda Text bo'lmasligi zarur !</b>")
        
    elif is_forwarded[0] != None or is_forwarded[1] != None:
        await msg.answer("❗️<b>Yuborgan videoingiz tepasida kanaldan yoki kimdandir yuborilgan degan so'z bo'lmasligi kerak !</b>")
    else:
        treller_message_id = msg.message_id
        async with state.proxy() as data:
            data["treller"] = treller_message_id
        
        await Add_anime.name.set()
        await msg.answer("🏷<b>Anime nomini yuboring !</b>")

@dp.message_handler(text_contains = "Ortga",state=Add_staff.adding)
async def start(msg:types.Message ,state : FSMContext):
    await state.finish()
    await Admin.menu.set()
    await msg.answer("✅<b>Bekor qilindi</b>",reply_markup=admin_button_btn())

@dp.message_handler(content_types=["text"],state=Add_staff.adding)
async def start(msg:types.Message ,state : FSMContext):
    text = msg.text
    try:
        user_id = int(text)
        
        user = get_user_base(user_id)
        if not user:
            await msg.answer("❗️<b>Bunday ID dagi user topilmadi !</b>")
        else:
            update_user_staff_base(user_id)
            await state.finish()
            await Admin.menu.set()
            try:
                await dp.bot.send_message(chat_id=user_id,text="👔Siz <b>Admin tomonidan Staff</b> darajasiga ko'tarildingiz ! <b>/admin</b> orqali <b>Staff panelga o'tishingiz mumkin !</b>")
            except:
                pass
            await msg.answer("<b>✅Ushu user Staff darajasiga ko'tarildi !</b>",reply_markup=admin_button_btn())
    
    except:
        await msg.answer("❗️<b>Bu ID emas</b>")

@dp.callback_query_handler(text_contains = "staff",state=Add_staff.adding)
async def qosh(call: types.CallbackQuery,state : FSMContext):
    
    user_id = int(call.data.split(",")[1])
    update_user_staff_delete_base(user_id)
    
    await call.message.delete()
    
    await state.finish()
    await Admin.menu.set()
    try:
        await dp.bot.send_message(chat_id=user_id,text="❌Siz <b>Admin tomonidan Staff</b> darajasidan olindingiz !")
    except:
        pass
    await call.message.answer("<b>✅Ushu user Stafflikdan bo'shatildi !</b>",reply_markup=admin_button_btn())

@dp.callback_query_handler(text_contains = "add",state=Add_staff.adding)
async def qosh(call: types.CallbackQuery,state : FSMContext):
    await Add_staff.adding.set()
    await call.message.answer("👔<b>Staff qilmoqchi</b> bo'lgan user ID sini yuboring !",reply_markup=back_button_btn())
    await call.message.delete()

@dp.callback_query_handler(text_contains = "exit",state=Add_staff.adding)
async def qosh(call: types.CallbackQuery,state : FSMContext):
    await state.finish()
    await Admin.menu.set()
    await call.message.delete()
    await call.message.answer("👔<b>Admin panel</b>",reply_markup=admin_button_btn())

@dp.callback_query_handler(text_contains = "add",state=Add_sponser.menu)
async def qosh(call: types.CallbackQuery,state : FSMContext):
    await Add_sponser.adding.set()
    await call.message.answer("🔒<b>Majburiy a'zo qo'shish</b> uchun <b>Kanal ID</b> sini yuboring\n❗️Bo't siz <b>majbury a'zo qilmoqchi bo'lgan kanalda</b> admin etib tayinlangan bo'lishi zarur !",reply_markup=back_button_btn())
    await call.message.delete()
    
@dp.message_handler(content_types=["any"],state=Add_sponser.adding)
async def start(msg:types.Message ,state : FSMContext):
    
    channel_id = msg.text
    
    if channel_id == "🔙Ortga":
        await state.finish()
        await Admin.menu.set()
        await msg.answer("👔<b>Admin panel</b>",reply_markup=admin_button_btn())
    else:
        try:
            channel_id = int(msg.forward_from_chat.id)
            try:
                chat = await dp.bot.get_chat(chat_id=channel_id)
                await dp.bot.get_chat_administrators(chat_id=channel_id)
                if msg.chat.type == "private":
                    channel_id = chat.id
                    name = chat.title
                    link = chat.invite_link
                else:
                    channel_id = chat.id
                    name = chat.title
                    link = f"https://t.me/{chat.username}"
                    
                add_sponsor_base(channel_id,name,link)
                await state.finish()
                await Admin.menu.set()
                await msg.answer("✅Ushbu kanal <b>Majbury a'zoga qo'shildi !</b>",reply_markup=admin_button_btn())
                
            except:
                await msg.answer("❗️<b>Bot kanalga Admin qilinmagan !</b>")
        except:
            await msg.answer("❗️<b>Xabar kanal yoki guruh nomidan ulashilmagan</b>")
        
@dp.callback_query_handler(text_contains = "sponsor",state=Add_sponser.menu)
async def qosh(call: types.CallbackQuery,state : FSMContext):
    channel_id = call.data.split(",")[1]
    delete_sponsor_base(int(channel_id))
    await dp.bot.leave_chat(chat_id=channel_id)
    await state.finish()
    await Admin.menu.set()
    await call.message.answer("✅<b>Ushbu kanal</b> Majbury a'zodan <b>o'chirib yuborildi !</b>",reply_markup=admin_button_btn())
    await call.message.delete()
    
@dp.callback_query_handler(text_contains = "exit",state=Add_sponser.menu)
async def qosh(call: types.CallbackQuery,state : FSMContext):
    await state.finish()
    await Admin.menu.set()
    await call.message.delete()
    await call.message.answer("👔<b>Admin panel</b>",reply_markup=admin_button_btn())

async def anime_serie_edit_func(anime_id,anime_name,msg,call,serie_num,serie_id,state):

    if not serie_num:
        serie_num = get_id_to_num_serie_base(serie_id) 

    series = get_series_base(anime_id)
    word = "seriya"

    text = f"""
🆔<b>anime :</b> {anime_id}
🏷Nomi : {anime_name}
--------------
🆔<b>{word} :</b> {series[serie_num-1][1]}
🌟<b>Sifat :</b> {series[serie_num-1][3]}
💾<b>Qism :</b> {series[serie_num-1][2]}
"""
        
    if not msg :
        a = await dp.bot.forward_message(chat_id=call.from_user.id,from_chat_id=anime_series_chat,message_id=series[serie_num-1][1])
        await call.message.answer(text,reply_markup=searched_series_list_clbtn(series,serie_num))
    if not call :
        a = await dp.bot.forward_message(chat_id=msg.from_user.id,from_chat_id=anime_series_chat,message_id=series[serie_num-1][1])
        await msg.answer(text,reply_markup=searched_series_list_clbtn(series,serie_num))

    async with state.proxy() as data:
        data["serie"] = a.message_id
        data["name"] = anime_name

@dp.message_handler(content_types=["text"],state=Edit_serie.search)
async def start(msg:types.Message ,state : FSMContext):
    
    text = msg.text
    
    if text != "🔙Ortga":
        anime = search_anime_base(text)
    
        if not anime:
            await msg.answer(f"🙁<b><i>{text}</i> nomi anime topilmadi ! Qayta urinib ko'ring.</b>")
            
        else:
            a = await msg.answer("⏳",reply_markup=back_button_btn())
            await a.delete()
            count = len(anime)
            if count == 1:
                await Edit_serie.series_menu.set()
                try:
                    await anime_serie_edit_func(anime[0][0],anime[0][3],msg,None,1,None,state)
                except:
                    await state.finish()
                    await Admin.menu.set()
                    await msg.answer(f"🙁<b><i>{text}</i> nomli animeda hali seriyalar mavjud emas !</b>",reply_markup=admin_button_btn())
            else:
                a = await msg.answer("⏳",reply_markup=back_button_btn())
                await a.delete()
                await msg.answer("🗂<b>Kerakligini tanlang !</b>",reply_markup=admin_searched_animes_clbtn(anime))
    
    else:
        await state.finish()
        await Admin.menu.set()
        await msg.answer("👔<b>Admin panel</b>",reply_markup=admin_button_btn())

@dp.callback_query_handler(text_contains = "search",state=Edit_serie.search)
async def qosh(call: types.CallbackQuery,state : FSMContext):

    content_id = int(call.data.split(",")[1])
    await call.message.delete()
    if content_id != "back":
        a = await call.message.answer("⏳",reply_markup=back_button_btn())
        await a.delete()
        
        anime = get_anime_base(content_id)

        await Edit_serie.series_menu.set()
        # try:
        await anime_serie_edit_func(anime[0][0],anime[0][3],None,call,1,None,state)
        # except:
        #     await call.answer(f"🙁Ushbu animeda hali filmlar mavjud emas !")

    else:
        await state.finish()
        await Admin.menu.set()
        await call.message.answer("👔<b>Admin panel</b>",reply_markup=admin_button_btn())

@dp.callback_query_handler(text_contains = "serie",state=Edit_serie.series_menu)
async def qosh(call: types.CallbackQuery,state : FSMContext):
    
    data = await state.get_data()
    forwarded_serie = data.get("serie")
    anime_name = data.get("name")

    serie_id = int(call.data.split(",")[1])
    anime_id = int(call.data.split(",")[2])
    command = call.data.split(",")[3]

    last_serie_id = int(get_last_serie_base(anime_id))

    if command != "back":

        if command == "now":

            is_last = False

            if serie_id == last_serie_id:
                is_last = True
            else:
                pass

            a = await call.message.answer("⏳",reply_markup=back_button_btn())
            await a.delete()
            await Edit_serie.editing_menu.set()
            await call.message.edit_reply_markup(searched_series_edit_clbtn(serie_id,is_last,anime_id))
            async with state.proxy() as data:
                data["name"] = anime_name
                
        else:
            serie_num = int(command)
            try:
                await dp.bot.delete_message(chat_id=call.from_user.id,message_id=forwarded_serie)
            except:
                pass
            await call.message.delete()
            await anime_serie_edit_func(anime_id,anime_name,None,call,serie_num,serie_id,state)

    else:
        try:
            await dp.bot.delete_message(chat_id=call.from_user.id,message_id=forwarded_serie)
        except:
            pass
        await call.message.delete()
        await state.finish()
        await Admin.menu.set()
        await call.message.answer("Admin panel",reply_markup=admin_button_btn())

@dp.callback_query_handler(text_contains = "edit",state=Edit_serie.editing_menu)
async def qosh(call: types.CallbackQuery,state : FSMContext):
    
    serie_id = int(call.data.split(",")[1])
    command = call.data.split(",")[2]
    anime_id = call.data.split(",")[3]
    data = await state.get_data()
    anime_name = data.get("name")
    serie_num = get_id_to_num_serie_base(serie_id)

    if command != "back":

        if command == "new":

            await call.message.delete()
            await state.finish()
            await Edit_serie.upload_new.set()
            await call.message.answer(f"❗️<b><i>{anime_name}</i> animesining <i>{serie_num}-seriyasi</i> uchun boshqa seriya yuboring !</b>",reply_markup=back_button_btn())
           
            async with state.proxy() as data:
                data["serie"] = serie_id
                data["name"] = anime_name
                data["anime_id"] = anime_id

        elif command == "delete":
            await call.message.delete()
            await Edit_serie.delete_serie.set()
            async with state.proxy() as data:
                data["name"] = anime_name
                data["num"] = serie_num
                data["anime_id"] = anime_id

            await call.message.answer(f"⁉️<b><i>{anime_name}</i> animesining <i>{serie_num}-seriyasini</i> o'chirishni tasdiqlayszmi ?</b>",reply_markup=are_you_sure_clbtn(serie_id))
            
    else:
        series = get_series_base(anime_id)

        await state.finish()
        await Edit_serie.series_menu.set()
        async with state.proxy() as data:
            data["name"] = anime_name

        await call.message.edit_reply_markup(searched_series_list_clbtn(series,serie_num))

@dp.message_handler(content_types=["video","text"],state=Edit_serie.upload_new)
async def start(msg:types.Message ,state : FSMContext):

    data = await state.get_data()
    serie_id = int(data.get("serie"))
    anime_id = int(data.get("anime_id"))
    anime_name = data.get("name")
    forwarded_serie= data.get("serie")
    serie_num = get_id_to_num_serie_base(serie_id)

    text= msg.text

    if text != "🔙Ortga":
        caption = msg.caption 
        is_forwarded = [msg.forward_from_chat,msg.forward_from]
        
        if caption != None:
            await msg.answer("📄<b>Yuborgan videoingizda Text bo'lmasligi zarur !</b>")
            
        elif is_forwarded[0] != None or is_forwarded[1] != None:
            await msg.answer("👤<b>Yuborgan videoingiz tepasida kanaldan yoki kimdandir yuborilgan degan so'z bo'lmasligi kerak !</b>")
            
        else:
            new_serie = msg.message_id
            try:
                await dp.bot.delete_message(chat_id=anime_series_chat,message_id=serie_id)
            except:
                pass

            quality = f"{msg.video.height}p"
            a = await dp.bot.forward_message(chat_id=anime_series_chat,from_chat_id=msg.from_user.id,message_id=new_serie)
            new_serie_id = a.message_id

            update_serie_base(serie_id,new_serie_id,quality)
            await msg.answer(f"🟢<b><i>{anime_name}</i> animeisning <i>{serie_num} - seriyasi</i> yangisiga alishtrildi !</b>")

            await asyncio.sleep(1)

            await state.finish()
            await Edit_serie.series_menu.set()

            await anime_serie_edit_func(anime_id,anime_name,msg,None,serie_num,new_serie_id,state)

    else:
        try:
            await dp.bot.delete_message(chat_id=msg.from_user.id,message_id=forwarded_serie)
        except:
            pass
        await state.finish()
        await Edit_serie.series_menu.set()
        await anime_serie_edit_func(anime_id,anime_name,msg,None,serie_num,serie_id,state)

@dp.callback_query_handler(text_contains = "sure",state=Edit_serie.delete_serie)
async def qosh(call: types.CallbackQuery,state : FSMContext):

    is_sure = call.data.split(",")[1]

    data = await state.get_data()
    anime_name = data.get("name")
    forwarded_serie = data.get("serie")
    serie_num = data.get("num")
    anime_id = int(data.get("anime_id"))
    serie_id = int(call.data.split(",")[2])

    if is_sure == "yeah":
        
        try:
            await dp.bot.delete_message(chat_id=anime_series_chat,message_id=serie_id)
        except:
            pass

        delete_serie_base(serie_id)
        update_anime_serie_count_minus_base(anime_id)
        await call.message.delete()
        await state.finish()
        await Admin.menu.set()
        await call.message.answer(f"<b>🟡<i>{anime_name}</i> animesining <i>{serie_num}</i> - seriyasi o'chirildi !</b>",reply_markup=admin_button_btn())
    
    else:
        try:
            await dp.bot.delete_message(chat_id=call.from_user.id,message_id=forwarded_serie)
        except:
            pass
        await state.finish()
        await Edit_serie.series_menu.set()
        await anime_serie_edit_func(anime_id,anime_name,None,call,serie_num,serie_id,state)

async def anime_editing_func(anime_id,msg,call,is_about,is_edit):

    anime_data = get_anime_base(anime_id)
    anime_id = anime_data[0][0]
    anime_lang = anime_data[0][1]
    anime_treller_id = anime_data[0][2]
    anime_name = anime_data[0][3]
    anime_about = anime_data[0][4]
    anime_genre = anime_data[0][5]
    anime_teg = anime_data[0][6]
    anime_dub = anime_data[0][7]
    anime_serie = anime_data[0][8]
    anime_film = anime_data[0][9]
    anime_is_vip = anime_data[0][10]
    anime_status = anime_data[0][11]
    anime_views = anime_data[0][12]
    
    if not msg:
        chat_id=call.from_user.id
    else:
        chat_id = msg.from_user.id
    
    if is_edit == False:
        try:
            await dp.bot.forward_message(chat_id=chat_id,from_chat_id=anime_treller_chat,message_id=anime_treller_id)
        except:
            pass
    
    if anime_status == "loading":
        status = "🟡OnGoing"
    elif anime_status == "finished":
        status = "🟢Tugallangan"
        
    if anime_lang == "uz":
        lang = "🇺🇿Ozbekcha"
        
    elif anime_lang == "ru":
        lang = "🇷🇺Ruscha"

    if anime_is_vip == 1:
        anime_vip = "🟢Yoniq"
    elif anime_is_vip == 0:
        anime_vip = "🔴O'chiq"

    if is_about == False:
        text = f"""
🆔 : {anime_id}
-------------------
🏷<b>Nomi : </b>{anime_name}
📑<b>Janri : </b>{anime_genre}
🎙<b>Ovoz beruvchi :</b> {anime_dub}
-------------------
🎞<b>Seriyalar soni :</b> {anime_serie}
🎥<b>Filmlar soni :</b> {anime_film}
-------------------
💬<b>Tili : </b>{lang}
⚡️<b>AniPass : </b>{anime_vip}
-------------------
#️⃣<b>Teg : </b>{anime_teg}
📉<b>Status :</b> {status}
👁‍🗨<b>Ko'rishlar :</b> {anime_views}
""" 
    else:
        text = f"""
-------------------
{anime_about}
-------------------
"""
    
    if is_edit == True:   
        if not msg:
            await call.message.edit_text(text,reply_markup=edit_anime_clbtn(anime_status,anime_id,is_about,anime_is_vip))
        else:
            await msg.edit_text(text,reply_markup=edit_anime_clbtn(anime_status,anime_id,is_about,anime_is_vip))
    if is_edit == False:   
        if not msg:
            await call.message.answer(text,reply_markup=edit_anime_clbtn(anime_status,anime_id,is_about,anime_is_vip))
        else:
            await msg.answer(text,reply_markup=edit_anime_clbtn(anime_status,anime_id,is_about,anime_is_vip))

@dp.message_handler(content_types=["text"],state=Edit_anime.search)
async def start(msg:types.Message ,state : FSMContext):
    
    text = msg.text
    if text != "🔙Ortga":
        anime = search_anime_base(text)
    
        if not anime:
            await msg.answer(f"🙁<b><i>{text}</i> nomi anime topilmadi ! Qayta urinib ko'ring.</b>")
            
        else:
            a = await msg.answer("⏳",reply_markup=back_button_btn())
            await a.delete()
            
            count = len(anime)
            if count == 1:
                await msg.answer("✅<b>Anime topildi !</b>")
                
                await Edit_anime.editing_menu.set()
                await anime_editing_func(anime[0][0],msg,None,False,False)
                
            else:
                await msg.answer("🗂<b>Kerakligini tanlang !</b>",reply_markup=admin_searched_animes_clbtn(anime))

    else:
        await state.finish()
        await Admin.menu.set()
        await msg.answer("👔<b>Admin panel</b>",reply_markup=admin_button_btn())

@dp.callback_query_handler(text_contains = "search",state=Edit_anime.search)
async def qosh(call: types.CallbackQuery,state : FSMContext):
    
    content_id = int(call.data.split(",")[1])
    await call.message.delete()
    if content_id != "back":
        a = await call.message.answer("⏳",reply_markup=back_button_btn())
        await a.delete()
        await Edit_anime.editing_menu.set()
        await anime_editing_func(content_id,None,call,False,False)
    
    else:
        await state.finish()
        await Admin.menu.set()
        await call.message.answer("Admin panel",reply_markup=admin_button_btn())

@dp.callback_query_handler(text_contains = "edit",state=Edit_anime.editing_menu)
async def qosh(call: types.CallbackQuery,state : FSMContext):
    
    command = call.data.split(",")[1]
    content_id = call.data.split(",")[2]
    next_states = True
    
    if command == "about_view":
        await anime_editing_func(content_id,None,call,True,True)
        next_states = False
    elif command == "basic_view":
        await anime_editing_func(content_id,None,call,False,True)
        next_states = False 
    elif command == "about":
        text = "<b>📃Ushbu anime uchun yangi Anime haqida text yuboring !</b>"
    
    elif command == "name":
        text = "<b>🏷Ushbu anime uchun yangi Nom yuboring !</b>"
        
    elif command == "genre":
        text = "<b>📑Ushbu anime uchun yangi Janr yuboring !</b>"
        
    elif command == "dub":
        text = "<b>🎙Ushbu anime uchun yangi Ovoz beruvchi yuboring !</b>"
    
    elif command == "teg":
        text = "<b>#️⃣Ushbu anime uchun yangi teg yuboring !</b>"
    
    elif command == "add_lang":
        text = "<b>🆔Ushbu anime Ikkinchi til qilib qo'shilishi kerak bo'lgan animening ID sini yuboring !</b>"
    
    elif command == "edit_lang":
        text = "<b>💬Ushbu anime uchun yangi 2-til yuboring !</b>"

    elif command == "exit":
        await call.message.delete()
        await state.finish()
        await Admin.menu.set()
        await call.message.answer("Admin panel",reply_markup=admin_button_btn())
        next_states = False
    
    elif command == "vip_on" or command == "vip_off":
        if command == "vip_on":
            text = "⚡️Vip yoqildi"
            additional = 1
        if command == "vip_off":
            text = "⚡️Vip o'chirildi"
            additional = 0

        update_anime_informations_base(content_id,"is_vip",additional)

        await call.answer(text,show_alert=True)
        await Edit_anime.editing_menu.set()
        await anime_editing_func(content_id,None,call,False,True)
        next_states = False

    elif command == "activate" or command == "stop":
        if command == "activate":
            text = "🟡<b>Ushbu animeni aktivlashtrishni tasdiqlayszmi ?</b>"
            additional = "loading"
        if command == "stop":
            text = "🟢<b>Ushbu animeni Tugallashni tasdiqlayszmi ?</b>"
            additional = "finished"
            
        next_states = False
        await call.message.delete()
        await call.message.answer(f"{text}",reply_markup=are_you_sure_clbtn(command,content_id,additional))
        
    elif command == "lang":
        lang_anime = get_anime_base(content_id)[0][1]
        if lang_anime == "uz":
            lang = "<b>O'zbekcha. Uni rus tiliga o'tkazishni tasdiqlaysizmi ?</b>"
            new_lang = "ru"
        if lang_anime == "ru":
            lang = "<b>Ruscha. Uni o'zbek tiliga o'tkazishni tasdiqlyasizmi ?</b>"
            new_lang = "uz"
        next_states = False
        await call.message.delete()
        await call.message.answer(f"♻️<b>Ushbu anime tili {lang}</b>",reply_markup=are_you_sure_clbtn(new_lang,content_id))
    
    elif command == "delete":
        next_states = False
        await call.message.delete()
        await call.message.answer(f"⁉️<b>Ushbu animeni o'chirishni tasdiqlayszmi ?</b>",reply_markup=are_you_sure_clbtn(command,content_id))

    if next_states == True:
        await call.message.delete()
        await Edit_anime.edit_about.set()
        async with state.proxy() as data:
            data["command"] = command
            data["anime_id"] = content_id
        await call.message.answer(text,reply_markup=back_button_btn())
    
@dp.message_handler(content_types=["text"],state=Edit_anime.edit_about)
async def start(msg:types.Message ,state : FSMContext):
        
    data = await state.get_data()
    command = data.get("command")

    content_id = int(data.get("anime_id"))
    
    text = msg.text
    
    next_state = True
    
    if text != "🔙Ortga":
        if command == "genre":
            if len(text.split(",")) < 3:
                next_state = False
                await msg.answer("❗️<b>Minimal 3 ta janr kiriting !</b>")
                
            else:
                text = text.replace(" ","")
                
        if command == "teg":
            if len(text.split(",")) < 3:
                next_state = False
                await msg.answer("❗️<b>Minimal 3 ta teg kiriting !</b>")
                
            else:
                text = text.replace(" ","")
                
        if command == "add_lang" or command == "edit_lang":
            try:
                text = int(text)
                anime = get_anime_base(text)
                anime_edited = get_anime_base(content_id)
                if not anime:
                    next_state = False 
                    await msg.answer("❗️<b>Bunday ID li anime topilmadi ! Boshqa ID yuboring</b>")

                else:
                    if anime[0][1] == anime_edited[0][1]:
                        next_state = False 
                        await msg.answer("❗️<b>Bu animeni 2- til qilib qo'sha olmaysiz, Sababi bu animening tili siz 2-til qilib qo'shmoqchi bo'lgan anime tili bilan bir xil ! Boshqa ID yuboring</b>")
                    else:
                        additional= f"{text},{anime[0][1]}"
                        next_state = False 
                        await msg.answer("<b>⚠️Qo'shishni tasdiqlaysizmi ?</b>",reply_markup=are_you_sure_clbtn(command,content_id,additional))
                        
            except:
                next_state = False
                await msg.answer("❗️<b>Bu ID emas</b>")
                
        if next_state == True:
        
            async with state.proxy() as data:
                data["text"] = text
            await msg.answer("<b>⚠️Tahrirlashni tasdiqlayszmi ?</b>",reply_markup=are_you_sure_clbtn(command,content_id))

    else:
        await Edit_anime.editing_menu.set()
        a = await msg.answer("✅<b>Bekor qilindi !</b>",reply_markup=back_button_btn())
        await asyncio.sleep(1)
        await a.delete()
        await anime_editing_func(content_id,msg,None,False,False)

@dp.callback_query_handler(text_contains = "sure",state=Edit_anime.all_states)
async def qosh(call: types.CallbackQuery,state : FSMContext):
    
    sure = call.data.split(",")[1]
    command = call.data.split(",")[2]

    content_id = call.data.split(",")[3]
    
    data = await state.get_data()
    text = data.get("text")
    
    next_states = True

    if sure == "yeah":
        if command == 'about':
            key = "about"
            call_text = "✅Anime haqida text yangilandi"
            
        elif command == 'name':
            key = "name"
            call_text = "✅Anime Nomi yangilandi"
        
        elif command == 'genre':
            key = "genre"
            call_text = "✅Anime Janri yangilandi"
            
        elif command == 'dub':
            key = "dub"
            call_text = "✅Anime Ovoz beruvchisi yangilandi"
        
        elif command == 'teg':
            key = "teg"
            call_text = "✅Anime Teg yangilandi"
        
        elif command == 'stop' or command == 'activate':
            key = "status"
            
            if command == 'stop':
                call_text = "✅Anime tugallandi !"
            elif command == 'activate':
                call_text = "✅Anime aktivlashtrildi !"
                
            text = call.data.split(",")[4]

        elif command == 'add_lang':
            key = "another_lang"
            text = call.data.split(",")[4]
            call_text = "✅Animega 2-til qo'shildi !"
        
        
        elif command == "uz":
            key = "lang"
            call_text = "✅Anime tili o'zbek tiliga o'zgartrildi !"
            text = "uz"

        elif command == "ru":
            key = "lang"
            call_text = "✅Anime tili Rus tiliga o'zgartrildi !"
            text = "ru"
        
        elif command == "delete":
            next_states = False

            delete_anime_base(content_id)
            update_statistics_minus_anime_base()
            await call.message.delete()
            await state.finish()
            await Admin.menu.set()
            await call.message.answer("⚠️<b>Anime o'chirib yuborildi !</b>",reply_markup=admin_button_btn())

        if next_states == True:
            await call.message.delete()
            update_anime_informations_base(content_id,key,text)
            await call.answer(call_text,show_alert=True)
            await Edit_anime.editing_menu.set()
            await anime_editing_func(content_id,None,call,False,False)
        
    else:
        await call.message.delete()
        await Edit_anime.editing_menu.set()
        await call.answer("✅Bekor qilindi !")
        await anime_editing_func(content_id,None,call,False,False)

async def serie_adding_text_func(anime_id,msg,call):

    anime_data = get_anime_base(anime_id)
    
    anime_id = anime_data[0][0]
    anime_lang = anime_data[0][1]
    anime_treller_id = anime_data[0][2]
    anime_name = anime_data[0][3]
    anime_genre = anime_data[0][5]
    anime_teg = anime_data[0][6]
    anime_dub = anime_data[0][7]
    anime_serie = anime_data[0][8]
    anime_film = anime_data[0][9]
    anime_vip = anime_data[0][10]
    anime_status = anime_data[0][11]
    anime_views = anime_data[0][12]

    if anime_vip == 1:
        anime_vip = "🟢Yoniq"
    elif anime_vip == 0:
        anime_vip = "🔴O'chiq"
    
    if not msg:
        chat_id=call.from_user.id
    else:
        chat_id = msg.from_user.id
        
    await dp.bot.forward_message(chat_id=chat_id,from_chat_id=anime_treller_chat,message_id=anime_treller_id)
    
    if anime_status == "loading":
        status = "OnGoing"
    elif anime_status == "finished":
        status = "Tugallangan"
        
    if anime_lang == "uz":
        lang = "Ozbekcha"
        
    elif anime_lang == "ru":
        lang = "Ruscha"

    text = f"""
🆔 : {anime_id}
-------------------
🏷<b>Nomi : </b>{anime_name}
📑<b>Janri : </b>{anime_genre}
🎙<b>Ovoz beruvchi : </b>{anime_dub}
-------------------
🎞<b>Seriyalar soni : </b>{anime_serie}
🎥<b>Filmlar soni : </b>{anime_film}
-------------------
💬<b>Tili : </b>{lang}
⚡️<b>AniPass : </b>{anime_vip}
-------------------
#️⃣<b>Teg : </b>{anime_teg}
📉<b>Status : </b>{status}
👁‍🗨<b>Ko'rishlar : </b>{anime_views}
""" 

    if not msg:
        await call.message.answer(text,reply_markup=anime_add_serie_clbtn(anime_status,anime_id))
    else:
        await msg.answer(text,reply_markup=anime_add_serie_clbtn(anime_status,anime_id))

@dp.message_handler(content_types=["text"],state=Add_serie.search)
async def start(msg:types.Message ,state : FSMContext):
    
    text = msg.text

    if text != "🔙Ortga":
        anime = search_anime_base(text)
        
        if not anime:
            await msg.answer(f"🙁<b><i>{text}</i> nomi anime topilmadi ! Qayta urinib ko'ring.</b>")
            
        else:
            a = await msg.answer("⏳",reply_markup=back_button_btn())
            await a.delete()
            
            count = len(anime)
            if count == 1:
                await msg.answer("✅<b>Anime topildi !</b>")
                
                await Add_serie.actions.set()
                await serie_adding_text_func(anime[0][0],msg,None)
        
            else:
                await msg.answer("🗂<b>Kerakligini tanlang !</b>",reply_markup=admin_searched_animes_clbtn(anime))
        
    else:
        await state.finish()
        await Admin.menu.set()
        await msg.answer("👔<b>Admin panel</b>",reply_markup=admin_button_btn())

@dp.callback_query_handler(text_contains = "search",state=Add_serie.search)
async def qosh(call: types.CallbackQuery,state : FSMContext):
    
    content_id = call.data.split(",")[1]
    await call.message.delete()

    if content_id != "back":
        anime_id = int(content_id)
        await Add_serie.actions.set()
        await serie_adding_text_func(anime_id,None,call)
        
    else:
        await state.finish()
        await Admin.menu.set()
        await call.message.answer("👔<b>Admin panel</b>",reply_markup=admin_button_btn())

@dp.callback_query_handler(text_contains = "add",state=Add_serie.actions)
async def qosh(call: types.CallbackQuery,state : FSMContext):
    
    command = call.data.split(",")[1]
    try:
        content_id = int(call.data.split(",")[2])
    except:
        pass
    
    if command == "serie":
        anime = get_anime_base(content_id)
        
        series = anime[0][8]
        anime_name = anime[0][3]
        
        await state.finish()
        await Add_serie.add_serie.set()
        async with state.proxy() as data:
            data["which"] = "serie"
            data["which_anime"] = content_id
            data["anime_name"] = anime_name
            data["anime_serie_count"] = series
        await call.message.delete()
        
        await call.message.answer(f"❗️<b><i>{anime_name}</i> animesi uchun <i>{series + 1} - seriyani</i> yuboring !</b>",reply_markup=back_button_btn())

    elif command == "finish":
        
        await call.message.delete()
        await Add_serie.finish_anime.set()
        await call.message.answer("⁉️<b>Siz ushbu animeni tugatishni tasdiqlayszmi ?</b>",reply_markup=are_you_sure_clbtn(content_id))
      
    elif command == "back":
        await call.message.delete()
        await Admin.menu.set()
        await call.message.answer("👔<b>Admin panel</b>",reply_markup=admin_button_btn())
    
@dp.callback_query_handler(text_contains = "sure",state=Add_serie.finish_anime)
async def qosh(call: types.CallbackQuery,state : FSMContext):
    
    command = call.data.split(",")[1]
    content_id = int(call.data.split(",")[2])
    
    if command == "yeah":
        await call.message.delete()
        update_anime_status_base(content_id)
        await state.finish()
        await Admin.menu.set()
        await call.message.answer("🟢<b>Ushbu anime tugallandi </b>",reply_markup=admin_button_btn())

    if command == "nope":
        await call.message.delete()
        await Add_serie.actions.set()
        await serie_adding_text_func(content_id,None,call)

@dp.message_handler(content_types=["video"],state=[Add_serie.add_serie,Add_serie.add_film])
async def start(msg:types.Message ,state : FSMContext):
    
    caption = msg.caption 
    is_forwarded = [msg.forward_from_chat,msg.forward_from]

    if caption != None:
        await msg.answer("<b>❗️Yuborgan videoingizda Text bo'lmasligi zarur !</b>")
        
    elif is_forwarded[0] != None or is_forwarded[1] != None:
        await msg.answer("❗️<b>Yuborgan videoingiz tepasida kanaldan yoki kimdandir yuborilgan degan so'z bo'lmasligi kerak !</b>")
    
    else:
        data = await state.get_data()
        which = data.get("which")
        which_anime = data.get("which_anime")
        anime_name = data.get("anime_name")
        anime_serie_count = int(data.get("anime_serie_count"))
        
        serie_id = msg.message_id
        
        if which == "serie" or which == "film":
            
            await state.finish()
            await Add_serie.add_serie.set()
            async with state.proxy() as data:
                data["which"] = which
                data["which_anime"] = which_anime
                data["anime_name"] = anime_name
                data["anime_serie_count"] = anime_serie_count+1
                
            if which == "serie":
                quality = f"{msg.video.height}p"
                
                serie = await dp.bot.forward_message(chat_id=anime_series_chat,from_chat_id=msg.from_user.id,message_id=serie_id)
                new_serie_id = serie.message_id
                
                add_serie_base(which_anime,new_serie_id,anime_serie_count+1,quality)
                update_anime_serie_count_base(which_anime,"series")
                
                await msg.answer(f"✅<b><i>{anime_name}</i> animesi uchun <i>{anime_serie_count+1}- seria</i> qabul qilindi \n\n ⚠️<i>{anime_serie_count+2} - seriani</i> yuboring</b>",reply_markup=back_button_clbtn(None))

@dp.callback_query_handler(text_contains = "back",state=[Add_serie.add_serie,Add_serie.add_film])
async def qosh(call: types.CallbackQuery,state : FSMContext):
    await call.message.delete()
    await state.finish()
    await Admin.menu.set()
    await call.message.answer("👔<b>Admin panel</b>",reply_markup=admin_button_btn())


@dp.message_handler(text_contains = "🔙Ortga",state=Add_anime.all_states)
async def start(msg:types.Message ,state : FSMContext):
    
    await state.finish()
    await Admin.menu.set()
    await msg.answer("✅<b>Bekor qilindi</b>",reply_markup=admin_button_btn())
    
@dp.callback_query_handler(text_contains = "lang",state=Add_anime.language)
async def qosh(call: types.CallbackQuery,state : FSMContext):
    
    lang = call.data.split(",")[1]
    
    if lang == "back":
        await call.message.delete()
        await state.finish()
        await Admin.menu.set()
        await call.message.answer("✅<b>Bekor qilindi</b>",reply_markup=admin_button_btn())

    else:
        await call.message.delete()
        await Add_anime.treller.set()
        async with state.proxy() as data:
            data["lang"] = lang
        await call.message.answer("🧿<b>Anime uchun Treller yuboring !</b>",reply_markup=back_button_btn())

@dp.message_handler(content_types=["text"],state=Add_anime.name)
async def start(msg:types.Message ,state : FSMContext):
    
    text = msg.text

    async with state.proxy() as data:
        data["name"] = text
        
    await Add_anime.about.set()
    await msg.answer("📄<b>Anime haqida qisqacha matn kiriting !</b>")
    
@dp.message_handler(content_types=["text"],state=Add_anime.about)
async def start(msg:types.Message ,state : FSMContext):
    
    text = msg.text

    if len(text) < 20:
        await msg.answer("❗️<b>Juda ham qisqa !<b>")
    else:
        async with state.proxy() as data:
            data["about"] = text
        
        await Add_anime.genre.set()
        await msg.answer("<b>📑Anime janrlarini kiriting !</b>\n\nNamuna: Ekshen,Sarguzasht,Drama . . .")

@dp.message_handler(content_types=["text"],state=Add_anime.genre)
async def start(msg:types.Message ,state : FSMContext):
    
    text = msg.text

    if len(text.split(",")) < 3:
        await msg.answer("❗️<b>Minimal 3 ta janr kiriting !</b>")
        
    else:
        async with state.proxy() as data:
            data["genre"] = text

        await Add_anime.teg.set()
        await msg.answer("#️⃣<b>Anime uchun teg kiriting !</b>\n\nNamuna: Saitama,Saytama,Vanpachmen . . .")
        
@dp.message_handler(content_types=["text"],state=Add_anime.teg)
async def start(msg:types.Message ,state : FSMContext):
    
    text = msg.text

    if len(text.split(",")) < 3:
        await msg.answer("❗️<b>Minimal 3 ta teg kiriting !</b>")
        
    else:
        async with state.proxy() as data:
            data["teg"] = text
            
        await Add_anime.dub.set()
        await msg.answer("<b>🎙Anime ovoz beruvchisini kiriting !</b>")
        
@dp.message_handler(content_types=["text"],state=Add_anime.dub)
async def start(msg:types.Message ,state : FSMContext):
    
    dub = msg.text
    
    admin_chat_id = msg.from_user.id
    
    data = await state.get_data()
    lang = data.get("lang")
    treller_id = int(data.get("treller"))
    name = data.get("name")
    about = str(data.get("about")).replace("\"","").replace("'","")
    genre = data.get("genre").replace(" ","")
    teg = data.get("teg")
    
    treller = await dp.bot.forward_message(chat_id=anime_treller_chat,from_chat_id=admin_chat_id,message_id=treller_id)
    new_treller_id = treller.message_id
    
    add_anime_base(lang,new_treller_id,name,about,genre,teg,dub)
    update_statistics_anime_base()

    await state.finish()
    await Admin.menu.set()
    await msg.answer("✅<b>Anime muvaffaqiyatli qo'shildi !</b>",reply_markup=admin_button_btn())

@dp.message_handler(content_types=["text"],state=[Admin.send_message_to_one,Admin.sending_to_one])
async def start(msg:types.Message ,state : FSMContext):

    text = msg.text
    
    data = await state.get_data()
    user_id = data.get("user_id")
    
    if text != "🔙Ortga":
        
        if not user_id or user_id == "":
        
            try:
                user_id = int(text)
                user = get_user_base(user_id)

                if not user:
                    await msg.answer("<b>❗️Bunday ID dagi foydalanuvchi topilmadi !</b>")
                
            except:
                if text[0] == "@":
                    user = get_user_by_username_base(text)
                else:
                    user = None
                    await msg.answer("❗️<b>Username '@' bilan boshlanishi kerak ! Qayta urinib ko'ring.</b>")
                
            if user:
                if user[0][7] != 0:
                    is_admin = "ADMIN"
                    
                elif user[0][8] != 0:
                    is_admin = "STAFF"
                    
                else:
                    is_admin = "Yo'q"
                
                await msg.answer(f"""
✅Foydalanuvchi topildi :
                                 
🆔 : {user[0][0]}
👤Username : {user[0][1]}
---------------
💬Til : {user[0][2]}
---------------
📌Adminlik : {is_admin}
""")
                
                await Admin.sending_to_one.set()
                async with state.proxy() as data:
                    data["user_id"] = user[0][0]
                await msg.answer("<b>❗️Ushbu foydalanuvchiga yuborish uchun xabar kiriting !</b>",reply_markup=back_button_btn())
        
        else:
            await Admin.sure.set()
            
            async with state.proxy() as data:
                data["command"] = "send_message_to_one"
                data["user_id"] = user_id
                data["msg"] = msg.message_id
                
            await msg.answer("<b>⚠️Usbu xabarni yuborishni tasdiqlayszmi ?</b>",reply_markup=are_you_sure_clbtn())
        
    else:
        await state.finish()
        await Admin.menu.set()
        await msg.answer("👔<b>Admin panel</b>",reply_markup=admin_button_btn())
        
@dp.message_handler(content_types=["any"],state=Admin.send_message)
async def start(msg:types.Message ,state : FSMContext):
    
    message_id = msg.message_id
    text = msg.text
    
    if text != "🔙Ortga":
        async with state.proxy() as data:
            data["command"] = "send_message_all"
            data["msg"] = message_id
        
        await Admin.sure.set()
        a = await msg.answer("⏳",reply_markup=back_button_btn())
        await a.delete()
        await msg.answer("<b>⚠️Usbu xabarni yuborishni tasdiqlayszmi ?</b>",reply_markup=are_you_sure_clbtn())
    
    else:
        await Admin.menu.set()
        await msg.answer("👔<b>Admin panel</b>",reply_markup=admin_button_btn())
    
@dp.callback_query_handler(text_contains = "sure",state=Admin.sure)
async def qosh(call: types.CallbackQuery,state : FSMContext):
    
    data = await state.get_data()
    command = data.get("command")
    
    sure = call.data.split(",")[1]
    
    admin_chat_id = call.from_user.id
    
    if command == "send_message_all":
        
        if sure == "yeah":
            await call.message.delete()
            
            users_list = get_all_user_base()
            message_id = data.get("msg")
            
            await Admin.menu.set()
            await call.message.answer("✅<b>Yuborilmoqda . . .</b>",reply_markup=admin_button_btn())
            
            sended_users_count = 0
            
            for user in users_list:
                user_id = user[0]
                
                try:
                    await dp.bot.forward_message(chat_id=user_id,from_chat_id=admin_chat_id,message_id=message_id)
                    sended_users_count += 1
                    await asyncio.sleep(3)
                except:
                    try:
                        await asyncio.sleep(1)
                        await dp.bot.forward_message(chat_id=user_id,from_chat_id=admin_chat_id,message_id=message_id)
                        sended_users_count += 1
                        
                    except:
                        await asyncio.sleep(3)

            await call.message.answer(f"<b>✅Xabar yuborib bo'lindi !!!\n\n{sended_users_count} ta foydalanuvchiga xabar yuborildi !</b>")
            
        elif sure == "nope":
            await call.message.delete()
            await Admin.menu.set()
            await call.message.answer("❌<b>Bekor qilindi</b>",reply_markup=admin_button_btn())

    if command == "send_message_to_one":
        if sure == "yeah":
            await call.message.delete()
            
            message_id = data.get("msg")
            user_id = data.get("user_id")
            
            try:
                await dp.bot.forward_message(chat_id=user_id,from_chat_id=admin_chat_id,message_id=message_id)
                await state.finish()
                await Admin.menu.set()
                await call.message.answer("✅<b>Xabar yuborildi !</b>",reply_markup=admin_button_btn())
            except:
                await state.finish()
                await Admin.menu.set()
                await call.message.answer("<b>❌Yuborib bo'lmadi ! Foydalanuvchi botni blocklagan bo'lishi mumkin.</b>",reply_markup=admin_button_btn())
            
        elif sure == "nope":
            await call.message.delete()
            await Admin.menu.set()
            await call.message.answer("❌<b>Bekor qilindi</b>",reply_markup=admin_button_btn())