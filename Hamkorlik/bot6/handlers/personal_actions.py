from aiogram import types,Bot
from users_base import *
from dispatcher import dp
from aiogram.dispatcher import FSMContext
from .buttons import *
from .languages import *
from .callbacks import *
from aiogram.dispatcher.filters.state import State, StatesGroup
import asyncio
from datetime import *
import shutil
from .searching_by_photo import *
import os
from aiogram.types import InputFile
from .search_photo import handle_photo_from_file
anime_treller_chat = -1001990975355
anime_series_chat = -1002076256295
vip_buying_chat = -1002099276344
from dotenv import load_dotenv
import os
from datetime import datetime
from dateutil.relativedelta import relativedelta
import logging
try:
    from fuzzywuzzy import process, fuzz
except ImportError:
    process = None
    fuzz = None
from config import ANIDUBLE,BOT_NAME,KARTA_RAQAM, KARTA_NOMI
load_dotenv()
from .admin_actions import get_mandatory_channels
BOT_TOKEN = os.getenv('BOT_TOKEN')



from aiogram import types, Bot




from users_base import get_user_base, add_user_base, update_statistics_user_base, update_user_vip_base
from dispatcher import dp
from aiogram.dispatcher import FSMContext
from .buttons import *
from .languages import *
from .callbacks import *
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import asyncio
from datetime import *
import shutil
from .searching_by_photo import *
import os
from aiogram.types import InputFile
from .search_photo import handle_photo_from_file
from dotenv import load_dotenv
from dateutil.relativedelta import relativedelta
import logging
try:
    from fuzzywuzzy import process, fuzz
except ImportError:
    process = None
    fuzz = None
from config import ANIDUBLE, BOT_NAME, KARTA_RAQAM, KARTA_NOMI
from .admin_actions import get_mandatory_channels, get_sponsor

anime_treller_chat = -1001990975355
anime_series_chat = -1002076256295
vip_buying_chat = -1002099276344

load_dotenv()
BOT_TOKEN = os.getenv('BOT_TOKEN')

# Logging sozlamalari
logging.basicConfig(level=logging.INFO, filename='bot_user.log')

class User(StatesGroup):
    language = State()
    menu = State()
    searching = State()
    searching_film = State()
    anime_menu = State()
    film_menu = State()
    watching = State()
    watching_film = State()
    films = State()
    genre_input = State()
    buying_vip = State()
    buying_lux = State()
    search_by_photo = State()
    search_state = State()
    tasodifiy = State()

# VIP foydalanuvchi tekshiruvi
async def check_premium_func(user_id):
    user = get_user_base(user_id)
    if not user or len(user) == 0 or len(user[0]) < 6:
        logging.warning(f"No valid user data for user_id {user_id}")
        return "False"
    
    vip = user[0][5] if user[0][5] is not None else "0"
    is_vip = "False"
    
    if vip != "0":
        try:
            expire_time = datetime.strptime(vip, "%Y-%m-%d")
            now = datetime.now()
            if expire_time >= now:
                is_vip = "True"
            else:
                update_user_vip_base(user_id, "0")
                text = "<b>‼️Sizdagi ⚡️AniPass muddati o'z nihoyasiga yetdi!</b>"
                try:
                    a = await dp.bot.send_message(chat_id=user_id, text=text)
                    await a.pin()
                except Exception as e:
                    logging.error(f"Error pinning VIP expiration message for user {user_id}: {e}")
                try:
                    await dp.bot.kick_chat_member(chat_id=-1002131546047, user_id=user_id)
                except Exception as e:
                    logging.error(f"Error kicking user {user_id} from VIP chat: {e}")
        except ValueError:
            logging.error(f"Invalid VIP date format for user {user_id}: {vip}")
            update_user_vip_base(user_id, "0")
    
    return is_vip

# Majburiy kanallarni inline tugmalar sifatida ko‘rsatish
async def display_mandatory_channels(msg: types.Message, lang: str, channels: list, edit=False):
    markup = InlineKeyboardMarkup(row_width=1)
    valid_channels = []
    
    for channel in channels:
        channel_link = channel[1].strip() if channel[1] else None
        channel_name = channel[2].strip() if channel[2] else "Unknown"
        if channel_link and channel_link.startswith('@'):
            channel_url = f"https://t.me/{channel_link.lstrip('@')}"
            expire_info = f" (Muddat: {channel[4]})" if channel[4] else ""
            markup.add(InlineKeyboardButton(f"{channel_name}{expire_info}", url=channel_url))
            valid_channels.append(channel)
    
    if not valid_channels:
        logging.warning("No valid channels to display")
        await msg.answer("Hech qanday kanal topilmadi. Iltimos, administrator bilan bog‘laning.")
        return False
    
    markup.add(InlineKeyboardButton("✅ Tekshirish", callback_data="check_subscription"))
    text = you_should_subscribe_message(lang)
    
    try:
        if edit:
            try:
                await msg.edit_text(text, reply_markup=markup, parse_mode="HTML")
            except Exception as e:
                if "Message is not modified" in str(e):
                    logging.info(f"Message not modified for user {msg.from_user.id}, sending new message")
                    await msg.delete()
                    await msg.answer(text, reply_markup=markup, parse_mode="HTML")
                else:
                    raise e
        else:
            await msg.answer(text, reply_markup=markup, parse_mode="HTML")
        logging.info(f"Displayed mandatory channels to user {msg.from_user.id}, edit={edit}")
        return True
    except Exception as e:
        logging.error(f"Error displaying mandatory channels: {e}")
        await msg.answer(text, reply_markup=markup, parse_mode="HTML")
        return True

# Sponsor va majburiy kanallarni tekshirish funksiyasi
async def sponsor_checking_func(msg: types.Message, lang: str):
    sponsor = get_sponsor() or []
    mandatory_channels = get_mandatory_channels() or []
    is_sub = True
    failed_channels = []

    if not sponsor and not mandatory_channels:
        logging.info(f"No sponsor or mandatory channels for user {msg.from_user.id}")
        return is_sub

    for s in sponsor:
        try:
            chat_id = s[1].strip() if s[1] and s[1].startswith('@') else None
            if not chat_id:
                logging.error(f"Invalid sponsor channel link: {s[1]}")
                failed_channels.append(s[1] or "Unknown")
                continue
            user = await dp.bot.get_chat_member(chat_id=chat_id, user_id=msg.from_user.id)
            if user.status == "left":
                is_sub = False
                failed_channels.append(s[1])
            await asyncio.sleep(0.5)  # API cheklovlaridan qochish
        except Exception as e:
            logging.error(f"Sponsor kanal tekshirishda xato: {s[0]}, link: {s[1]}, xato: {e}")
            failed_channels.append(s[1] or "Unknown")
            continue

    if is_sub:
        for channel in mandatory_channels:
            try:
                chat_id = channel[1].strip() if channel[1] and channel[1].startswith('@') else None
                if not chat_id:
                    logging.error(f"Invalid mandatory channel link: {channel[1]}")
                    failed_channels.append(channel[1] or "Unknown")
                    continue
                user = await dp.bot.get_chat_member(chat_id=chat_id, user_id=msg.from_user.id)
                if user.status == "left":
                    is_sub = False
                    failed_channels.append(channel[1])
                await asyncio.sleep(0.5)  # API cheklovlaridan qochish
            except Exception as e:
                logging.error(f"Majburiy kanal tekshirishda xato: {channel[0]}, link: {channel[1]}, xato: {e}")
                failed_channels.append(channel[1] or "Unknown")
                continue

    if not is_sub:
        combined_channels = mandatory_channels + [(s[0], s[1], s[1] or "Unknown", None, None, 0, None) for s in sponsor]
        success = await display_mandatory_channels(msg, lang, combined_channels, edit=False)
        if success:
            logging.info(f"User {msg.from_user.id} not subscribed to channels: {', '.join(failed_channels)}")
        else:
            is_sub = True  # Agar kanallar ko‘rsatilmasa, tekshiruvni o‘tkazib yuboramiz

    return is_sub

# “Tekshirish” tugmasi uchun handler
@dp.callback_query_handler(text="check_subscription", state="*")
async def check_subscription_callback(callback: types.CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    lang = (await state.get_data()).get("lang", "uz")
    sponsor = get_sponsor() or []
    mandatory_channels = get_mandatory_channels() or []
    is_sub = True
    failed_channels = []

    for s in sponsor:
        try:
            chat_id = s[1].strip() if s[1] and s[1].startswith('@') else None
            if not chat_id:
                logging.error(f"Invalid sponsor channel link: {s[1]}")
                failed_channels.append(s[1] or "Unknown")
                continue
            user = await dp.bot.get_chat_member(chat_id=chat_id, user_id=user_id)
            if user.status == "left":
                is_sub = False
                failed_channels.append(s[1])
            await asyncio.sleep(0.5)  # API cheklovlaridan qochish
        except Exception as e:
            logging.error(f"Sponsor kanal tekshirishda xato: {s[0]}, link: {s[1]}, xato: {e}")
            failed_channels.append(s[1] or "Unknown")
            continue

    if is_sub:
        for channel in mandatory_channels:
            try:
                chat_id = channel[1].strip() if channel[1] and channel[1].startswith('@') else None
                if not chat_id:
                    logging.error(f"Invalid mandatory channel link: {channel[1]}")
                    failed_channels.append(channel[1] or "Unknown")
                    continue
                user = await dp.bot.get_chat_member(chat_id=chat_id, user_id=user_id)
                if user.status == "left":
                    is_sub = False
                    failed_channels.append(channel[1])
                await asyncio.sleep(0.5)  # API cheklovlaridan qochish
            except Exception as e:
                logging.error(f"Majburiy kanal tekshirishda xato: {channel[0]}, link: {channel[1]}, xato: {e}")
                failed_channels.append(channel[1] or "Unknown")
                continue

    try:
        if is_sub:
            await state.finish()
            await User.menu.set()
            is_vip = await check_premium_func(user_id)
            async with state.proxy() as data:
                data["lang"] = lang
                data["vip"] = is_vip
            await callback.message.delete()  # Eski xabarni o‘chirish
            await callback.message.answer(
                main_menu_message(lang),
                reply_markup=user_button_btn(lang, is_vip),
                parse_mode="HTML"
            )
            await callback.answer("✅ Barcha kanallarga a’zo bo‘ldingiz!", show_alert=True)
            logging.info(f"User {user_id} successfully subscribed to all channels")
        else:
            combined_channels = mandatory_channels + [(s[0], s[1], s[1] or "Unknown", None, None, 0, None) for s in sponsor]
            success = await display_mandatory_channels(callback.message, lang, combined_channels, edit=True)
            if success:
                await callback.answer(
                    f"Iltimos, quyidagi kanallarga a’zo bo‘ling: {', '.join(failed_channels)}",
                    show_alert=True
                )
                logging.info(f"User {user_id} not subscribed to channels: {', '.join(failed_channels)}")
    except Exception as e:
        logging.error(f"Error in check_subscription_callback: {e}")
        combined_channels = mandatory_channels + [(s[0], s[1], s[1] or "Unknown", None, None, 0, None) for s in sponsor]
        success = await display_mandatory_channels(callback.message, lang, combined_channels, edit=False)
        if success:
            await callback.answer(
                f"Iltimos, quyidagi kanallarga a’zo bo‘ling: {', '.join(failed_channels)}",
                show_alert=True
            )

# Til tanlash handleri
@dp.callback_query_handler(lambda c: c.data.startswith("select,"), state=User.language)
async def qosh(callback: types.CallbackQuery, state: FSMContext):
    lang = callback.data.split(",")[1]
    user_id = callback.from_user.id
    username = f"@{callback.from_user.username}" if callback.from_user.username else "None"

    async with state.proxy() as data:
        data["lang"] = lang

    is_vip = await check_premium_func(user_id)

    try:
        add_user_base(user_id=user_id, username=username, lang=lang)
        update_statistics_user_base()
    except Exception as e:
        logging.error(f"Error adding user {user_id} to database: {e}")
        await callback.answer("Xato yuz berdi, iltimos qayta urinib ko‘ring!", show_alert=True)
        return

    is_sub = await sponsor_checking_func(callback.message, lang)
    if not is_sub:
        return

    await User.menu.set()
    await callback.message.delete()

    async with state.proxy() as data:
        data["lang"] = lang
        data["vip"] = is_vip

    await callback.message.answer(start_message(lang), reply_markup=user_button_btn(lang, is_vip))
    await callback.answer(f"Til muvaffaqiyatli o‘zgartirildi: {lang}", show_alert=True)
    logging.info(f"User {user_id} selected language {lang}")

# Ortga qaytish tugmasi
@dp.callback_query_handler(lambda c: c.data == "back", state="*")
async def back_to_main_menu(callback_query: types.CallbackQuery, state: FSMContext):
    user_id = callback_query.from_user.id
    lang = (await state.get_data()).get("lang", "uz")

    is_sub = await sponsor_checking_func(callback_query.message, lang)
    if not is_sub:
        return

    await state.finish()
    await User.menu.set()
    is_vip = await check_premium_func(user_id)
    async with state.proxy() as data:
        data["lang"] = lang
        data["vip"] = is_vip

    await callback_query.message.delete()
    await callback_query.message.answer(
        main_menu_message(lang),
        reply_markup=user_button_btn(lang, is_vip),
        parse_mode="HTML"
    )
    logging.info(f"User {user_id} returned to main menu")

# Start komandasi
@dp.message_handler(commands="start", state="*")
async def start(msg: types.Message, state: FSMContext):
    if str(msg.chat.id)[0] == "-":
        return

    user_id = msg.from_user.id
    user = get_user_base(user_id)
    lang = user[0][2] if user and len(user) > 0 and len(user[0]) > 2 else "uz"

    is_sub = await sponsor_checking_func(msg, lang)
    if not is_sub:
        return

    if not user:
        username = msg.from_user.username
        user_name = f"@{username}" if username else "None"
        await User.language.set()
        async with state.proxy() as data:
            data["username"] = user_name
        text = "Tilni tanlang:"
        await msg.answer(text=text, reply_markup=choose_language_clbtn())
        logging.info(f"New user {user_id} prompted to choose language")
    else:
        is_vip = await check_premium_func(user_id)
        async with state.proxy() as data:
            data["lang"] = lang
            data["vip"] = is_vip

        try:
            start = msg.text.replace("/start ", "")
            if "serie" in start:
                serie_post_id = int(start.split("serie")[0])
                anime = get_anime_base(serie_post_id)
                if anime:
                    a = await msg.answer(anime_found_message(lang), reply_markup=back_button_btn())
                    await a.delete()
                    serie = get_series_base(serie_post_id)[-1]
                    serie_id = int(serie[1])
                    serie_num = int(serie[2])
                    serie_quality = serie[3]
                    which_anime = int(serie[0])
                    page = serie_num // 21
                    series = get_anime_series_base(which_anime)
                    is_vip_anime = anime[0][10]
                    next_states = True

                    if is_vip_anime == "vip" and is_vip == "False":
                        await state.finish()
                        await User.menu.set()
                        async with state.proxy() as data:
                            data["lang"] = lang
                            data["vip"] = is_vip
                        await msg.answer("‼️Ushbu animeni tomosha qilish uchun ⚡️AniPass sotib olishingiz kerak!", reply_markup=user_button_btn(lang))
                        return

                    protect = is_vip_anime == "True"
                    await User.watching.set()
                    a = await dp.bot.forward_message(chat_id=user_id, message_id=serie_id, from_chat_id=anime_series_chat, protect_content=protect)
                    async with state.proxy() as data:
                        data["lang"] = lang
                        data["serie"] = a.message_id
                    await msg.answer(anime_serie_message(lang, serie_num, serie_quality), reply_markup=anime_series_clbtn(serie_num, series, page))
                else:
                    await state.finish()
                    await User.menu.set()
                    async with state.proxy() as data:
                        data["lang"] = lang
                    caption_text = f"""<b>
✨ Salom! {msg.from_user.username} Men — {BOT_NAME}!
🎌 O'zbek tilida dublyaj qilingan animelar olamiga hush kelibsiz!
...
</b>"""
                    with open("media/aniduble.jpg", "rb") as photo:
                        await msg.answer_photo(
                            photo=photo,
                            caption=caption_text,
                            reply_markup=user_button_btn(lang, is_vip),
                            parse_mode="HTML"
                        )
            else:
                await state.finish()
                await User.menu.set()
                async with state.proxy() as data:
                    data["lang"] = lang
                caption_text = f"""<b>
✨ Salom! {msg.from_user.username} Men — {BOT_NAME}!
🎌 O'zbek tilida dublyaj qilingan animelar olamiga hush kelibsiz!
...
</b>"""
                with open("media/aniduble.jpg", "rb") as photo:
                    await msg.answer_photo(
                        photo=photo,
                        caption=caption_text,
                        reply_markup=user_button_btn(lang, is_vip),
                        parse_mode="HTML"
                    )
        except Exception as e:
            logging.error(f"Start command error for user {user_id}: {e}")
            await state.finish()
            await User.menu.set()
            async with state.proxy() as data:
                data["lang"] = lang
            caption_text = f"""<b>
✨ Salom! {msg.from_user.username} Men — {BOT_NAME}!
🎌 O'zbek tilida dublyaj qilingan animelar olamiga hush kelibsiz!
...
</b>"""
            with open("media/aniduble.jpg", "rb") as photo:
                await msg.answer_photo(
                    photo=photo,
                    caption=caption_text,
                    reply_markup=user_button_btn(lang, is_vip),
                    parse_mode="HTML"
                )





import logging
import sqlite3
import datetime
import asyncio
import re
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import BOT_NAME, BOT_TOKEN, ANIDUBLE
from .buttons import back_button_btn
from typing import List, Tuple

# Logging sozlamalari
logging.basicConfig(level=logging.INFO, filename='bot_setup.log')

# Majburiy a'zolik va post kanallari uchun holatlar
class ChannelManagement(StatesGroup):
    select_type = State()
    add_mandatory_channel = State()
    remove_mandatory_channel = State()
    add_post_channel = State()
    remove_post_channel = State()
    view_channel_stats = State()

class Admin(StatesGroup):
    menu = State()

# Bazada kanallar jadvallarini yaratish
def create_channels_tables():
    try:
        with sqlite3.connect("hamkor.db") as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS mandatory_channels (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    channel_username TEXT UNIQUE,
                    channel_link TEXT NOT NULL UNIQUE,
                    channel_name TEXT NOT NULL,
                    channel_type TEXT NOT NULL,
                    channel_platform TEXT NOT NULL DEFAULT 'telegram',
                    expire_date TEXT,
                    subscribers_count INTEGER DEFAULT 0,
                    added_date TEXT NOT NULL
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS post_channels (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    channel_link TEXT NOT NULL UNIQUE,
                    channel_name TEXT NOT NULL,
                    posts_count INTEGER DEFAULT 0,
                    added_date TEXT NOT NULL
                )
            """)
            conn.commit()
            logging.info("Kanallar jadvallari muvaffaqiyatli yaratildi.")
    except sqlite3.Error as e:
        logging.error(f"Kanallar jadvallarini yaratishda xato: {e}")

# Migrate existing mandatory_channels table
def migrate_mandatory_channels():
    try:
        with sqlite3.connect("hamkor.db") as conn:
            cursor = conn.cursor()
            # Check if channel_platform column exists
            cursor.execute("PRAGMA table_info(mandatory_channels)")
            columns = [col[1] for col in cursor.fetchall()]
            if "channel_platform" not in columns:
                cursor.execute("ALTER TABLE mandatory_channels ADD COLUMN channel_platform TEXT NOT NULL DEFAULT 'telegram'")
                conn.commit()
                logging.info("Added channel_platform column to mandatory_channels.")
            if "channel_link" in columns and "channel_username" not in columns:
                # Rename the existing table
                cursor.execute("ALTER TABLE mandatory_channels RENAME TO mandatory_channels_old")
                # Create the new table
                cursor.execute("""
                    CREATE TABLE mandatory_channels (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        channel_username TEXT UNIQUE,
                        channel_link TEXT NOT NULL UNIQUE,
                        channel_name TEXT NOT NULL,
                        channel_type TEXT NOT NULL,
                        channel_platform TEXT NOT NULL DEFAULT 'telegram',
                        expire_date TEXT,
                        subscribers_count INTEGER DEFAULT 0,
                        added_date TEXT NOT NULL
                    )
                """)
                # Migrate data
                cursor.execute("""
                    INSERT INTO mandatory_channels (id, channel_username, channel_link, channel_name, channel_type, channel_platform, expire_date, subscribers_count, added_date)
                    SELECT id, channel_link, channel_link, channel_name, channel_type, 'telegram', expire_date, subscribers_count, added_date
                    FROM mandatory_channels_old
                """)
                # Drop the old table
                cursor.execute("DROP TABLE mandatory_channels_old")
                conn.commit()
                logging.info("mandatory_channels table migrated successfully.")
    except sqlite3.Error as e:
        logging.error(f"mandatory_channels table migration error: {e}")

# Initialize database and migrate
create_channels_tables()
migrate_mandatory_channels()

# Kanal linkini validatsiya qilish
async def validate_channel_link(bot, channel_link: str, platform: str = 'telegram') -> bool:
    if platform == 'telegram':
        if not (channel_link.startswith("@") or channel_link.startswith("https://t.me/")):
            logging.error(f"Invalid Telegram link format: {channel_link}")
            return False
        try:
            chat = await bot.get_chat(channel_link)
            logging.info(f"Successfully validated Telegram channel: {channel_link}, type: {chat.type}")
            return chat.type in ["channel", "supergroup"]
        except Exception as e:
            if "Chat not found" in str(e):
                logging.error(f"Chat not found for {channel_link}. Bot may not be a member of the channel.")
            else:
                logging.error(f"Error validating Telegram channel link {channel_link}: {e}")
            return False
    elif platform == 'instagram':
        # Instagram profil linklari uchun validatsiya
        instagram_pattern = r'^(https?:\/\/)?(www\.)?instagram\.com\/[A-Za-z0-9._-]+\/?$'
        if not re.match(instagram_pattern, channel_link):
            logging.error(f"Invalid Instagram link format: {channel_link}")
            return False
        logging.info(f"Validated Instagram link: {channel_link}")
        return True
    else:
        logging.error(f"Unsupported platform: {platform}")
        return False

# Kanal linkini to‘g‘ri URL formatiga o‘tkazish
def format_channel_url(channel_link: str, platform: str = 'telegram') -> str:
    if platform == 'telegram':
        if channel_link.startswith("https://t.me/"):
            return channel_link
        elif channel_link.startswith("@"):
            return f"https://t.me/{channel_link.lstrip('@')}"
    elif platform == 'instagram':
        if not channel_link.startswith("https://"):
            return f"https://{channel_link.lstrip('www.')}"
    return channel_link

# Majburiy kanallar ro'yxatini olish
def get_mandatory_channels() -> List[Tuple]:
    try:
        with sqlite3.connect("hamkor.db") as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, channel_username, channel_link, channel_name, channel_type, channel_platform, expire_date, subscribers_count, added_date FROM mandatory_channels")
            return cursor.fetchall()
    except sqlite3.Error as e:
        logging.error(f"Majburiy kanallarni olishda xato: {e}")
        return []

# Post kanallar ro'yxatini olish
def get_post_channels() -> List[Tuple]:
    try:
        with sqlite3.connect("hamkor.db") as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM post_channels")
            return cursor.fetchall()
    except sqlite3.Error as e:
        logging.error(f"Post kanallarni olishda xato: {e}")
        return []

# Back button klaviaturasini aniq ta'minlash
def get_back_button():
    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(InlineKeyboardButton("🔙 Ortga", callback_data="back_to_main_menu"))
    return markup

# Admin paneli uchun inline klaviatura
def get_admin_inline_button():
    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(
        InlineKeyboardButton("🔐 Majburiy a'zo", callback_data="manage_channels"),
        InlineKeyboardButton("📊 Statistika", callback_data="view_admin_stats"),
        InlineKeyboardButton("🔙 Chiqish", callback_data="back")
    )
    return markup

# Klaviatura tengligini tekshirish uchun yordamchi funksiya
def are_keyboards_equal(current_markup: InlineKeyboardMarkup, new_markup: InlineKeyboardMarkup) -> bool:
    if not current_markup or not new_markup:
        return False
    current_buttons = [[btn.to_dict() for btn in row] for row in current_markup.inline_keyboard]
    new_buttons = [[btn.to_dict() for btn in row] for row in new_markup.inline_keyboard]
    return current_buttons == new_buttons

@dp.callback_query_handler(state=ChannelManagement.select_type)
async def process_channel_management(call: types.CallbackQuery, state: FSMContext):
    logging.info(f"Callback received: {call.data}, State: {await state.get_state()}")
    
    try:
        # Asosiy kanal boshqaruv menyusiga qaytish
        if call.data == "back_to_main_menu":
            markup = InlineKeyboardMarkup(row_width=1)
            markup.add(
                InlineKeyboardButton("📢 Post qilish uchun kanal", callback_data="manage_post_channels"),
                InlineKeyboardButton("🔐 Majburiy a'zo uchun kanal", callback_data="manage_mandatory_channels"),
                InlineKeyboardButton("🔙 Ortga", callback_data="back_to_admin_menu")
            )
            new_text = "🔐 Kanal boshqaruvi:"
            current_markup = call.message.reply_markup
            if call.message.text != new_text or not are_keyboards_equal(current_markup, markup):
                await call.message.edit_text(new_text, reply_markup=markup)
            logging.info(f"User {call.from_user.id} returned to main menu")
            return

        # Kanal turini tanlash
        if call.data in ["manage_mandatory_channels", "manage_post_channels"]:
            await state.update_data(channel_management_type=call.data)
            markup = InlineKeyboardMarkup(row_width=3)
            if call.data == "manage_mandatory_channels":
                channels = get_mandatory_channels()
                if not channels:
                    markup.add(
                        InlineKeyboardButton("➕ Kanal qo'shish", callback_data="add_channel"),
                        InlineKeyboardButton("🔙 Ortga", callback_data="back_to_main_menu")
                    )
                    new_text = (
                        "📭 Hozircha hech qanday majburiy a'zolik kanali qo'shilmagan.\n"
                        "Yangi kanal qo'shish uchun tugmani bosing:"
                    )
                    current_markup = call.message.reply_markup
                    if call.message.text != new_text or not are_keyboards_equal(current_markup, markup):
                        await call.message.edit_text(new_text, reply_markup=markup)
                    logging.info(f"User {call.from_user.id} viewed empty mandatory channels list")
                    return

                for channel in channels:
                    channel_id, channel_username, channel_link, channel_name, channel_type, channel_platform, expire_date, subscribers_count, added_date = channel
                    display_text = f"{channel_name} ({channel_platform})"
                    channel_url = channel_link
                    expire_info = f" (Muddat: {expire_date})" if expire_date else ""
                    try:
                        markup.row(
                            InlineKeyboardButton(f"{display_text}{expire_info}", url=format_channel_url(channel_url, channel_platform)),
                            InlineKeyboardButton(f"👥 {subscribers_count}", callback_data="view_channel_stats"),
                            InlineKeyboardButton("🗑", callback_data=f"remove_channel_{channel_id}")
                        )
                    except Exception as e:
                        logging.error(f"Error creating button for channel {channel_url}: {str(e)}")
                        continue

                markup.row(
                    InlineKeyboardButton("➕ Kanal qo'shish", callback_data="add_channel"),
                    InlineKeyboardButton("🔙 Ortga", callback_data="back_to_main_menu")
                )

                new_text = (
                    "🔐 <b>Majburiy a'zolik kanallari ro'yxati:</b>\n\n"
                    "Kanal nomi | A'zolar soni | O'chirish"
                )
                current_markup = call.message.reply_markup
                if call.message.text != new_text or not are_keyboards_equal(current_markup, markup):
                    await call.message.edit_text(new_text, reply_markup=markup, parse_mode="HTML")
                logging.info(f"User {call.from_user.id} viewed mandatory channels in table format")
            else:
                channels = get_post_channels()
                if not channels:
                    markup.add(
                        InlineKeyboardButton("➕ Kanal qo'shish", callback_data="add_channel"),
                        InlineKeyboardButton("🔙 Ortga", callback_data="back_to_main_menu")
                    )
                    new_text = (
                        "📭 Hozircha hech qanday post qilish kanali qo'shilmagan.\n"
                        "Yangi kanal qo'shish uchun tugmani bosing:"
                    )
                    current_markup = call.message.reply_markup
                    if call.message.text != new_text or not are_keyboards_equal(current_markup, markup):
                        await call.message.edit_text(new_text, reply_markup=markup)
                    logging.info(f"User {call.from_user.id} viewed empty post channels list")
                    return

                markup.add(
                    InlineKeyboardButton("➕ qo'shish", callback_data="add_channel"),
                    InlineKeyboardButton("➖ o'chirish", callback_data="remove_channel"),
                    InlineKeyboardButton("📋 ro'yxat", callback_data="list_channels"),
                    InlineKeyboardButton("📊 Statistika", callback_data="view_stats"),
                    InlineKeyboardButton("🔙 Ortga", callback_data="back_to_main_menu")
                )
                new_text = "📢 Post qilish kanallarini boshqarish:"
                current_markup = call.message.reply_markup
                if call.message.text != new_text or not are_keyboards_equal(current_markup, markup):
                    await call.message.edit_text(new_text, reply_markup=markup)
                logging.info(f"User {call.from_user.id} selected manage_post_channels")
            return

        user_data = await state.get_data()
        management_type = user_data.get("channel_management_type")
        if not management_type:
            await state.finish()
            await Admin.menu.set()
            markup = get_admin_inline_button()
            new_text = "✅ Admin panelga qaytildi!"
            current_markup = call.message.reply_markup
            if call.message.text != new_text or not are_keyboards_equal(current_markup, markup):
                await call.message.edit_text(new_text, reply_markup=markup)
            return

        if call.data == "add_channel":
            if management_type == "manage_mandatory_channels":
                await ChannelManagement.add_mandatory_channel.set()
                new_text = (
                    "➕ Qo'shmoqchi bo'lgan kanal ma'lumotlarini yuboring (masalan, @ChannelName yoki https://t.me/ChannelName yoki https://t.me/+hash yoki https://www.instagram.com/username [oddiy/yopiq/zayafkali 7 kun]):"
                )
                markup = get_back_button()
                current_markup = call.message.reply_markup
                if call.message.text != new_text or not are_keyboards_equal(current_markup, markup):
                    await call.message.edit_text(new_text, reply_markup=markup)
                logging.info(f"User {call.from_user.id} entered add_mandatory_channel state")
            elif management_type == "manage_post_channels":
                await ChannelManagement.add_post_channel.set()
                new_text = (
                    "➕ Qo'shmoqchi bo'lgan kanal linkini yuboring (masalan, @ChannelName yoki https://t.me/ChannelName):"
                )
                markup = get_back_button()
                current_markup = call.message.reply_markup
                if call.message.text != new_text or not are_keyboards_equal(current_markup, markup):
                    await call.message.edit_text(new_text, reply_markup=markup)
                logging.info(f"User {call.from_user.id} entered add_post_channel state")

        elif call.data.startswith("remove_channel_"):
            channel_id = call.data.split("_")[-1]
            if management_type == "manage_mandatory_channels":
                try:
                    with sqlite3.connect("hamkor.db") as conn:
                        cursor = conn.cursor()
                        cursor.execute("DELETE FROM mandatory_channels WHERE id = ?", (channel_id,))
                        conn.commit()
                        affected = cursor.rowcount

                    if affected:
                        new_text = f"✅ Kanal (ID: {channel_id}) majburiy a'zolik ro'yxatidan o'chirildi!"
                        markup = get_back_button()
                        current_markup = call.message.reply_markup
                        if call.message.text != new_text or not are_keyboards_equal(current_markup, markup):
                            await call.message.edit_text(new_text, reply_markup=markup)
                        logging.info(f"Channel {channel_id} removed from mandatory_channels by user {call.from_user.id}")
                    else:
                        new_text = "❌ Bunday kanal topilmadi!"
                        markup = get_back_button()
                        current_markup = call.message.reply_markup
                        if call.message.text != new_text or not are_keyboards_equal(current_markup, markup):
                            await call.message.edit_text(new_text, reply_markup=markup)
                        logging.info(f"Channel {channel_id} not found in mandatory_channels")
                except sqlite3.Error as e:
                    logging.error(f"Baza xatosi: {e}")
                    new_text = "❌ Ma'lumotlarni o'chirishda xato yuz berdi!"
                    markup = get_back_button()
                    current_markup = call.message.reply_markup
                    if call.message.text != new_text or not are_keyboards_equal(current_markup, markup):
                        await call.message.edit_text(new_text, reply_markup=markup)
                return

        elif call.data == "list_channels":
            if management_type == "manage_mandatory_channels":
                channels = get_mandatory_channels()
                markup = InlineKeyboardMarkup(row_width=3)
                if not channels:
                    markup.add(
                        InlineKeyboardButton("➕ Kanal qo'shish", callback_data="add_channel"),
                        InlineKeyboardButton("🔙 Ortga", callback_data="back_to_main_menu")
                    )
                    new_text = "📭 Hozircha hech qanday majburiy a'zolik kanali qo'shilmagan."
                    current_markup = call.message.reply_markup
                    if call.message.text != new_text or not are_keyboards_equal(current_markup, markup):
                        await call.message.edit_text(new_text, reply_markup=markup)
                    logging.info(f"User {call.from_user.id} viewed empty mandatory channels list")
                    return
                for channel in channels:
                    channel_id, channel_username, channel_link, channel_name, channel_type, channel_platform, expire_date, subscribers_count, added_date = channel
                    display_text = f"{channel_name} ({channel_platform})"
                    channel_url = channel_link
                    expire_info = f" (Muddat: {expire_date})" if expire_date else ""
                    try:
                        markup.row(
                            InlineKeyboardButton(f"{display_text}{expire_info}", url=format_channel_url(channel_url, channel_platform)),
                            InlineKeyboardButton(f"👥 {subscribers_count}", callback_data="view_channel_stats"),
                            InlineKeyboardButton("🗑", callback_data=f"remove_channel_{channel_id}")
                        )
                    except Exception as e:
                        logging.error(f"Error creating button for channel {channel_url}: {str(e)}")
                        continue

                markup.row(
                    InlineKeyboardButton("➕ Kanal qo'shish", callback_data="add_channel"),
                    InlineKeyboardButton("🔙 Ortga", callback_data="back_to_main_menu")
                )

                new_text = (
                    "🔐 <b>Majburiy a'zolik kanallari ro'yxati:</b>\n\n"
                    "Kanal nomi | A'zolar soni | O'chirish"
                )
                current_markup = call.message.reply_markup
                if call.message.text != new_text or not are_keyboards_equal(current_markup, markup):
                    await call.message.edit_text(new_text, reply_markup=markup, parse_mode="HTML")
                logging.info(f"User {call.from_user.id} viewed mandatory channels list in table format")

            elif management_type == "manage_post_channels":
                channels = get_post_channels()
                if not channels:
                    markup = InlineKeyboardMarkup(row_width=1)
                    markup.add(
                        InlineKeyboardButton("➕ Kanal qo'shish", callback_data="add_channel"),
                        InlineKeyboardButton("🔙 Ortga", callback_data="back_to_main_menu")
                    )
                    new_text = "📭 Hozircha hech qanday post qilish kanali qo'shilmagan."
                    current_markup = call.message.reply_markup
                    if call.message.text != new_text or not are_keyboards_equal(current_markup, markup):
                        await call.message.edit_text(new_text, reply_markup=markup)
                    logging.info(f"User {call.from_user.id} viewed empty post channels list")
                    return
                text = "📢 <b>Post qilish kanallari ro'yxati:</b>\n\n"
                for i, channel in enumerate(channels, 1):
                    text += (
                        f"{i}. {channel[2]} ({channel[1]})\n"
                        f"   Postlar: {channel[3]}\n"
                        f"   Qo'shilgan: {channel[4]}\n\n"
                    )
                markup = get_back_button()
                current_markup = call.message.reply_markup
                if call.message.text != text or not are_keyboards_equal(current_markup, markup):
                    await call.message.edit_text(text, parse_mode="HTML", reply_markup=markup)
                logging.info(f"User {call.from_user.id} viewed post channels list")

        elif call.data == "view_stats":
            if management_type == "manage_mandatory_channels":
                channels = get_mandatory_channels()
                markup = InlineKeyboardMarkup(row_width=3)
                if not channels:
                    markup.add(
                        InlineKeyboardButton("➕ Kanal qo'shish", callback_data="add_channel"),
                        InlineKeyboardButton("🔙 Ortga", callback_data="back_to_main_menu")
                    )
                    new_text = "📭 Hozircha hech qanday majburiy a'zolik kanali qo'shilmagan."
                    current_markup = call.message.reply_markup
                    if call.message.text != new_text or not are_keyboards_equal(current_markup, markup):
                        await call.message.edit_text(new_text, reply_markup=markup)
                    logging.info(f"User {call.from_user.id} viewed empty mandatory channels stats")
                    return
                for channel in channels:
                    channel_id, channel_username, channel_link, channel_name, channel_type, channel_platform, expire_date, subscribers_count, added_date = channel
                    display_text = f"{channel_name} ({channel_platform})"
                    channel_url = channel_link
                    expire_info = f" (Muddat: {expire_date})" if expire_date else ""
                    try:
                        markup.row(
                            InlineKeyboardButton(f"{display_text}{expire_info}", url=format_channel_url(channel_url, channel_platform)),
                            InlineKeyboardButton(f"👥 {subscribers_count}", callback_data="view_channel_stats"),
                            InlineKeyboardButton("🗑", callback_data=f"remove_channel_{channel_id}")
                        )
                    except Exception as e:
                        logging.error(f"Error creating button for channel {channel_url}: {str(e)}")
                        continue

                markup.row(
                    InlineKeyboardButton("➕ Kanal qo'shish", callback_data="add_channel"),
                    InlineKeyboardButton("🔙 Ortga", callback_data="back_to_main_menu")
                )

                new_text = (
                    "📊 <b>Majburiy a'zolik kanallari statistikasi:</b>\n\n"
                    "Kanal nomi | A'zolar soni | O'chirish"
                )
                current_markup = call.message.reply_markup
                if call.message.text != new_text or not are_keyboards_equal(current_markup, markup):
                    await call.message.edit_text(new_text, reply_markup=markup, parse_mode="HTML")
                logging.info(f"User {call.from_user.id} viewed mandatory channels stats in table format")

            elif management_type == "manage_post_channels":
                channels = get_post_channels()
                if not channels:
                    markup = InlineKeyboardMarkup(row_width=1)
                    markup.add(
                        InlineKeyboardButton("➕ Kanal qo'shish", callback_data="add_channel"),
                        InlineKeyboardButton("🔙 Ortga", callback_data="back_to_main_menu")
                    )
                    new_text = "📭 Hozircha hech qanday post qilish kanali qo'shilmagan."
                    current_markup = call.message.reply_markup
                    if call.message.text != new_text or not are_keyboards_equal(current_markup, markup):
                        await call.message.edit_text(new_text, reply_markup=markup)
                    logging.info(f"User {call.from_user.id} viewed empty post channels stats")
                    return
                text = "📊 <b>Post qilish kanallari statistikasi:</b>\n\n"
                total_posts = sum(channel[3] for channel in channels)
                text += f"📈 <b>Jami postlar:</b> {total_posts}\n\n"
                for i, channel in enumerate(channels, 1):
                    text += (
                        f"{i}. {channel[2]}\n"
                        f"   Postlar: {channel[3]}\n\n"
                    )
                markup = get_back_button()
                current_markup = call.message.reply_markup
                if call.message.text != text or not are_keyboards_equal(current_markup, markup):
                    await call.message.edit_text(text, parse_mode="HTML", reply_markup=markup)
                logging.info(f"User {call.from_user.id} viewed post channels stats")

        elif call.data == "back_to_admin_menu":
            await state.finish()
            await Admin.menu.set()
            markup = get_admin_inline_button()
            new_text = "✅ Admin panelga qaytildi!"
            current_markup = call.message.reply_markup
            if call.message.text != new_text or not are_keyboards_equal(current_markup, markup):
                await call.message.edit_text(new_text, reply_markup=markup)
            logging.info(f"User {call.from_user.id} returned to admin menu")

        else:
            await state.finish()
            await Admin.menu.set()
            markup = get_admin_inline_button()
            new_text = "✅ Admin panelga qaytildi!"
            current_markup = call.message.reply_markup
            if call.message.text != new_text or not are_keyboards_equal(current_markup, markup):
                await call.message.edit_text(new_text, reply_markup=markup)
            logging.info(f"User {call.from_user.id} returned to admin menu")

    except Exception as e:
        logging.error(f"Error in process_channel_management: {e}")
        await state.finish()
        await Admin.menu.set()
        markup = get_admin_inline_button()
        new_text = "✅ Admin panelga qaytildi!"
        current_markup = call.message.reply_markup
        if call.message.text != new_text or not are_keyboards_equal(current_markup, markup):
            await call.message.edit_text(new_text, reply_markup=markup)

# Majburiy a'zolik kanalini qo'shish
@dp.message_handler(content_types=["text"], state=ChannelManagement.add_mandatory_channel)
async def add_mandatory_channel(msg: types.Message, state: FSMContext):
    input_text = msg.text.strip()
    parts = input_text.split()
    
    if not parts:
        await msg.answer(
            "❌ Kanal ma'lumotlarini kiriting! Masalan: @ChannelName yoki https://t.me/ChannelName yoki https://t.me/+hash yoki https://www.instagram.com/username [oddiy/yopiq/zayafkali 7 kun]",
            reply_markup=get_back_button()
        )
        logging.error("Empty input for add_mandatory_channel")
        return

    channel_username = None
    channel_link = parts[0]
    channel_type = "oddiy"
    expire_date = None
    platform = 'telegram'

    # Platformani aniqlash va kirishni tahlil qilish
    if channel_link.startswith("https://www.instagram.com/") or channel_link.startswith("www.instagram.com/"):
        platform = 'instagram'
        parts = parts[1:]  # Turi va muddatni qayta ishlash uchun partsni siljitish
    elif channel_link.startswith("@"):
        channel_username = channel_link
        if len(parts) > 1 and parts[1].startswith("https://t.me/"):
            channel_link = parts[1]
            parts = parts[2:]  # Turi va muddatni qayta ishlash uchun partsni siljitish
        else:
            parts = parts[1:]  # Link kiritilmagan, turi va muddatni qayta ishlash
    elif channel_link.startswith("https://t.me/"):
        parts = parts[1:]  # Link kiritilgan, turi va muddatni qayta ishlash
    else:
        await msg.answer(
            "❌ Noto'g'ri format! Iltimos, @ChannelName, https://t.me/ChannelName, https://t.me/+hash yoki https://www.instagram.com/username shaklida yuboring.",
            reply_markup=get_back_button()
        )
        logging.error(f"Invalid channel format: {channel_link}")
        return

    # Kanal linkini validatsiya qilish
    if not await validate_channel_link(msg.bot, channel_link, platform):
        if platform == 'telegram':
            error_message = (
                f"❌ Kanal mavjud emas yoki bot kanalda a'zo emas! "
                f"Agar kanal xususiy bo'lsa, iltimos, botni (@{BOT_NAME}) quyidagi qadamlar orqali kanalga qo'shing:\n"
                "1. Kanal sozlamalariga o'ting (kanal admini sifatida).\n"
                "2. 'A'zolar' bo'limida '@{BOT_NAME}' ni qo'shing yoki taklif linki orqali botni qo'shing.\n"
                "3. Bot kanal a'zolari ro'yxatida ko'rinsin.\n"
                "Keyin qayta urinib ko'ring. Yoki to'g'ri Telegram linkini yuboring (masalan, https://t.me/ChannelName yoki https://t.me/+hash)."
            )
        else:
            error_message = (
                "❌ Noto'g'ri Instagram linki! "
                "Iltimos, faqat Instagram profil linkini yuboring (masalan, https://www.instagram.com/username).\n"
                "Eslatma: Reels, post yoki boshqa turdagi linklar (masalan, /reels/, /p/) qabul qilinmaydi."
            )
        await msg.answer(error_message, reply_markup=get_back_button())
        logging.error(f"Invalid channel link: {channel_link} for platform {platform}")
        return

    # Telegram uchun username validatsiyasi (agar kiritilgan bo'lsa)
    if channel_username and platform == 'telegram' and not await validate_channel_link(msg.bot, channel_username, platform):
        await msg.answer(
            "❌ Noto'g'ri Telegram kanal username formati yoki kanal mavjud emas! Iltimos, @ChannelName shaklida yuboring.",
            reply_markup=get_back_button()
        )
        logging.error(f"Invalid channel username: {channel_username}")
        return

    # Telegram linklari uchun username ni olish (agar kiritilmagan bo'lsa)
    if not channel_username and platform == 'telegram':
        try:
            chat = await msg.bot.get_chat(channel_link)
            channel_username = chat.username if chat.username else None
            logging.info(f"Fetched username for {channel_link}: {channel_username}")
        except Exception as e:
            logging.warning(f"Could not fetch username for {channel_link}: {e}")

    # Kanal turi va muddatni tahlil qilish
    if parts:
        if parts[0].lower() in ["oddiy", "yopiq"]:
            channel_type = parts[0].lower()
        elif parts[0].lower() == "zayafkali":
            channel_type = "zayafkali"
            try:
                days = int(parts[1])
                expire_date = (datetime.datetime.now() + datetime.timedelta(days=days)).strftime("%Y-%m-%d %H:%M:%S")
            except (IndexError, ValueError):
                await msg.answer(
                    "❌ Zayafkali kanal uchun muddatni kunlarda kiriting (masalan: @ChannelName zayafkali 7 yoki https://www.instagram.com/username zayafkali 7)",
                    reply_markup=get_back_button()
                )
                logging.error(f"Invalid zayafkali duration: {input_text}")
                return

    # Kanal nomini olish
    if platform == 'telegram':
        channel_name = channel_username.lstrip("@") if channel_username else channel_link.split("/")[-1]
    else:
        channel_name = channel_link.split("/")[-1].rstrip("/")

    try:
        with sqlite3.connect("hamkor.db") as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT OR IGNORE INTO mandatory_channels 
                (channel_username, channel_link, channel_name, channel_type, channel_platform, expire_date, added_date) 
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    channel_username,
                    channel_link,
                    channel_name,
                    channel_type,
                    platform,
                    expire_date,
                    datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                )
            )
            conn.commit()
            affected = cursor.rowcount

        if affected:
            await msg.answer(
                f"✅ {platform.capitalize()} kanal ({channel_link}{f', {channel_username}' if channel_username else ''}) majburiy a'zolik ro'yxatiga qo'shildi!",
                reply_markup=get_admin_inline_button()
            )
            logging.info(f"Channel added to mandatory_channels: {channel_link}, username: {channel_username}, platform: {platform}")
        else:
            await msg.answer(
                f"⚠️ Bu {platform} kanal allaqachon ro'yxatda mavjud!",
                reply_markup=get_admin_inline_button()
            )
            logging.info(f"Channel already exists in mandatory_channels: {channel_link}, platform: {platform}")
        
        await state.finish()
        await Admin.menu.set()

    except sqlite3.Error as e:
        logging.error(f"Baza xatosi: {e}")
        await msg.answer(
            "❌ Ma'lumotlarni saqlashda xato yuz berdi!",
            reply_markup=get_admin_inline_button()
        )
        await state.finish()

# Majburiy a'zolik kanalini o'chirish
@dp.message_handler(content_types=["text"], state=ChannelManagement.remove_mandatory_channel)
async def remove_mandatory_channel(msg: types.Message, state: FSMContext):
    channel_input = msg.text.strip()
    try:
        with sqlite3.connect("hamkor.db") as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM mandatory_channels WHERE channel_link = ? OR channel_username = ?", (channel_input, channel_input))
            conn.commit()
            affected = cursor.rowcount

        if affected:
            await msg.answer(f"✅ Kanal ({channel_input}) majburiy a'zolik ro'yxatidan o'chirildi!", reply_markup=get_admin_inline_button())
            logging.info(f"Channel removed from mandatory_channels: {channel_input}")
        else:
            await msg.answer("❌ Bunday kanal topilmadi!", reply_markup=get_admin_inline_button())
            logging.info(f"Channel not found in mandatory_channels: {channel_input}")
        
        await state.finish()
        await Admin.menu.set()

    except sqlite3.Error as e:
        logging.error(f"Baza xatosi: {e}")
        await msg.answer("❌ Ma'lumotlarni o'chirishda xato yuz berdi!", reply_markup=get_admin_inline_button())
        await state.finish()

# Post qilish kanalini qo'shish
@dp.message_handler(content_types=["text"], state=ChannelManagement.add_post_channel)
async def add_post_channel(msg: types.Message, state: FSMContext):
    channel_link = msg.text.strip()
    if not await validate_channel_link(msg.bot, channel_link, platform='telegram'):
        await msg.answer(
            "❌ Noto'g'ri kanal formati yoki kanal mavjud emas! Iltimos, @ChannelName yoki https://t.me/ChannelName shaklida yuboring.",
            reply_markup=get_back_button()
        )
        logging.error(f"Invalid channel link: {channel_link}")
        return

    try:
        with sqlite3.connect("hamkor.db") as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT OR IGNORE INTO post_channels (channel_link, channel_name, added_date) VALUES (?, ?, ?)",
                (channel_link, channel_link.split("/")[-1], datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            )
            conn.commit()
            affected = cursor.rowcount

        if affected:
            await msg.answer(f"✅ Kanal ({channel_link}) post qilish ro'yxatiga qo'shildi!", reply_markup=get_admin_inline_button())
            logging.info(f"Channel added to post_channels: {channel_link}")
        else:
            await msg.answer("⚠️ Bu kanal allaqachon ro'yxatda mavjud!", reply_markup=get_admin_inline_button())
            logging.info(f"Channel already exists in post_channels: {channel_link}")
        
        await state.finish()
        await Admin.menu.set()

    except sqlite3.Error as e:
        logging.error(f"Baza xatosi: {e}")
        await msg.answer("❌ Ma'lumotlarni saqlashda xato yuz berdi!", reply_markup=get_admin_inline_button())
        await state.finish()

# Post qilish kanalini o'chirish
@dp.message_handler(content_types=["text"], state=ChannelManagement.remove_post_channel)
async def remove_post_channel(msg: types.Message, state: FSMContext):
    channel_link = msg.text.strip()
    try:
        with sqlite3.connect("hamkor.db") as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM post_channels WHERE channel_link = ?", (channel_link,))
            conn.commit()
            affected = cursor.rowcount

        if affected:
            await msg.answer(f"✅ Kanal ({channel_link}) post qilish ro'yxatidan o'chirildi!", reply_markup=get_admin_inline_button())
            logging.info(f"Channel removed from post_channels: {channel_link}")
        else:
            await msg.answer("❌ Bunday kanal topilmadi!", reply_markup=get_admin_inline_button())
            logging.info(f"Kanal topilmadi: {channel_link}")

        await state.finish()
        await Admin.menu.set()

    except sqlite3.Error as e:
        logging.error(f"Baza xatosi: {e}")
        await msg.answer("❌ Ma'lumotlarni o'chirishda xato yuz berdi!", reply_markup=get_admin_inline_button())
        await state.finish()

# Zayafkali kanallarni tekshirish va o'chirish
async def check_expired_channels():
    try:
        with sqlite3.connect("hamkor.db") as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM mandatory_channels WHERE expire_date IS NOT NULL")
            channels = cursor.fetchall()
            current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            for channel in channels:
                if channel[6] and channel[6] < current_time:  # expire_date is at index 6
                    cursor.execute("DELETE FROM mandatory_channels WHERE id = ?", (channel[0],))
                    logging.info(f"Zayafkali kanal o'chirildi: {channel[2]} ({channel[5]})")  # channel_link, platform
            conn.commit()
    except sqlite3.Error as e:
        logging.error(f"Zayafkali kanallarni tekshirishda xato: {e}")

# Bot ishga tushganda zayafkali kanallarni tekshirish
async def schedule_expired_check():
    while True:
        await check_expired_channels()
        await asyncio.sleep(3600)  # Har soatda tekshirish




from aiogram.dispatcher.filters import Command

@dp.message_handler(Command("help"))
async def send_help(message: types.Message):
     lang = "uz" 
     user_id = message.from_user.id


     await message.answer(about_bot_message(lang,message.from_user.id))






@dp.callback_query_handler(text_contains = "select",state=User.language)
async def qosh(call: types.CallbackQuery,state : FSMContext):
     
     lang = call.data.split(",")[1]
     user_id = call.from_user.id
     username = f"@{call.from_user.username}"
     
     is_vip = await check_premium_func(user_id)


     async with state.proxy() as data:
          data["lang"] = lang

     add_user_base(user_id=user_id,username=username,lang=lang)
     update_statistics_user_base()

     await User.menu.set()
     await call.message.delete()

     async with state.proxy() as data:
          data["lang"] = lang
     
     await call.message.answer(start_message(lang),reply_markup=user_button_btn(lang,is_vip))





async def check_premium_func(user_id):
     user = get_user_base(user_id)
     vip = user[0][5]
     lux = user[0][6]

     is_vip = "True"
     is_lux = "True"
     
     if vip == 0 or vip == "0":
          is_vip = "False"

     if lux == 0 or lux == "0":
          is_lux = "False"
     else:
          today = datetime.now().strftime("%Y-%m-%d")
          today2 = datetime.strptime(today, "%Y-%m-%d")
          users = update_user_vip_over_base(today)

          if users:
               for i in users:
                    try:
                         await dp.bot.kick_chat_member(chat_id=-1002131546047,user_id=i[0])
                    except:
                         pass

          if is_vip == "True":
               is_premium_user = datetime.strptime(vip, "%Y-%m-%d")
          
               if today2 >= is_premium_user:
                    update_user_free_base(user_id)
                    text = "<b>‼️Sizdagi ⚡️AniPass muddati o'z nihoyasiga yetdi !</b>"
                    try:
                         a = await dp.bot.send_message(chat_id=user_id,text=text)
                         await a.pin()
                    except:
                         pass
                    is_vip = "False"
               else:
                    is_vip = "True"
          
          if is_lux == "True":
               is_lux_user = datetime.strptime(lux, "%Y-%m-%d")

               if today2 >= is_lux_user:

                    update_user_free_lux_base(user_id)

                    try:
                         await dp.bot.kick_chat_member(chat_id=-1002131546047,user_id=user_id)
                    except:
                         pass

                    text = "<b>‼️Sizdagi 💎Lux obuna muddati o'z nihoyasiga yetdi !</b>"
                    try:
                         a = await dp.bot.send_message(chat_id=user_id,text=text)
                         await a.pin()
                    except:
                         pass

     return is_vip

async def sponsor_cheking_func(msg,lang):
     
     sponsor = get_sponsor()
     is_sub = False
     
     if not sponsor:
          is_sub = True
          pass
     else:
          for i in sponsor:
               try:
                    user = await dp.bot.get_chat_member(chat_id=i[0],user_id=msg.from_user.id)
               except:
                    delete_sponsor(i[0])
                    continue
               
               if user.status == "left":
                    if i[2] == None:
                         try:
                              chat = await dp.bot.get_chat(chat_id=i[0])
                         except:
                              chat == None
                              
                         if chat != None:
                              if chat.type == "private":
                                   link = chat.invite_link
                              else:
                                   link = f"https://t.me/{chat.username}"
                              update_sponsor(i[0],link)
                         
                         else:
                              delete_sponsor(i[2])
                         
                         sponsor = get_sponsor()
                         
                    await msg.answer(you_should_subscribe_message(lang),reply_markup=sponsors_sub_lists(sponsor))
                    is_sub = False
                    break
               else:
                    is_sub = True

     return is_sub






async def check_premium_func(user_id):
     user = get_user_base(user_id)
     print(user)
     vip = user[0][5]

     lux = user[0][6]

     is_vip = "True"
     is_lux = "True"
     
     if vip == 0 or vip == "0":
          is_vip = "False"

     if lux == 0 or lux == "0":
          is_lux = "False"
     else:
          today = datetime.now().strftime("%Y-%m-%d")
          today2 = datetime.strptime(today, "%Y-%m-%d")
          users = update_user_vip_over_base(today)

          if users:
               for i in users:
                    try:
                         await dp.bot.kick_chat_member(chat_id=-1002131546047,user_id=i[0])
                    except:
                         pass

          if is_vip == "True":
               is_premium_user = datetime.strptime(vip, "%Y-%m-%d")
          
               if today2 >= is_premium_user:
                    update_user_free_base(user_id)
                    text = "<b>‼️Sizdagi ⚡️AniPass muddati o'z nihoyasiga yetdi !</b>"
                    try:
                         a = await dp.bot.send_message(chat_id=user_id,text=text)
                         await a.pin()
                    except:
                         pass
                    is_vip = "False"
               else:
                    is_vip = "True"
          
          if is_lux == "True":
               is_lux_user = datetime.strptime(lux, "%Y-%m-%d")

               if today2 >= is_lux_user:

                    update_user_free_lux_base(user_id)

                    try:
                         await dp.bot.kick_chat_member(chat_id=-1002131546047,user_id=user_id)
                    except:
                         pass

                    text = "<b>‼️Sizdagi 💎Lux obuna muddati o'z nihoyasiga yetdi !</b>"
                    try:
                         a = await dp.bot.send_message(chat_id=user_id,text=text)
                         await a.pin()
                    except:
                         pass

     return is_vip

@dp.message_handler(content_types=["text"],state=User.menu)
async def start(msg:types.Message ,state : FSMContext):

     data = await state.get_data()
     lang = data.get("lang")

     user_id = msg.from_user.id

     is_vip = await check_premium_func(user_id)
     if not lang:
          user_id = msg.from_user.id
          user = get_user_base(user_id)
          lang = user[0][2]
          async with state.proxy() as data:
               data["lang"] = lang
     
     text = msg.text

     if text == "💸Reklama va Homiylik" or text == "💸Reklama va Homiylik":
          admin_user_name = get_user_base(6385061330)[0][1]
          await msg.answer(contacting_message(lang,admin_user_name))
     
     elif text == "🧧 Ongoing animelar" or text == "Ongoing animelar 🧧":
          animes = get_animes_ongoing_base()

          text = "<b>Ongoing animelar 🧧</b> \n°•───────────────────\n"

          num = 0
          
          for i in animes:
               num += 1
               # bot='ANIDUBLE_RASMIY_BOT'
               text += f"<b>{num}.</b> [ <a href='https://t.me/{ANIDUBLE}?start={i[0]}'>{i[1]}</a> ]\n"

          await msg.answer(text)

     if is_vip == "False":
          if text == "⚡️AniPass" or text == "⚡️AniPass":
               is_vip = get_user_is_vip_base(user_id)
               text = f"""
<b>🔥Qaysi turdagi obunani sotib olishni istaysiz ?</b>
"""
               await msg.answer(text,reply_markup=which_vip_clbtn())
               await User.menu.set()
   
          elif text == "🔍Anime Qidirish":
                    text = """<b>📚 Anime nomini yoki kodini yozayotganda e'tiborli bo‘ling!</b>

<i>🔍 Imloviy xatolardan, masalan:</i>
- nuqta `.`
- vergul `,`
- yoki boshqa tinish belgilari kabi xatolardan saqlaning.

<b>📥 Masalan:</b> <i>Solo Leveling</i>
<b>📌 Kalit so‘z:</b> <i>Solo</i>

🧠 <b>Agar tushungan bo‘lsangiz, animening to‘liq nomi yoki kodini kiriting.</b>
<i>❗️ Agar menda topilmasa yoki xatolik yuz bersa, @AniLebot dan qidirib ko‘ring.</i>"""

                    with open("media/aniduble.jpg", "rb") as photo:
                         await msg.answer_photo(
                              photo=photo,
                              caption=text,
                              reply_markup=back_user_button_btn(lang),
                              parse_mode="HTML"
                         )
                    await User.searching.set()

          elif text == "🤝 Hamkorlik dasturi":
               await msg.answer(
                    "<b>🤝 Hamkorlik dasturini amalga oshirmoqchi bo'lsangiz,</b>\n"
                    "<i>📩 @aniduble_admin  bilan bog'laning!</i>\n\n"
                    "<a href='https://t.me/aniduble_admin '>🔗 Sizni kutamiz! 🚀</a>",
                    parse_mode="HTML"
               )
    
     elif is_vip =="True":
          

          if text == "🤝 Hamkorlik dasturi":
               await msg.answer(
                    "<b>🤝 Hamkorlik dasturini amalga oshirmoqchi bo'lsangiz,</b>\n"
                    "<i>📩 @aniduble_admin  bilan bog'laning!</i>\n\n"
                    "<a href='https://t.me/aniduble_admin '>🔗 Sizni kutamiz! 🚀</a>",
                    parse_mode="HTML"
               )
          

          elif text == "📚Qo'llanma" or text == "📚Qo'llanma":
               await msg.answer(about_bot_message(lang,msg.from_user.id))

          elif text == "🔍Anime Qidirish" or text == "🔍Запросить аниме":
               await msg.answer("<b>Qidiruv turini tanlang!</b>",reply_markup=search_clbtn(),parse_mode="HTML")
               await User.searching.set()

          elif text == "📓 Animelar ro'yhati" or text == "Animelar ro'yhati 📓":
               animes = get_animes_base()
          
               f = open(f"animes_list_{msg.from_user.id}.txt", "a",encoding="utf-8")
               text = f"""
     AniDuble botidagi Barcha animelar ro'yxati :
     Barcha animelar soni : {len(animes)} ta
     """       
               num = 0
               for i in animes:
                    num += 1
                    text += f"""
     ----  {num}  ----
     Anime ID : {i[0]}
     Nomi : [ {i[1]} ]
     Janri : {i[2].replace(","," ")}
     """
               f.write(text)
               f.close()

               document = InputFile(f"animes_list_{msg.from_user.id}.txt")

               await msg.answer_document(document=document,caption=f"<b>📓{BOT_NAME} botidagi barcha animelar ro'yxati</b>")
               os.remove(f"animes_list_{msg.from_user.id}.txt")
               await msg.answer(f"{BOT_NAME} botidagi barcha animelar ro'yxati",reply_markup=user_button_btn(lang,is_vip))     

          elif text == "⚡️AniPass":
               is_vip = get_user_is_vip_base(user_id)

               if is_vip and is_vip[0][0]:
                    expiry_date_str = is_vip[0][0]

                    try:
                         expiry_date = datetime.strptime(expiry_date_str, "%Y-%m-%d %H:%M:%S")
                    except ValueError:
                         expiry_date = datetime.strptime(expiry_date_str, "%Y-%m-%d")

                    current_time = datetime.now()
                    time_left = expiry_date - current_time

                    if time_left.total_seconds() > 0:
                         days_left = time_left.days
                         hours_left = time_left.seconds // 3600
                         minutes_left = (time_left.seconds // 60) % 60

                         message = (
                              f"<b>Sizdagi ⚡️AniPass tugash vaqti:</b> {expiry_date_str}\n"
                              f"<b>Qolgan vaqt:</b> {days_left} kun, {hours_left} soat, {minutes_left} daqiqa"
                         )
                    else:
                         message = (
                              f"<b>Sizdagi ⚡️AniPass muddati tugagan!</b>\n"
                         )
               
               else:
                    message = "<b>Sizda ⚡️AniPass mavjud emas yoki muddati aniqlanmadi.</b>"
               await msg.answer(message, reply_markup=user_button_btn(lang, is_vip))

          vip = data.get("vip")

          if not vip:
               async with state.proxy() as data:
                    data["lang"] = lang
                    data["vip"] = is_vip

@dp.callback_query_handler(text_contains = "search_rasm",state=User.searching)
async def start(call: types.CallbackQuery,state : FSMContext):
     lang = (await state.get_data()).get("lang")
     
     await call.message.delete()
     caption = """<b>🔍 Rasm orqali qidiruv</b>

<i>Qidirilishi kerak bo‘lgan anime sahnasining suratini yuboring.</i>

<b>‼️ DIQQAT:</b>
<i>Yaxshi natija olish uchun quyidagilarga amal qiling:</i>
• 🎥 Animening <u>videosidan olingan skrinshot</u> bo‘lishi kerak  
• ✂️ Faqat <u>asosiy sahna yoki qahramon tasviri</u> bo‘lishi lozim  
• 🚫 Poster, banner yoki reklamalarni yubormang!
"""

     with open("media/aniduble.jpg", "rb") as photo:
          await call.message.answer_photo(
               photo=photo,
               caption=caption,
               reply_markup=back_user_button_btn(lang),
               parse_mode="HTML"
          )

     await User.search_by_photo.set()


@dp.callback_query_handler(text_contains = "search_id_name",state=User.searching)
async def start(call: types.CallbackQuery,state : FSMContext):
     lang = (await state.get_data()).get("lang")
     await call.message.delete()
     text = """<b>📚 Anime nomini yoki kodini yozayotganda e'tiborli bo‘ling!</b>

<i>🔍 Imloviy xatolardan, masalan:</i>
- nuqta `.`
- vergul `,`
- yoki boshqa tinish belgilari kabi xatolardan saqlaning.

<b>📥 Masalan:</b> <i>Solo Leveling</i>
<b>📌 Kalit so‘z:</b> <i>Solo</i>

🧠 <b>Agar tushungan bo‘lsangiz, animening to‘liq nomi yoki kodini kiriting.</b>
<i>❗️ Agar menda topilmasa yoki xatolik yuz bersa, @AniLebot dan qidirib ko‘ring.</i>"""

     with open("media/aniduble.jpg", "rb") as photo:
          await call.message.answer_photo(
               photo=photo,
               caption=text,
               reply_markup=back_user_button_btn(lang),
               parse_mode="HTML"
          )
     await User.searching.set()

@dp.callback_query_handler(text_contains="search_teg", state=User.searching)
async def handle_search_tag(call: types.CallbackQuery, state: FSMContext):
     data = await state.get_data()
     lang = data.get("lang")
     user_id = call.from_user.id 
     protect = True  

     await call.message.delete()

     result = get_random_anime_sql()  
     serie_id = result[0][2]
     is_vip_user = data.get("vip")
              
     have_serie = False
     if result[0][8] > 0:
          have_serie = True


     trailer_id = result[0][2]
     anime_id = result[0][0]
     is_vip = result[0][10]

     trailer = await dp.bot.forward_message(message_id=trailer_id,chat_id=user_id,from_chat_id=anime_treller_chat)

     await state.finish()

     async with state.proxy() as data:
          data["trailer"] = trailer.message_id
          data["have_serie"] = have_serie
          data["lang"] = lang
          data["vip"] = is_vip_user

     await User.anime_menu.set()
     await call.message.answer(anime_menu_message(lang,result),reply_markup=anime_menu_clbtn(lang,anime_id,False,have_serie,is_vip))
     await call.answer()  


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dp.callback_query_handler(text_contains='search_anime_id', state=User.searching)
async def prompt_genre_input(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    lang = data.get("lang", "uz")
    
    await call.message.delete()
    caption = f"""<b>📚 {BOT_NAME} Bot: Janr orqali qidiruv</b>

<i>Endi siz o‘zingizga yoqadigan anime janrlarini yozib, ular bo‘yicha tavsiyalar olishingiz mumkin!</i>

🔍 <b>Masalan:</b> <i>Ekshen, Komediya, Drama</i>

🤖 <b>Bot shu janrda mavjud animelarni ko‘rsatadi.</b>
<i>Bu orqali siz o‘z sevimli janringizdagi animelarni tez va oson topishingiz mumkin.</i>
"""
    with open("media/aniduble.jpg", "rb") as photo:
          await call.message.answer_photo(
               photo=photo,
               caption=caption,
               reply_markup=back_user_button_btn(lang),
               parse_mode="HTML"
          )

     
    await User.genre_input.set()
    await call.answer()

@dp.message_handler(state=User.genre_input)
async def handle_genre_search(message: types.Message, state: FSMContext, page=1):
    user_genre = message.text.strip().lower()
    data = await state.get_data()
    lang = data.get("lang", "uz")
    user_id = message.from_user.id
    items_per_page = 10

    async with state.proxy() as data:
        data["search_query"] = user_genre
        data["page"] = page

    logger.info(f"Searching for genre: {user_genre}, page: {page}")

    try:
        cursor.execute("SELECT DISTINCT genre FROM anime")
        raw_genres = [genre[0].lower() for genre in cursor.fetchall() if genre[0]]
        
        all_genres = []
        for genre in raw_genres:
            all_genres.extend([g.strip() for g in genre.split(",") if g.strip()])
        all_genres = list(set(all_genres)) 
        logger.info(f"All genre tags: {all_genres}")
        matched_genres = []
        if process and fuzz:
            matches = process.extract(user_genre, all_genres, scorer=fuzz.token_sort_ratio, limit=5)
            matched_genres = [match[0] for match in matches if match[1] >= 60]
            logger.info(f"Fuzzy matched genres: {matches}")
            if user_genre in all_genres:
                matched_genres.append(user_genre)
        else:
            matched_genres = [user_genre] if user_genre in all_genres else []
            logger.warning("fuzzywuzzy not installed, using exact match")

        matched_genres = list(set(matched_genres))  
        logger.info(f"Final matched genres: {matched_genres}")

        if not matched_genres:
            await message.answer(
                f"'{user_genre}' janrida anime topilmadi! Iltimos, boshqa janr kiriting." if lang == "uz" else
                f"Аниме жанра '{user_genre}' не найдено! Попробуйте другой жанр."
            )
            return

        # Build SQL query for matched genres
        like_conditions = " OR ".join([f"LOWER(genre) LIKE ?" for _ in matched_genres])
        query_params = [f"%{genre}%" for genre in matched_genres]

        # Count total matching anime for pagination
        cursor.execute(f"""
            SELECT COUNT(*) 
            FROM anime 
            WHERE {like_conditions}
        """, query_params)
        total_anime = cursor.fetchone()[0]
        logger.info(f"Total anime found: {total_anime}")

        # Fetch anime for current page
        cursor.execute(f"""
            SELECT anime_id, name, views 
            FROM anime 
            WHERE {like_conditions}
            ORDER BY views DESC
            LIMIT ? OFFSET ?
        """, query_params + [items_per_page, (page - 1) * items_per_page])
        anime_list = cursor.fetchall()
        logger.info(f"Animes fetched: {len(anime_list)}")
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        await message.answer(
            "Ma'lumotlar bazasida xato yuz berdi!" if lang == "uz" else "Ошибка в базе данных!"
        )
        return

    if anime_list:
        inline_keyboard = InlineKeyboardMarkup(row_width=1)
        for anime in anime_list:
            anime_id, anime_name, views = anime
            callback_data = f"anime_select_{anime_id}"
            button = InlineKeyboardButton(
                text=f"{anime_name} - {views} ko'rish" if lang == "uz" else f"{anime_name} - {views} просмотров",
                callback_data=callback_data
            )
            inline_keyboard.add(button)

        # Add pagination buttons if needed
        if total_anime > items_per_page:
            nav_buttons = []
            if page > 1:
                nav_buttons.append(InlineKeyboardButton(
                    text="⬅️ Oldingi" if lang == "uz" else "⬅️ Предыдущая",
                    callback_data=f"genre_page_{page-1}_{user_genre}"
                ))
            if page * items_per_page < total_anime:
                nav_buttons.append(InlineKeyboardButton(
                    text="Keyingi ➡️" if lang == "uz" else "Следующая ➡️",
                    callback_data=f"genre_page_{page+1}_{user_genre}"
                ))
            inline_keyboard.row(*nav_buttons)

        try:
            await dp.bot.send_message(
                chat_id=user_id,
                text=(
                    f"'{user_genre}' janridagi animelar ro'yxati (sahifa {page}):"
                    if lang == "uz" else
                    f"Список аниме жанра '{user_genre}' (страница {page}):"
                ),
                reply_markup=inline_keyboard
            )
        except Exception as e:
            logger.error(f"Message send error: {str(e)}")
            await message.answer(
                "Xabar yuborishda xato yuz berdi!" if lang == "uz" else "Ошибка при отправке сообщения!"
            )
            return
    else:
        await dp.bot.send_message(
            chat_id=user_id,
            text=(
                f"'{user_genre}' janrida anime topilmadi!" if lang == "uz" else
                f"Аниме жанра '{user_genre}' не найдено!"
            )
        )

    await User.menu.set()

@dp.callback_query_handler(lambda c: c.data.startswith("genre_page_"), state="*")
async def handle_pagination(call: types.CallbackQuery, state: FSMContext):
    try:
        parts = call.data.split("_", 3)
        if len(parts) != 4:
            raise ValueError("Invalid callback data format")
        _, _, page, genre = parts
        page = int(page)
    except (IndexError, ValueError) as e:
        logger.error(f"Pagination error: {str(e)}")
        await call.answer("Noto'g'ri sahifa formati!", show_alert=True)
        return

    async with state.proxy() as data:
        data["page"] = page
        data["search_query"] = genre

    await call.message.delete()

    # Create a fake message to reuse handle_genre_search
    class FakeMessage:
        def __init__(self, text, from_user):
            self.text = text
            self.from_user = from_user

    await handle_genre_search(
        FakeMessage(text=genre, from_user=call.from_user),
        state,
        page=page
    )
    await call.answer()

@dp.callback_query_handler(text_contains="search_top_10", state=User.searching)
async def handle_search_top_10(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    lang = data.get("lang", "uz")
    user_id = call.from_user.id
    await call.message.delete()

    try:
        cursor.execute("""
            SELECT anime_id, name, views 
            FROM anime 
            ORDER BY views DESC 
            LIMIT 10
        """)
        top_anime = cursor.fetchall()
    except Exception as e:
        await call.message.answer("Ma'lumotlar bazasida xato yuz berdi!")
        await call.answer()
        return

    if top_anime:
        inline_keyboard = InlineKeyboardMarkup(row_width=1)
        for anime in top_anime:
            anime_id, anime_name, views = anime
            callback_data = f"anime_select_{anime_id}"
            button = InlineKeyboardButton(text=f"{anime_name} - {views} ko'rish", callback_data=callback_data)
            inline_keyboard.add(button)
        try:
            await dp.bot.send_message(
                chat_id=user_id,
                text="Top 10 eng ko'p ko'rilgan anime ro'yxati:" if lang == "uz" else "Топ-10 самых просматриваемых аниме:",
                reply_markup=inline_keyboard
            )
        except Exception as e:
            await call.message.answer("Xabar yuborishda xato yuz berdi!")
            await call.answer()
            return
    else:
        await dp.bot.send_message(
            chat_id=user_id,
            text="Hozircha top 10 anime mavjud emas!" if lang == "uz" else "Нет аниме в топ-10!"
        )

    await User.menu.set()
    await call.answer()

@dp.callback_query_handler(lambda c: c.data.startswith("anime_select_"), state="*")
async def handle_anime_selection(call: types.CallbackQuery, state: FSMContext):
    try:
        anime_id = int(call.data.split("_", 2)[2])
    except (IndexError, ValueError):
        await call.answer("Noto‘g‘ri formatdagi ID!", show_alert=True)
        return

    try:
        cursor.execute("""
               SELECT anime_id, lang, treller_id, name, about, genre, teg, dub, series, films, is_vip, status, views 
               FROM anime 
               WHERE anime_id = ?
          """, (anime_id,))

        anime = cursor.fetchall()
    except Exception as e:
        await call.answer("Ma'lumotlar bazasida xato yuz berdi!", show_alert=True)
        return

    if not anime:
        await call.answer("Anime topilmadi!", show_alert=True)
        return

    anime_data = anime[0]
    data = await state.get_data()
    lang = data.get("lang", "uz")
    is_vip_user = data.get("vip", False)

    await call.message.delete()

    try:
        trailer_id = anime_data[2]
        have_serie = anime_data[8] > 0
        is_vip = anime_data[10]
        trailer = await dp.bot.forward_message(
            chat_id=call.from_user.id,
            from_chat_id=anime_treller_chat,
            message_id=trailer_id
        )

        async with state.proxy() as data:
            data["trailer"] = trailer.message_id
            data["have_serie"] = have_serie
            data["lang"] = lang
            data["vip"] = is_vip_user

        await call.message.answer(
            anime_menu_message(lang, anime),
            reply_markup=anime_menu_clbtn(lang, anime_data[0], False, have_serie, is_vip)
        )
    except Exception as e:
        await call.answer("Anime ma'lumotlarini ko‘rsatishda xato yuz berdi!", show_alert=True)
        return

    await User.anime_menu.set()
    await call.answer()

@dp.message_handler(state=User.search_by_photo)
async def start(msg: types.Message, state: FSMContext):
     text = msg.text
     lang = (await state.get_data()).get("lang")
     user_id = msg.from_user.id
     is_vip = await check_premium_func(user_id)
     if text == "🔙Ortga":
          await state.finish()
          await User.menu.set()
          async with state.proxy() as data:
               data["lang"] = lang

          await msg.answer("🔥",reply_markup=user_button_btn(lang,is_vip))


@dp.message_handler(content_types=["photo"], state=User.search_by_photo)
async def start(msg: types.Message, state: FSMContext):

     lang = (await state.get_data()).get("lang")

     try:
          shutil.rmtree(f"anime_image_{msg.from_user.id}")
     except:
          pass

     try:
          path = f"anime_image_{msg.from_user.id}/anime.jpg"
          a = await msg.answer("♻️<b>Serverga yuklanmoqda</b> . . .")
          await msg.photo[-1].download(destination_file=path)

          with open(path, "rb") as f:
               image_bytes = f.read()

          result = await handle_photo_from_file(image_bytes, BOT_TOKEN)
          await User.menu.set()

          if "error" in result:
               await msg.answer(result["error"])
               return

          await a.delete()

          caption = (
               f"🎌 Anime topildi!\n"
               f"📛 <b>Nomi</b>: {result['uzbek_title']}\n"
               f"🎞 <b>Epizod</b>: {result['episode']}\n"
               f"🕒 <b>Vaqti</b>: {result['minutes']} daqiqa {result['seconds']} soniya\n"
               f"🎯 <b>Aniqlik</b>: {result['similarity']}%\n"
               f"🏷 <b>Janr</b>: {result['genre']}"
          )

          await msg.answer_photo(photo=result["image"], caption=caption)
          if result.get("video"):
               await msg.answer_video(video=result["video"])

          shutil.rmtree(f"anime_image_{msg.from_user.id}")
     except:
          await msg.answer(error_try_again_message(lang))


@dp.message_handler(state=[User.searching,User.anime_menu,User.watching])
async def start(msg:types.Message ,state : FSMContext):

     data = await state.get_data()
     lang = data.get("lang")
     is_vip_user = data.get("vip")


     text = msg.text

     
     user_id = msg.from_user.id

     if text != "🔙Ortga":

          anime = search_anime_base(text)
          
          if not anime:
               await msg.answer(not_found_this_anime_message(lang,text),reply_markup=back_button_btn())

               await state.finish()
               await User.menu.set()
               async with state.proxy() as data:
                    data["lang"] = lang
               await msg.answer(main_menu_message(lang),reply_markup=user_button_btn(lang,is_vip_user))
          else:
               if text.isdigit():
                    await msg.answer(select_function_message(lang),reply_markup=admin_searched_animes_clbtn(anime))
               else:
                    a = await msg.answer("⏳",reply_markup=back_user_button_btn(lang))
                    await a.delete()
                    
                    count = len(anime)
                    
                    if count == 1:
                         await msg.answer(anime_found_message(lang))
                         
                         have_serie = False
                         if anime[0][8] > 0:
                              have_serie = True
                         
                         is_vip = anime[0][10]

                         trailer_id = anime[0][2]
                         anime_id = anime[0][0]
                         trailer = await dp.bot.forward_message(message_id=trailer_id,chat_id=user_id,from_chat_id=anime_treller_chat)
                         await state.finish()

                         async with state.proxy() as data:
                              data["trailer"] = trailer.message_id
                              data["have_serie"] = have_serie
                              data["lang"] = lang
                              data["vip"] = is_vip_user

                         await User.anime_menu.set()
                         await msg.answer(anime_menu_message(lang,anime),reply_markup=anime_menu_clbtn(lang,anime_id,False,have_serie,is_vip))
                         
                    else:
                         await msg.answer(select_function_message(lang),reply_markup=admin_searched_animes_clbtn(anime))
               
     else:
          await state.finish()
          await User.menu.set()
          async with state.proxy() as data:
               data["lang"] = lang
          await msg.answer(main_menu_message(lang),reply_markup=user_button_btn(lang,is_vip_user))

@dp.callback_query_handler(text_contains = "which",state=User.menu)
async def qosh(call: types.CallbackQuery,state : FSMContext):

     data = await state.get_data()
     lang = data.get("lang")

     vip_type = call.data.split(",")[1]
     await call.message.delete()

     if vip_type == "vip":
          text = (
    f"💫 <b>{BOT_NAME} botidan ⚡️ AniPass</b> sotib olganingizdan keyingi qulayliklar:\n"
    "°•───────────────────\n"
    "🎉 <b>Qulayliklar</b>\n\n"
    "🔹️ Botni 2x tezlikda ishlatish\n"
    "🔹️ Botdan mukammal va erkin foydalana olish\n"
    "🔹️ Eski seriyalar o'chmaydi\n"
    "🔹️ Homiy kanallarga a'zo bo‘lish shart emas\n"
    "🔹️ Botdan sizga qo‘shimcha reklamalar kelmaydi va bezovta qilmaydi\n"
    "°•───────────────────\n"
    "🎟 <b>Qo‘shiladigan tugmalar</b>\n\n"
    "🔹️ Rasm orqali qidiruv\n"
    "🔹️ Tasodifiy anime\n"
    "🔹️ Eng ko‘p ko‘rilgan animelar\n"
    "🔹️ Janr orqali qidiruv\n\n"
    "⚠️ <i>Eslatma:</i>\n"
    "⚡️ AniPass faqat bot uchun amal qiladi\n"
    "⚡️ AniPass narxi atiga: <b>5.000 so‘m 💵</b>"
)

          await call.message.answer_animation(animation=open("media/vip.mp4","rb"),caption=text,reply_markup=vip_buying_clbtn())

     else:

          text = f"""
🔥 <b>AniDuble botidan 💎 Lux Kanalga ulanish uchun ma'lumotlar :<i>
°•───────────────────
Endilikda Echchi va Hentai animelarni o'zbek tilida Lux Kanalimizda ko'rishingiz mumkun 
°•───────────────────
Lux kanalga Echchi va hentai animelar o'zbek tilida joylab boriladi 💎
°•───────────────────
💎Lux Kanal uchun  obuna sotib olish narxlarni menu dan tanlashingiz mumkin</i></b>
"""                 
          await call.message.answer_animation(animation=open("media/vip_channel.mp4","rb"),caption=text,reply_markup=vip_channel_clbtn())


@dp.callback_query_handler(text_contains="free", state=User.menu)
async def qosh(call: types.CallbackQuery, state: FSMContext):
     data = await state.get_data()
     lang = data.get("lang")
     user_id = call.from_user.id
     is_vip = get_user_is_vip_base(user_id)
    

     await User.buying_vip.set()
     a = await call.message.answer(". . .", reply_markup=user_button_btn(lang,is_vip))
     await a.delete()
     await call.message.delete()
     if get_free_status(user_id)>0:
          await call.message.answer(
                    f"""({call.from_user.username} ) 😕 Foydalanuvchi siz uchun 5 kun tekin AniPass obunasi o'z nihoyasiga yetdi 
🎉 Agar siz AniPass sotib olishni hohlasangiz pastdagi 💸 Sotib olish tugmasini bosing""",
                    reply_markup=vip_2nd_buying_clbtn()
          )

     elif get_free_status(user_id) == 0:
          await call.message.bot.send_message(
                    call.from_user.id,
                    "🔹️ Siz haqiqatdan ham free AniPass ni faollashtirmoqchimiz ?",
                    reply_markup=true_false_link_clbtn()
          )


@dp.callback_query_handler(text_contains="HA", state=User.buying_vip)
async def qosh(call: types.CallbackQuery, state: FSMContext):
     data = await state.get_data()
     lang = data.get("lang")
     is_vip = data.get("vip")

     await User.buying_vip.set()
     a = await call.message.answer(". . .", reply_markup=user_button_btn(lang,is_vip))
     await a.delete()
     await call.message.delete()
     user_id = call.from_user.id

     date_1 = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
     date_1 = datetime.strptime(date_1, "%Y-%m-%d %H:%M:%S")
     result = date_1 + relativedelta(days= +5)
     result = str(result)[:-9]  
     update_free_status(user_id,1)
     update_user_vip_base(user_id, result)


     text = (
    f"🎉 <b>{call.from_user.username}</b>!\n\n"
    f"🎊 <b>Tabriklaymiz!</b> Siz <b>{BOT_NAME}</b> botidan tekinga <b>AniPass</b> aktivlashtirdingiz ✅️\n\n"
    "⚠️ <i>Eslatma:</i>\n"
    "Bu obuna faqat <b>5 kun</b> amal qiladi.\n"
    "5 kundan so‘ng <b>AniPass</b> avtomatik tarzda bekor bo‘ladi.\n\n"
    "Atigi oyiga <b>5 000 so‘m</b> to‘lab yana o‘sha imkonyatlardan bemalol foydalanishingiz mumkin 🎥✨"
)
     await call.message.answer(text, reply_markup=vip_2nd_buying_clbtn(),parse_mode="HTML")

@dp.callback_query_handler(text_contains="Keyinroq", state=User.buying_vip)
async def qosh(call: types.CallbackQuery, state: FSMContext):
     data = await state.get_data()
     lang = data.get("lang")
     is_vip = data.get("vip")

     await call.message.delete()
     await User.menu.set()
     await call.message.answer("<b>✅Bekor qilindi</b>",reply_markup=user_button_btn(lang,is_vip))

@dp.callback_query_handler(text_contains = "vip",state=User.menu)
async def qosh(call: types.CallbackQuery,state : FSMContext):

     data = await state.get_data()
     lang = data.get("lang")

     vip_type = call.data.split(",")[1]

     if vip_type == "vip":

          await User.buying_vip.set()
          a = await call.message.answer(". . .",reply_markup=user_button_btn(lang,vip_type))
          await a.delete()
          await call.message.delete()

          text = f"""
<b>🔥{BOT_NAME} botida ⚡️AniPass obuna sotib olish uchun :</b>

1. <code>{KARTA_RAQAM}</code>
   <b>( {KARTA_NOMI} )</b>

<b>kartaga 💵5.000 so'm miqdorda pul o'tkazing</b>

<b>2. 🧾Pul o'tganligi haqida chekni rasmini yuboring !</b>
"""
     
          await call.message.answer(text,reply_markup=vip_2nd_buying_clbtn())
          await asyncio.sleep(5)
          await call.answer("🧾Pul o'tkazilganligi haqida chekni rasmini yuboring . . .")

     else:

          month = int(call.data.split(",")[2])

          await User.buying_lux.set()
          a = await call.message.answer(". . .",reply_markup=user_button_btn(lang,vip_type))
          await a.delete()
          await call.message.delete()

          async with state.proxy() as data:
               data["month"] = month

          text = f"""
<b>Qoidalar 💡
🔥 AniDuble Lux kanaliga obuna sotib olganingizdan keyin 
Bot sizga faqat bir martda silka beradi ⚡️ <i>
°•───────────────────
Agar kanaldan chqib ketsangiz bot ham admin ham boshqa silka tashlamaydi 💡
°•───────────────────
Agar chiqib ketganingizdan so'ng yana lux kanalga qo'shilmoqchi bo'lsangiz boshqattan to'lo'v 
qilishingizga to'g'ri keladi
 
°•───────────────────</i>
Kanalga qo'shilish uchun 💎

<code>9860 1201 6396 3172</code>

Umarbek Azimov
°•───────────────────
Kartaga {month} oylik obuna uchun - {month*20}.000 so'm miqdorda pul o'tkazing
Va botga skrenshot ni rasm tarzda yuboring ( Fayl format yoki rasmni siqilgan holda tashlasangiz bot qabul qilmaydi ) ⚠️</b>
"""
     
          await call.message.answer(text,reply_markup=vip_2nd_buying_clbtn())
          await asyncio.sleep(5)
          await call.answer("🧾Pul o'tkazilganligi haqida chekni rasmini yuboring . . .")

@dp.callback_query_handler(text_contains = "back",state=[User.buying_vip,User.buying_lux])
async def qosh(call: types.CallbackQuery,state : FSMContext):

     data = await state.get_data()
     lang = data.get("lang")

     is_vip_user = data.get("vip")

     await call.message.delete()
     await User.menu.set()
     await call.message.answer("<b>✅Bekor qilindi</b>",reply_markup=user_button_btn(lang,is_vip_user))

@dp.message_handler(state=User.buying_vip,content_types=["photo"])
async def start(msg:types.Message ,state : FSMContext):

     data = await state.get_data()
     lang = data.get("lang")

     user_id = msg.from_user.id
     is_vip = data.get("vip")

     a = await dp.bot.forward_message(chat_id=vip_buying_chat,message_id=msg.message_id,from_chat_id=user_id)

     text = f"""
<b>ID :</b> <code>{user_id}</code>
-
<b>⚡️AniPass obuna sotib olish uchun so'rov yuborilgan</b>
"""

     await a.reply(text,reply_markup=vip_activate_clbtn(user_id))

     await User.menu.set()
     await msg.answer("<b>✅Sizning sorovingiz adminlarga yuborildi ! Tez orada javob olasiz</b>",reply_markup=user_button_btn(lang,is_vip))

@dp.message_handler(state=User.buying_lux,content_types=["photo"])
async def start(msg:types.Message ,state : FSMContext):

     data = await state.get_data()
     lang = data.get("lang")
     month = int(data.get("month"))

     user_id = msg.from_user.id

     a = await dp.bot.forward_message(chat_id=vip_buying_chat,message_id=msg.message_id,from_chat_id=user_id)

     text = f"""
<b>ID :</b> <code>{user_id}</code>
-
<b>{month} oyga 💎Lux kanalga obuna bo'lmoqchi</b>
"""
     
     await a.reply(text,reply_markup=lux_activate_clbtn(user_id))
     await User.menu.set()
     await msg.answer("<b>✅Sizning so'rovingiz adminlarga yuborildi ! Tez orada javob olasiz</b>",reply_markup=user_button_btn(lang))


@dp.callback_query_handler(text_contains = "search",state=[User.searching,User.anime_menu,User.watching])
async def qosh(call: types.CallbackQuery,state : FSMContext):
     anime_id = call.data.split(",")[1]

     data = await state.get_data()
     lang = data.get("lang")
     is_vip_user= data.get("vip")

     user_id = call.from_user.id
     if anime_id.isdigit():
          anime_id = int(anime_id)
          anime = get_anime_base(anime_id)

          await call.message.delete()
                    
          have_serie = False
          if anime[0][8] > 0:
               have_serie = True

          trailer_id = anime[0][2]
          anime_id = anime[0][0]
          is_vip = anime[0][10]
          
          trailer = await dp.bot.forward_message(message_id=trailer_id,chat_id=user_id,from_chat_id=anime_treller_chat)
          
          await state.finish()

          async with state.proxy() as data:
               data["trailer"] = trailer.message_id
               data["have_serie"] = have_serie
               data["lang"] = lang
               data["vip"] = is_vip_user

          await User.anime_menu.set()
          await call.message.answer(anime_menu_message(lang,anime),reply_markup=anime_menu_clbtn(lang,anime_id,False,have_serie,is_vip))
 
     else:
          await call.message.delete()
          await state.finish()
          await User.menu.set()

          async with state.proxy() as data:
               data["lang"] = lang

          await call.message.answer("🔥",reply_markup=user_button_btn(lang,is_vip_user))



@dp.callback_query_handler(text_contains = "anime",state=User.anime_menu)
async def qosh(call: types.CallbackQuery,state : FSMContext):

     data = await state.get_data()
     lang = data.get("lang")
     is_vip_user= data.get("vip")
     have_serie = data.get("have_serie")

     user_id = call.from_user.id

     command = call.data.split(",")[1]
     if command != "back":

          anime_id = int(call.data.split(",")[2])
          
          if command == "about":
               anime = get_anime_base(anime_id)
               is_vip = anime[0][10]
               about = get_anime_about_base(anime_id)[0][0]
               await call.message.edit_text(about,reply_markup=anime_menu_clbtn(lang,anime_id,True,have_serie,is_vip))
          elif command == "main":
               anime = get_anime_base(anime_id)
               is_vip = anime[0][10]

               await call.message.edit_text(anime_menu_message(lang,anime),reply_markup=anime_menu_clbtn(lang,anime_id,False,have_serie,is_vip))

          elif command == "watch":

               next_states = True

               is_vip_anime = call.data.split(",")[3]
               if is_vip_anime == "vip":
                    if is_vip_user == "True":
                         next_states = True
                    else:
                         await call.answer("‼️Ushbu animeni tomosha qilish uchun ⚡️AniPass sotib olishingiz kerak !",show_alert=True)
                         next_states = False

               if next_states == True:
                    trailer = data.get("trailer")
                    if trailer is not None:
                         trailer = int(trailer)
                    else:
                         trailer = 0
                    try:
                         await dp.bot.delete_message(chat_id=user_id,message_id=trailer)
                    except:
                         pass

                    await call.message.delete()
                    series = get_anime_series_base(anime_id)
                    if len(series) > 0:
                         serie_id = series[0][1]
                         serie_num = series[0][2]
                         serie_quality = series[0][3]

                         await state.finish()
                         await User.watching.set()

                         if is_vip_anime == "True":
                              protect = True
                         else:
                              protect = False
                         
                         a = await dp.bot.forward_message(chat_id=user_id,message_id=serie_id,from_chat_id=anime_series_chat,protect_content=protect)

                         async with state.proxy() as data:
                              data["lang"] = lang
                              data["serie"] = a.message_id
                              data["vip"] = is_vip_user
                              data["vip_anime"] = is_vip_anime

                         update_anime_views_base(anime_id)
                         await call.message.answer(anime_serie_message(lang,serie_num,serie_quality),reply_markup=anime_series_clbtn(1,series))
                    else:
                         await call.message.answer("�� Ushbu animeni seriyasi yo'q!")
                    
     else:
          trailer = int(data.get("trailer"))
          try:
               await dp.bot.delete_message(chat_id=user_id,message_id=trailer)
          except:
               pass
          await call.message.delete()
          await state.finish()
          await User.menu.set()

          if not lang:
               user = get_user_base(call.from_user.id)
               lang = user[0][2]

          async with state.proxy() as data:
               data["lang"] = lang
          await call.message.answer(main_menu_message(lang),reply_markup=user_button_btn(lang,is_vip_user))

@dp.callback_query_handler(text_contains = "watching",state=User.watching)
async def qosh(call: types.CallbackQuery,state : FSMContext):
     data = await state.get_data()
     lang = data.get("lang")
     is_vip_user = data.get("vip")
     is_vip_anime = data.get("vip_anime")

     user_id = call.from_user.id

     command = call.data.split(",")[1]
     if command == "now":
          await call.answer(you_watch_this_now_message(lang))
     elif command == "back":
          serie = int(data.get("serie"))

          if is_vip_user == "False":
               try:
                    await dp.bot.delete_message(chat_id=user_id,message_id=serie)
               except:
                    pass

          await call.message.delete()
          await state.finish()
          await User.menu.set()
          async with state.proxy() as data:
               data["lang"] = lang
               data["vip"] = is_vip_user
          await call.message.answer(main_menu_message(lang),reply_markup=user_button_btn(lang,is_vip_user))

     elif command == "watch":

          serie = int(data.get("serie"))

          if is_vip_user == "False":

               try:
                    await dp.bot.delete_message(chat_id=user_id,message_id=serie)
               except:
                    pass

          await call.message.delete()

          serie_id = int(call.data.split(",")[2])
          serie_num = int(call.data.split(",")[3])
          serie_quality = call.data.split(",")[4]
          which_anime = int(call.data.split(",")[5])
          page = int(call.data.split(",")[6])

          series = get_anime_series_base(which_anime)

          if is_vip_anime == "True":
               protect = True
          else:
               protect = False

          a = await dp.bot.forward_message(chat_id=user_id,message_id=serie_id,from_chat_id=anime_series_chat,protect_content=protect)

          async with state.proxy() as data:
               data["lang"] = lang
               data["serie"] = a.message_id

          await call.message.answer(anime_serie_message(lang,serie_num,serie_quality),reply_markup=anime_series_clbtn(serie_num,series,page))

     elif command == "next" or command == "previous":

          page = int(call.data.split(",")[2])
          serie_num = int(call.data.split(",")[4])
          anime_id = int(call.data.split(",")[3])

          series = get_anime_series_base(anime_id)
          await call.message.edit_reply_markup(anime_series_clbtn(serie_num,series,page))

@dp.message_handler(content_types=["text"])
async def start(msg:types.Message ,state : FSMContext):
     if str(msg.chat.id)[0] == "-":
          pass
     else:
          await msg.answer("🔥New update /start")