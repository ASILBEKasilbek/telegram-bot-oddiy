from aiogram import types
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

load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')

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
     buying_lux= State()

     search_by_photo = State()
     search_state= State()
     tasodifiy= State()

async def check_premium_func(user_id):
     user = get_user_base(user_id)  
     if user and len(user) > 0 and len(user[0]) > 5:
          vip = user[0][5]
     else:
          vip = "0"  
     is_vip = "True"
     if vip != "0":
          expire_time = datetime.strptime(vip, "%Y-%m-%d")
          now = datetime.now()
          if expire_time < now:
               is_vip = "False"
               update_user_vip_base(user_id,"0")
     if vip == 0 or vip == "0":
          is_vip = "False"
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
                    update_user_vip_base(user_id,"0")

               else:
                    is_vip = "True"
          
     return is_vip

@dp.message_handler(commands="start",state="*")
async def start(msg:types.Message ,state : FSMContext):

     if str(msg.chat.id)[0] == "-":
          pass
     else:
          user_id = msg.from_user.id
          user = get_user_base(user_id)
          if not user:
               
               username = msg.from_user.username
               
               if username != None:
                    user_name = f"@{msg.from_user.username}"
               else:
                    user_name = "None"
                    
               await User.language.set()
               
               async with state.proxy() as data:
                    data["username"] = user_name
                    
               text = """
Tilini tanlang :
"""
               await msg.answer(text=text,reply_markup=choose_language_clbtn())
          else:
               lang = user[0][2]

               is_vip = await check_premium_func(user_id)
               async with state.proxy() as data:
                    data["lang"] = lang
                    data["vip"] = is_vip

               try:
                    
                    try:
                         is_sub = await sponsor_cheking_func(msg,lang)

                         if is_sub == True:

                              start = msg.text.replace("/start ","")
                              serie_post_id = int(start.split("serie")[0])
                              str(start.split("serie")[1])
                              anime = get_anime_base(serie_post_id)

                              if anime:
                                   a = await msg.answer(anime_found_message(lang),reply_markup=back_button_btn())
                                   await a.delete()

                                   serie = get_series_base(serie_post_id)[-1]
                                   print(serie)
                                   serie_id = int(serie[1])
                                   serie_num = int(serie[2])
                                   serie_quality = serie[3]
                                   which_anime = int(serie[0])
                                   page = serie_num // 21

                                   next_states = True

                                   series = get_anime_series_base(which_anime)

                                   is_vip_anime = anime[0][10]

                                   if is_vip_anime == "vip":
                                        if is_vip_user == "True":
                                             next_states = True
                                        else:
                                             await state.finish()
                                             await User.menu.set()

                                             async with state.proxy() as data:
                                                  data["lang"] = lang
                                                  data["vip"] = is_vip

                                             await msg.answer("‼️Ushbu animeni tomosha qilish uchun ⚡️AniPass sotib olishingiz kerak !",reply_markup=user_button_btn(lang))
                                             next_states = False

                                   if is_vip_anime == "True":
                                        protect = True
                                   else:
                                        protect = False     
                                   
                                   if next_states == True:
                                        await User.watching.set()
                                        
                                        a = await dp.bot.forward_message(chat_id=user_id,message_id=serie_id,from_chat_id=anime_series_chat,protect_content=protect)

                                        async with state.proxy() as data:
                                             data["lang"] = lang
                                             data["serie"] = a.message_id

                                        await msg.answer(anime_serie_message(lang,serie_num,serie_quality),reply_markup=anime_series_clbtn(serie_num,series,page))
                              
                              elif serie_post_id:
                                   a = await msg.answer(anime_found_message(lang),reply_markup=back_button_btn())
                                   await a.delete()

                                   serie = get_series_base2(serie_post_id)
                                   serie_id = int(serie[0][1])
                                   serie_num = int(serie[0][2])
                                   serie_quality = serie[0][3]
                                   which_anime = int(serie[0][0])
                                   page = serie_num // 21
                                   next_states = True

                                   series = get_anime_series_base(which_anime)

                                   is_vip_anime = "False"
                                   if is_vip_anime == "vip":
                                        if is_vip_user == "True":
                                             next_states = True
                                        else:
                                             await state.finish()
                                             await User.menu.set()

                                             async with state.proxy() as data:
                                                  data["lang"] = lang
                                                  data["vip"] = is_vip

                                             await msg.answer("‼️Ushbu animeni tomosha qilish uchun ⚡️AniPass sotib olishingiz kerak !",reply_markup=user_button_btn(lang))
                                             next_states = False

                                   if is_vip_anime == "True":
                                        protect = True
                                   else:
                                        protect = False 
                                   
                                   if next_states == True:
                                        await User.watching.set()
                                        
                                        a = await dp.bot.forward_message(chat_id=user_id,message_id=serie_id,from_chat_id=anime_series_chat,protect_content=protect)

                                        async with state.proxy() as data:
                                             data["lang"] = lang
                                             data["serie"] = a.message_id

                                        await msg.answer(anime_serie_message(lang,serie_num,serie_quality),reply_markup=anime_series_clbtn(serie_num,series,page))

                              else:
                                   username = msg.from_user.username
               
                                   if username != None:
                                        user_name = f"@{msg.from_user.username}"
                                   else:
                                        user_name = "None"
                                   await state.finish()
                                   await User.menu.set()
                                   try:
                                        update_user_username_base(msg.from_user.id,username)
                                   except:
                                        pass
                                   async with state.proxy() as data:
                                        data["lang"] = lang
                                        
                                   await msg.answer("🔥",reply_markup=user_button_btn(lang))

                    
                    except:

                         content_id = msg.text.replace("/start ","")
                         
                         is_sub = await sponsor_cheking_func(msg,lang)

                         content_id = int(content_id)
                         if is_sub == True:
                              anime = get_anime_base(content_id)
                              if anime:
                                   await msg.answer(anime_found_message(lang))
                                             
                                   have_serie = False
                                   if anime[0][8] > 0:
                                        have_serie = True

                                   trailer_id = anime[0][2]
                                   anime_id = anime[0][0]
                                   is_vip = anime[0][10]

                                   await msg.delete()

                                   is_vip_user = await check_premium_func(user_id)

                                   trailer = await dp.bot.forward_message(message_id=trailer_id,chat_id=user_id,from_chat_id=anime_treller_chat)
                                   async with state.proxy() as data:
                                        data["trailer"] = trailer.message_id
                                        data["have_serie"] = have_serie
                                        data["lang"] = lang
                                        data["vip"] = is_vip_user

                                   await User.anime_menu.set()
                                   await msg.answer(anime_menu_message(lang,anime),reply_markup=anime_menu_clbtn(lang,anime_id,False,have_serie,is_vip))
                              else:
                                   username = msg.from_user.username
               
                                   if username != None:
                                        user_name = f"@{msg.from_user.username}"
                                   else:
                                        user_name = "None"
                                   await state.finish()
                                   await User.menu.set()
                                   try:
                                        update_user_username_base(msg.from_user.id,username)
                                   except:
                                        pass
                                   async with state.proxy() as data:
                                        data["lang"] = lang
                                        
                                   await msg.answer("🔥",reply_markup=user_button_btn(lang))
               except:
                    username = msg.from_user.username
               
                    if username != None:
                         user_name = f"@{msg.from_user.username}"
                    else:
                         user_name = "None"
                    await state.finish()
                    await User.menu.set()
                    try:
                         update_user_username_base(msg.from_user.id,username)
                    except:
                         pass
                    async with state.proxy() as data:
                         data["lang"] = lang
                         
                    await msg.answer("🔥",reply_markup=user_button_btn(lang,is_vip))

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

     if text == "📚Qo'llanma" or text == "📚Qo'llanma":
          await msg.answer(about_bot_message(lang,msg.from_user.id))

     elif text == "💸Reklama va Homiylik" or text == "💸Reklama va Homiylik":
          admin_user_name = get_user_base(6385061330)[0][1]
          await msg.answer(contacting_message(lang,admin_user_name))
     
     elif text == "🧧 Ongoing animelar" or text == "Ongoing animelar 🧧":
          animes = get_animes_ongoing_base()

          text = "<b>Ongoing animelar 🧧</b> \n°•───────────────────\n"

          num = 0
          
          for i in animes:
               num += 1
               bot='ANIDUBLE_RASMIY_BOT'
               text += f"<b>{num}.</b> [ <a href='https://t.me/{bot}?start={i[0]}'>{i[1]}</a> ]\n"

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
               await msg.answer(
                    "<b>🔍 Qidirish uchun anime nomi yoki ID sini yuboring!</b>",
                    reply_markup=back_user_button_btn(lang),
                    parse_mode="HTML"
               )

               await User.searching.set()
     
    
     elif is_vip =="True":

          if text == "🔍Anime Qidirish" or text == "🔍Запросить аниме":
               await msg.answer("<b>Qidiruv turini tanlang!</b>",reply_markup=search_clbtn(),parse_mode="HTML")
               await User.searching.set()

          elif text == "Animelar ro'yhati 📓" or text == "Animelar ro'yhati 📓":
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

               await msg.answer_document(document=document,caption="<b>📓AniDuble botidagi barcha animelar ro'yxati</b>")
               os.remove(f"animes_list_{msg.from_user.id}.txt")
               await msg.answer("AniDuble botidagi barcha animelar ro'yxati",reply_markup=user_button_btn(lang,is_vip))     

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
               print(is_vip)
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
     await call.message.answer("🔍Nomini topa olmayotgan animeingizni Rasmini yuboring",reply_markup=back_user_button_btn(lang))
     print(90)
     await User.search_by_photo.set()
     print(91)

@dp.callback_query_handler(text_contains = "search_id_name",state=User.searching)
async def start(call: types.CallbackQuery,state : FSMContext):
     lang = (await state.get_data()).get("lang")
     await call.message.delete()
     await call.message.answer("🔍Qidirish uchun anime nomi yoki ID sini yuboring !",reply_markup=back_user_button_btn(lang))
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
    await call.message.answer(
        "Iltimos, qidirish uchun anime janrini kiriting:" if lang == "uz" else
        "Пожалуйста, введите жанр аниме для поиска:"
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
        # Get all unique genres from the database
        cursor.execute("SELECT DISTINCT genre FROM anime")
        raw_genres = [genre[0].lower() for genre in cursor.fetchall() if genre[0]]
        
        # Split comma-separated genres into individual tags
        all_genres = []
        for genre in raw_genres:
            all_genres.extend([g.strip() for g in genre.split(",") if g.strip()])
        all_genres = list(set(all_genres))  # Remove duplicates
        logger.info(f"All genre tags: {all_genres}")

        # Find close matches for the user-input genre
        matched_genres = []
        if process and fuzz:
            matches = process.extract(user_genre, all_genres, scorer=fuzz.token_sort_ratio, limit=5)
            matched_genres = [match[0] for match in matches if match[1] >= 60]
            logger.info(f"Fuzzy matched genres: {matches}")
            # Add exact match if user_genre exists in all_genres
            if user_genre in all_genres:
                matched_genres.append(user_genre)
        else:
            # Fallback to exact match if fuzzywuzzy is not installed
            matched_genres = [user_genre] if user_genre in all_genres else []
            logger.warning("fuzzywuzzy not installed, using exact match")

        matched_genres = list(set(matched_genres))  # Remove duplicates
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
    "💫 <b>Aniduble botidan ⚡️ AniPass</b> sotib olganingizdan keyingi qulayliklar:\n"
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
     result = str(result)[:-9]  # So'nggi sekundlarni olib tashlash

     update_free_status(user_id,1)
     update_user_vip_base(user_id, result)


     text = (
    f"🎉 <b>{call.from_user.username}</b>!\n\n"
    "🎊 <b>Tabriklaymiz!</b> Siz <b>AniDuble</b> botidan tekinga <b>AniPass</b> aktivlashtirdingiz ✅️\n\n"
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

          text = """
<b>🔥AniDuble botida ⚡️AniPass obuna sotib olish uchun :</b>

1. <code>9860 1201 6396 3172</code>
   <b>( Umarbek Azimov )</b>

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
     if anime_id != "🔙Ortga":
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

          await call.message.answer("🔥",reply_markup=user_button_btn(lang,is_vip))



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