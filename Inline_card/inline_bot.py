from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup, InlineQueryResultArticle, InputTextMessageContent
from aiogram.utils import executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
import logging
import uuid
import sys
import os
import time
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from users_base import get_random_anime_sql, search_anime_base,get_anime_series_base
from database import init_db, add_user, get_all_users, add_mandatory_channel, get_mandatory_channels, remove_mandatory_channel

from dotenv import load_dotenv
logging.basicConfig(level=logging.INFO)
from functools import wraps
from aiogram import types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

load_dotenv()

TOKEN = os.getenv('TOKEN')
ADMIN_IDS = [5306481482,6699160460]  

bot = Bot(token=TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

# FSM holatlari
class BroadcastState(StatesGroup):
    waiting_for_message = State()

class AddChannelState(StatesGroup):
    waiting_for_channel = State()

class RemoveChannelState(StatesGroup):
    waiting_for_channel_id = State()

# Bot ishga tushganda bazani ishga tushirish
async def on_startup(_):
    init_db()
    logging.info("Bot started and database initialized")

# Majburiy a'zolikni tekshirish
async def check_subscription(user_id):
    channels = get_mandatory_channels()
    if not channels:
        return True, [] 
    not_subscribed = []
    for channel_id, channel_username in channels:
        try:
            member = await bot.get_chat_member(channel_id, user_id)
            if member.status in ["left", "kicked"]:
                not_subscribed.append((channel_id, channel_username))
        except Exception as e:
            logging.error(f"Error checking subscription for {channel_id}: {e}")
            continue
    return len(not_subscribed) == 0, not_subscribed


def subscription_required(handler):
    @wraps(handler)
    async def wrapper(message: types.Message, *args, **kwargs):
        is_subscribed, not_subscribed_channels = await check_subscription(message.from_user.id)
        if not is_subscribed:
            keyboard = InlineKeyboardMarkup(row_width=1)
            for _, channel_username in not_subscribed_channels:
                keyboard.add(InlineKeyboardButton("➕ A'zo bo'lish", url=f"https://t.me/{channel_username[1:]}"))
            keyboard.add(InlineKeyboardButton("✅ Tekshirish", callback_data="check_subscription"))
            
            await message.answer(
                "Iltimos, botdan foydalanish uchun quyidagi kanallarga a'zo bo'ling:\n" +
                "\n".join([f"{ch[1]}" for ch in not_subscribed_channels]),
                reply_markup=keyboard
            )
            return
        return await handler(message, *args, **kwargs)
    return wrapper

# Inline query uchun subscription tekshiruvi
async def check_inline_subscription(inline_query: types.InlineQuery):
    is_subscribed, not_subscribed_channels = await check_subscription(inline_query.from_user.id)
    if not is_subscribed:
        keyboard = InlineKeyboardMarkup(row_width=1)
        for _, channel_username in not_subscribed_channels:
            keyboard.add(InlineKeyboardButton("➕ A'zo bo'lish", url=f"https://t.me/{channel_username[1:]}"))
        keyboard.add(InlineKeyboardButton("✅ Tekshirish", callback_data="check_subscription"))
        
        results = [
            InlineQueryResultArticle(
                id=str(uuid.uuid4()),
                title="Majburiy a'zolik talab qilinadi",
                input_message_content=InputTextMessageContent(
                    message_text=f"Iltimos, botdan foydalanish uchun quyidagi kanallarga a'zo bo'ling:\n" +
                                 "\n".join([f"{ch[1]}" for ch in not_subscribed_channels])
                ),
                reply_markup=keyboard
            )
        ]
        await inline_query.answer(results, cache_time=1)
        return False
    return True

@dp.message_handler(commands=["start"])
@subscription_required
async def start_command(message: types.Message, state: FSMContext):
    add_user(message.from_user.id, message.from_user.username, message.from_user.first_name)
    inline_kb = InlineKeyboardMarkup(row_width=1).add(
        InlineKeyboardButton("🔹️ Qidiruv berish 🔹️", switch_inline_query="")
    )
    await message.answer_photo(
        "https://i.imgur.com/lgx2V81.jpeg",
        caption=f"""
<b>Salom, {message.from_user.username}!</b> ⚪️ <i>@Anilebot</i> ga hush kelibsiz! 

🤖 <b>Ushbu bot nima qila oladi?</b>

Botimiz siz izlayotgan animeni tezda topishga yordam beradi. Bu bot <a href="https://t.me/Aniduble"> @Aniduble</a> kanaliga tegishli bo'lib, O'zbekistondagi eng katta anime bazasiga ega.

🤖 Menga shunchaki qidiruv bering va animelardan zavq oling!

👨‍💻 <b>Support:</b> <a href="https://t.me/AniDuble_admin">@AniDuble_admin</a>
""", parse_mode="HTML", reply_markup=inline_kb)
    await state.finish()  

# Inline qidiruv
@dp.inline_handler()
async def inline_query_handler(inline_query: types.InlineQuery):
    if not await check_inline_subscription(inline_query):
        return

    query = inline_query.query.strip()
    results = []

    if query:
        anime_results = search_anime_base(query)
        if anime_results:
            for a in anime_results:
                anime_id = a[0]
                series = get_anime_series_base(anime_id)
                a1 = 'ANIDUBLE_RASMIY_BOT'
                buttons = InlineKeyboardMarkup().add(
                    InlineKeyboardButton(
                        text="✨Tomosha qilish✨",
                        url=f"https://t.me/{a1}?start={series[0][1]}serie"
                    )
                )
                results.append(
                    InlineQueryResultArticle(
                        id=str(uuid.uuid4()),
                        title=f"✨ {a[3]}",
                        description=f"{a[4]} haqida batafsil ma'lumot",
                        thumb_url="https://i.imgur.com/lgx2V81.jpeg",
                        input_message_content=InputTextMessageContent(
                            message_text=(
                                f"✅️ *{a[3]}* topildi!\n"
                                "°───────────────────°\n"
                                f"🏷 *Anime nomi:* {a[3]}\n"
                                f"🎭 *Janr:* {a[5]}\n"
                                f"🔢 *Qismlar:* {a[8]}\n"
                                "🌐 *Tili:* 🇺🇿 O'zbekcha\n\n"
                                f"![Rasm]({ 'https://i.imgur.com/lgx2V81.jpeg' })"
                            ),
                            parse_mode="Markdown",
                        ),
                        reply_markup=buttons
                    )
                )
        else:
            results.append(
                InlineQueryResultArticle(
                    id=str(uuid.uuid4()),
                    title="No results found",
                    input_message_content=InputTextMessageContent(
                        message_text="Kechirasiz, siz so'ragan anime topilmadi."
                    )
                )
            )
    else:
        for i in range(20):
            a = get_random_anime_sql()
            anime_id = a[0][0]
            series = get_anime_series_base(anime_id)

            a1 = 'ANIDUBLE_RASMIY_BOT'
            buttons = InlineKeyboardMarkup().add(
                InlineKeyboardButton(
                    text="✨Tomosha qilish✨",
                    url=f"https://t.me/{a1}?start={series[0][1]}serie"
                )
            )
            results.append( 
                InlineQueryResultArticle(
                    id=str(uuid.uuid4()),
                    title=f"✨ {a[0][3]}",
                    description=f"{a[0][4]} haqida batafsil ma'lumot",
                    thumb_url="https://i.imgur.com/lgx2V81.jpeg",
                    input_message_content=InputTextMessageContent(
                        message_text=(
                            f"✅️ *{a[0][3]}* topildi!\n"
                            "°───────────────────°\n"
                            f"🏷 *Anime nomi:* {a[0][3]}\n"
                            f"🎭 *Janr:* {a[0][5]}\n"
                            f"🔢 *Qismlar:* {a[0][8]}\n"
                            "🌐 *Tili:* 🇺🇿 O'zbekcha\n\n"
                            f"![Rasm]({ 'https://i.imgur.com/lgx2V81.jpeg' })"
                        ),
                        parse_mode="Markdown",
                    ),
                    reply_markup=buttons
                )
            )
    await inline_query.answer(results, cache_time=1)

# A'zolik tekshirish tugmasi
@dp.callback_query_handler(text="check_subscription")
async def check_subscription_callback(callback: types.CallbackQuery):
    is_subscribed, not_subscribed_channels = await check_subscription(callback.from_user.id)
    if is_subscribed:
        await callback.message.delete()
        await start_command(callback.message)
    else:
        keyboard = InlineKeyboardMarkup(row_width=1)
        for _, channel_username in not_subscribed_channels:
            keyboard.add(InlineKeyboardButton("➕ A'zo bo'lish", url=f"https://t.me/{channel_username[1:]}"))
        keyboard.add(InlineKeyboardButton("✅ Tekshirish", callback_data="check_subscription"))
        
        await callback.message.edit_text(
            f"Iltimos, botdan foydalanish uchun quyidagi kanallarga a'zo bo'ling:\n" +
            "\n".join([f"{ch[1]}" for ch in not_subscribed_channels]),
            reply_markup=keyboard
        )

# Admin panel tugmalari
def get_admin_keyboard():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    keyboard.add(KeyboardButton("📢 Xabar yuborish"))
    keyboard.add(KeyboardButton("📌 Majburiy kanal qo'shish"))
    keyboard.add(KeyboardButton("🗑 Majburiy kanal o'chirish"))
    keyboard.add(KeyboardButton("🔙 Chiqish"))
    return keyboard

@dp.message_handler(commands=["admin"], user_id=ADMIN_IDS)
async def admin_panel(message: types.Message):
    await message.answer("Admin Panel:", reply_markup=get_admin_keyboard())

# Xabar yuborish
@dp.message_handler(lambda message: message.text == "📢 Xabar yuborish", user_id=ADMIN_IDS)
async def broadcast_start(message: types.Message):
    await message.answer("Hamma foydalanuvchilarga yuboriladigan xabarni kiriting:", reply_markup=ReplyKeyboardMarkup(resize_keyboard=True).add(KeyboardButton("🔙 Bekor qilish")))
    await BroadcastState.waiting_for_message.set()

@dp.message_handler(state=BroadcastState.waiting_for_message)
async def process_broadcast_message(message: types.Message, state: FSMContext):
    if message.text == "🔙 Bekor qilish":
        await message.answer("Xabar yuborish bekor qilindi.", reply_markup=get_admin_keyboard())
        await state.finish()
        return
    users = get_all_users()
    success_count = 0
    for user_id in users:
        try:
            await bot.send_message(user_id, message.text, parse_mode="Markdown")
            success_count += 1
            time.sleep(0.05)
        except Exception as e:
            logging.error(f"Failed to send message to {user_id}: {e}")
    await message.answer(f"Xabar {success_count} foydalanuvchiga yuborildi.", reply_markup=get_admin_keyboard())
    await state.finish()

# Majburiy kanal qo'shish
@dp.message_handler(lambda message: message.text == "📌 Majburiy kanal qo'shish", user_id=ADMIN_IDS)
async def add_channel_start(message: types.Message):
    await message.answer("Majburiy kanal username'sini kiriting (masalan, @Aniduble):", reply_markup=ReplyKeyboardMarkup(resize_keyboard=True).add(KeyboardButton("🔙 Bekor qilish")))
    await AddChannelState.waiting_for_channel.set()

@dp.message_handler(state=AddChannelState.waiting_for_channel)
async def process_channel(message: types.Message, state: FSMContext):
    if message.text == "🔙 Bekor qilish":
        await message.answer("Kanal qo'shish bekor qilindi.", reply_markup=get_admin_keyboard())
        await state.finish()
        return
    channel_username = message.text.strip()
    if not channel_username.startswith("@"):
        await message.answer("Iltimos, kanal username'sini @ bilan boshlang (masalan, @Aniduble).")
        return
    try:
        chat = await bot.get_chat(channel_username)
        add_mandatory_channel(chat.id, channel_username)
        await message.answer(f"{channel_username} majburiy kanal sifatida qo'shildi.", reply_markup=get_admin_keyboard())
    except Exception as e:
        await message.answer(f"Xatolik: {e}. Kanal username'sini tekshiring.")
    await state.finish()

# Majburiy kanal o'chirish
@dp.message_handler(lambda message: message.text == "🗑 Majburiy kanal o'chirish", user_id=ADMIN_IDS)
async def remove_channel_start(message: types.Message):
    channels = get_mandatory_channels()
    if not channels:
        await message.answer("Hozirda majburiy kanallar yo'q.", reply_markup=get_admin_keyboard())
        return
    response = "O'chirmoqchi bo'lgan kanalni tanlang (ID va username):\n"
    for channel_id, channel_username in channels:
        response += f"ID: {channel_id} | Username: {channel_username}\n"
    response += "\nKanal ID'sini yuboring:"
    await message.answer(response, reply_markup=ReplyKeyboardMarkup(resize_keyboard=True).add(KeyboardButton("🔙 Bekor qilish")))
    await RemoveChannelState.waiting_for_channel_id.set()

@dp.message_handler(state=RemoveChannelState.waiting_for_channel_id)
async def process_remove_channel(message: types.Message, state: FSMContext):
    if message.text == "🔙 Bekor qilish":
        await message.answer("Kanal o'chirish bekor qilindi.", reply_markup=get_admin_keyboard())
        await state.finish()
        return
    try:
        channel_id = int(message.text)
        channels = get_mandatory_channels()
        if any(ch[0] == channel_id for ch in channels):
            remove_mandatory_channel(channel_id)
            await message.answer("Kanal majburiy kanallar ro'yxatidan o'chirildi.", reply_markup=get_admin_keyboard())
        else:
            await message.answer("Bunday ID'li kanal topilmadi. Iltimos, ro'yxatni tekshiring.")
    except ValueError:
        await message.answer("Iltimos, faqat raqamli ID yuboring.")
    await state.finish()

# Admin paneldan chiqish
@dp.message_handler(lambda message: message.text == "🔙 Chiqish", user_id=ADMIN_IDS)
async def exit_admin_panel(message: types.Message):
    await message.answer("Admin paneldan chiqildi.", reply_markup=types.ReplyKeyboardRemove())

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)