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

     buying_vip = State()
     buying_lux= State()

     search_by_photo = State()
     search_state= State()
     tasodifiy= State()

async def check_premium_func(user_id):
     user = get_user_base(user_id)  # Assuming this function fetches the user data
     print(user)  # Print the user data for debugging purposes
     
     # Ensure 'user' is not empty and contains at least one item
     if user and len(user) > 0 and len(user[0]) > 5:
          # Access the 6th element if the list is long enough
          vip = user[0][5]
     else:
          # Handle the case where the list is shorter than expected or data is missing
          vip = "0"  # Or some other default value

     # lux = user[0][6]

     is_vip = "True"
     # is_lux = "True"
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
          
          # if is_lux == "True":
          #      is_lux_user = datetime.strptime(lux, "%Y-%m-%d")

          #      if today2 >= is_lux_user:

          #           update_user_free_lux_base(user_id)

          #           try:
          #                await dp.bot.kick_chat_member(chat_id=-1002131546047,user_id=user_id)
          #           except:
          #                pass

          #           text = "<b>‼️Sizdagi 💎Lux obuna muddati o'z nihoyasiga yetdi !</b>"
          #           try:
          #                a = await dp.bot.send_message(chat_id=user_id,text=text)
          #                await a.pin()
          #           except:
          #                pass

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
     # if send_expiration_message(user_id) == True:
     #      is_vip = "True"
     # else:
     #      is_vip = "False"
     # if is_vip == "True":
     #      is_sub = True
     # else:
     #      is_sub = await sponsor_cheking_func(msg,lang)

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

          if text == "Tasodifiy anime":
               await msg.answer("Tasodifiy anime tugmasini bosing")
               await User.tasodifiy.set()

          elif text == "⚡️AniPass" or text == "⚡️AniPass":
               is_vip = get_user_is_vip_base(user_id)
               is_lux = get_user_is_lux_base(user_id)

               if is_vip[0][0] != "0" and is_lux[0][0] != "0":

                    text = f"""
<b>Sizdagi ⚡️AniPass obunani tugash vaqti :</b> {is_vip[0][0]}

"""
                    
# <b>Sizdagi 💎Lux kanaldagi obunangizni tugash vaqti :</b> {is_lux[0][0]}
                    await msg.answer(text,reply_markup=user_button_btn(lang))

               elif is_vip[0][0] != "0" and is_lux[0][0] == "0":

                    text = f"""
<b>Sizdagi ⚡️AniPass tugash vaqti :</b> {is_vip[0][0]}
-
🔥 <b>AniDuble botidan 💎 Lux Kanalga ulanish uchun ma'lumotlar :<i>
°•───────────────────
Endilikda Echchi va Hentai animelarni o'zbek tilida Lux Kanalimizda ko'rishingiz mumkun 
°•───────────────────
Lux kanalga Echchi va hentai animelar o'zbek tilida joylab boriladi 💎
°•───────────────────
💎Lux Kanal uchun  obuna sotib olish narxlarni menu dan tanlashingiz mumkin</i></b>
"""                 
                    await msg.answer_animation(animation=open("media/vip_channel.mp4","rb"),caption=text,reply_markup=vip_channel_clbtn())
                    
#                elif is_vip[0][0] == "0" and is_lux[0][0] != "0":

#                     text = f"""
# <b>Sizdagi 💎Lux kanaldagi obunangizni tugash vaqti :</b> {is_lux[0][0]}
# -
# 💫 Aniduble botidan ⚡️ AniPass sotib olganingizdan keyingi qulayliklar
# °•───────────────────
# 🎉 Qulayliklar 

# 🔹️ Botni 2x tezlikda ishlatish 
# 🔹️ Botdan mukkammal va erkin foydalana olish 
# 🔹️ Eski seriyalar o'chmaydi 
# 🔹️ Homiy kanallarga a'zo bo'lish shart 
# emas .
# 🔹️ Botdan sizga qoshimcha reklamalar kelmaydi va bezovta qilmaydi .
# °•───────────────────
# 🎟  Qo'shiladigan tugmalar 

# 🔹️ Rasm orqali qidiruv
# 🔹️ Tasodifiy anime 
# 🔹️ Eng ko'p ko'rilgan animelar 
# 🔹️ Janr orqali qidiruv 

# ⚠️ Eslatma : ⚡️AniPass faqat bot uchun amal qiladi 
# ⚡️ AniPass narxi atiga : 5.000 so'm 💵
# """
#                     print(text)
#                     await msg.answer_animation(animation=open("media/vip.mp4","rb"),caption=text,reply_markup=vip_buying_clbtn())

               else:

                    text = f"""
<b>🔥Qaysi turdagi obunani sotib olishni istaysiz ?</b>
"""
                    await msg.answer(text,reply_markup=which_vip_clbtn())
         
          elif text == "🔍Anime Qidirish":
               await msg.answer(
                    "<b>🔍 Qidirish uchun anime nomi yoki ID sini yuboring!</b>",
                    reply_markup=back_button_btn(),
                    parse_mode="HTML"
               )

               await User.searching.set()
     
    
     elif is_vip =="True":

          # if text == "🏙Rasm orqali qidiruv" or text == "🏙Rasm orqali qidiruv":
          #      await User.search_by_photo.set()
          #      text = "<b>🔍Nomini topa olmayotgan animeingizni Rasmini yuboring</b>"
          #      await msg.answer(text,reply_markup=back_user_button_btn(lang))
          
          if text == "🔍Anime Qidirish" or text == "🔍Запросить аниме":
               await msg.answer("<b>Qidiruv turini tanlang!</b>",reply_markup=search_clbtn(),parse_mode="HTML")
               await User.searching.set()
               # await msg.answer("Qaytish uchun /start ni bosing")

          elif text == "Tasodifiy anime":
               await msg.answer("<b>Tasodifiy anime tugmasini bosing<b>",parse_mode="HTML")
               await User.tasodifiy.set()
               
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

                    # Formatni avtomatik aniqlash
                    try:
                         # Avval to‘liq datetime format bo‘lishi mumkinligini tekshir
                         expiry_date = datetime.strptime(expiry_date_str, "%Y-%m-%d %H:%M:%S")
                    except ValueError:
                         # Faqat sana bo‘lsa, vaqtni 00:00:00 deb qo‘sh
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
                         # send_expiration_message(user_id)
                         message = (
                              f"<b>Sizdagi ⚡️AniPass muddati tugagan!</b>\n"
                         )
               else:
                    message = "<b>Sizda ⚡️AniPass mavjud emas yoki muddati aniqlanmadi.</b>"

               await msg.answer(message, reply_markup=user_button_btn(lang, is_vip))

#                if is_vip[0][0] != "0" and is_lux[0][0] != "0":

#                     text = f"""
# <b>Sizdagi ⚡️AniPass obunani tugash vaqti :</b> {is_vip[0][0]}
# """
                    
# # <b>Sizdagi 💎Lux kanaldagi obunangizni tugash vaqti :</b> {is_lux[0][0]}
#                     await msg.answer(text,reply_markup=user_button_btn(lang))

#                elif is_vip[0][0] != "0" and is_lux[0][0] == "0":

#                     text = f"""
# <b>Sizdagi ⚡️AniPass tugash vaqti :</b> {is_vip[0][0]}
# -
# 🔥 <b>AniDuble botidan 💎 Lux Kanalga ulanish uchun ma'lumotlar :<i>
# °•───────────────────
# Endilikda Echchi va Hentai animelarni o'zbek tilida Lux Kanalimizda ko'rishingiz mumkun 
# °•───────────────────
# Lux kanalga Echchi va hentai animelar o'zbek tilida joylab boriladi 💎
# °•───────────────────
# 💎Lux Kanal uchun  obuna sotib olish narxlarni menu dan tanlashingiz mumkin</i></b>
# """                 
#                     await msg.answer_animation(animation=open("media/vip_channel.mp4","rb"),caption=text,reply_markup=vip_channel_clbtn())
                    
#                elif is_vip[0][0] == "0" and is_lux[0][0] != "0":

#                     text = f"""
# <b>Sizdagi 💎Lux kanaldagi obunangizni tugash vaqti :</b> {is_lux[0][0]}
# -
# 🔥<b>💫 Aniduble botidan ⚡️ AniPass sotib olganingizdan keyingi qulayliklar
# °•───────────────────
# 🎉Qulayliklar 
# ⚡️ Botni 2x tezlikda ishlatish 
# 💣 Botdan mukkammal va erkin foydalana olish 
# 📺 Eski seriyalar o'chmaydi 
# 📡 Homiy kanallarga a'zo bo'lish shart 
# emas .
# 🧨 Botdan sizga qoshimcha reklamalar kelmaydi va bezovta qilmaydi .
# °•───────────────────
# 🎟 Qoshiladigan tugmalar 
# 🖼 Rasm orqali qidiruv
# 🔃 Tasodifiy anime 
# 🔸️ Eng ko'p ko'rilgan animelar 
# 🏮 Janr orqali qidiruv 
# ⚠️ Eslatma : ⚡️AniPass  faqat bot uchun amal qiladi 
# ⚡️ AniPass narxi atiga : 5.000 so'm 💵</b>
# """                     
#                     print(text)
#                     await msg.answer_animation(animation=open("media/vip.mp4","rb"),caption=text,reply_markup=vip_buying_clbtn())

               # else:

#                     text = f"""
# <b>🔥Qaysi turdagi obunani sotib olishni istaysiz ?</b>
# """
#                     await msg.answer(text,reply_markup=which_vip_clbtn())

          elif len(text) > 5:
               anime = search_anime_base(text)
               user_id = msg.from_user.id
               
               if anime:
                    await msg.answer(anime_found_message(lang))
                         
                    have_serie = False
                    if anime[0][8] > 0:
                         have_serie = True

                    trailer_id = anime[0][2]
                    anime_id = anime[0][0]
                    is_vip = anime[0][10]

                    trailer = await dp.bot.forward_message(message_id=trailer_id,chat_id=user_id,from_chat_id=anime_treller_chat)
                    async with state.proxy() as data:
                         data["trailer"] = trailer.message_id
                         data["have_serie"] = have_serie
                    await User.anime_menu.set()
                    await msg.answer(anime_menu_message(lang,anime),reply_markup=anime_menu_clbtn(lang,anime_id,False,have_serie,is_vip))

          vip = data.get("vip")

          if not vip:
               async with state.proxy() as data:
                    data["lang"] = lang
                    data["vip"] = is_vip

@dp.callback_query_handler(text_contains = "search_rasm",state=User.searching)
async def start(call: types.CallbackQuery,state : FSMContext):
     lang = (await state.get_data()).get("lang")
     # is_vip_user = (await state.get_data()).get("vip")
     
     await call.message.delete()
     await call.message.answer("🔍Nomini topa olmayotgan animeingizni Rasmini yuboring",reply_markup=back_user_button_btn(lang))
     await User.search_by_photo.set()
     await call.answer("Qaytish uchun /start ni bosing")

@dp.callback_query_handler(text_contains = "search_id_name",state=User.searching)
async def start(call: types.CallbackQuery,state : FSMContext):
     lang = (await state.get_data()).get("lang")
     # is_vip_user = (await state.get_data()).get("vip")

     await call.message.delete()
     await call.message.answer("🔍Qidirish uchun anime nomi yoki ID sini yuboring !",reply_markup=back_user_button_btn(lang))
     await User.searching.set()
     await call.answer("Qaytish uchun /start ni bosing")

@dp.message_handler(state=[User.tasodifiy, User.anime_menu, User.watching])
async def start(call: types.Message, state: FSMContext):
    # FSMContext yordamida holat ma'lumotlarini olish
     data = await state.get_data()
     lang = data.get("lang")
     is_vip_user = data.get("vip")
     anime=[]

     user_id = call.from_user.id
     anime.append(get_random_anime())
     await call.delete()
               
     have_serie = False
     if anime[0][9] > 0:
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
     await call.answer(anime_menu_message(lang,anime),reply_markup=anime_menu_clbtn(lang,anime_id,False,have_serie,is_vip_user))
     await call.answer("Qaytish uchun /start ni bosing")

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

        # Rasmni o‘qiymiz
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

# async def send_expiration_message(user_id):
#     is_vip = get_user_is_vip_base(user_id)  # Masalan: [('2025-04-11 12:10:00',)]

#     if is_vip[0][0] == "0":
#         # Allaqachon tugagan bo‘lsa
#         text = "⚠️ AniPass muddati tugadi! Obunani davom ettirish uchun qayta to'lov qiling."
#         await dp.bot.send_message(user_id, text)
#         return

#     expire_time = datetime.strptime(is_vip[0][0], "%Y-%m-%d %H:%M:%S")
#     now = datetime.now()

#     if now < expire_time:
#         return "True"
#     else:
#         # Vaqti tugagan
#         text = "⚠️ AniPass muddati tugadi! Obunani davom ettirish uchun qayta to'lov qiling."
#         update_user_vip_base(user_id, '0')
#         User.menu.state()
#         await dp.bot.send_message(user_id, text)


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

     if anime_id != "back":
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

          await call.message.answer("🔥",reply_markup=user_button_btn(lang))



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
               
                    trailer = int(data.get("trailer"))
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