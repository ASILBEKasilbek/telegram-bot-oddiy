from config import REKLAMA,ADMIN,BOT_NAME
def user_button(lang):
    if lang == "uz":
        buttons = ["🔍Anime Qidirish","📚Qo'llanma","💸Reklama va Homiylik","⚡️AniPass","📓 Animelar ro'yhati","🧧 Ongoing animelar","🤝 Hamkorlik dasturi"]
    elif lang == "ru":
        buttons = []
        
    return buttons

def have_results_photo_message(lang):
    if lang == "uz":
        text = "<b>✅Rasm bo'yicha natijalar topildi</b>"
    elif lang == "ru":
        text = "<b>✅ Найдены результаты по картинке</b>"
    return text

def error_try_again_message(lang):
    if lang == "uz":
        text = "<b>❌Xatolik yuz berdi. Qayta urinib ko'ring !</b>"
    elif lang == "ru":
        text = "<b>❌ Произошла ошибка. Попробуйте еще раз !</b>"
    return text

def user_film_button(lang):
    if lang == "uz":
        buttons = ["🔍Kino Qidirish","💬Buyurtma berish","🔙Chiqish"]
    elif lang == "ru":
        buttons = []
        
    return buttons

def searching_anime_message(lang):
    if lang == "uz":
        text = "🔍Qidirish uchun anime nomini yuboring !"
    
    elif lang == "ru":
        text = " "
        
    return text

def searching_film_message(lang):
    if lang == "uz":
        text = "🔍Qidirish uchun film nomini yuboring !"
    
    elif lang == "ru":
        text = " "
        
    return text

def films_menu_message(lang):
    if lang == "uz":
        text = "<b>🖥Kino filmlar bo'limi</b>"
    
    elif lang == "ru":
        text = ""
        
    return text

def not_found_this_anime_message(lang,name):
    if lang == "uz":
        text = f"{name} Nomli anime topilmadi ! Qayta urinib ko'ring :"
    
    elif lang == "ru":
        text = f"Аниме по имени {name} не найдено! Попробуйте еще раз :"
        
    return text

def not_found_this_film_message(lang,name):
    if lang == "uz":
        text = f"{name} Nomli Film topilmadi ! Qayta urinib ko'ring :"
    
    elif lang == "ru":
        text = f"Аниме по имени {name} не найдено! Попробуйте еще раз :"
        
    return text

def you_should_subscribe_message(lang):
    if lang == "uz":
        text = "💭<b>Avval homiy</b> kanallarimizga to'liq <b>obuna bo'ling 👇</b>"
    elif lang == "ru":
        text = "💭<b>Сначала полностью</b> подпишитесь на <b>наши спонсорские</b> каналы 👇"
    return text

def select_function_message(lang):
    if lang == "uz":
        text = "🔍Kerakligini tanlang :"
    
    elif lang == "ru":
        text = "🔍Выберите подходящий :"
        
    return text

def anime_found_message(lang):
    if lang == "uz":
        text = "✅<b>Anime topildi</b>"
    
    elif lang == "ru":
        text = ""
        
    return text

def film_found_message(lang):
    if lang == "uz":
        text = "✅<b>Film topildi</b>"
    
    elif lang == "ru":
        text = ""
        
    return text

def you_watch_this_now_message(lang):
    if lang == "uz":
        text = "💿Siz hozir shu qismni tomosha qilyapiz !"
    
    elif lang == "ru":
        text = ""
        
    return text

def about_bot_message(lang,user_id):
    if lang == "uz":
        text = f"""
<b>⋆⭒˚｡⋆༶ Botini ishlatish bo'yicha qo'llanma ⋆༶｡˚⭒⋆</b>
<b>
🔍 Anime Qidirish  </b>
Botda mavjud bo'lgan animelarni qidirish uchun ishlatiladi.
<b>💸 Reklama va Homiylik  </b>
Bot adminlari bilan reklama yoki homiylik yuzasidan aloqaga chiqish.
<b>🧧 Ongoing animelar  </b>
Yangi chiqayotgan animelar ro'yhati.
<b>
⚡️ AniPass  </b>
AniPass foydalanuvchilari uchun maxsus imkoniyatlar:  
  ▪ Janrlar orqali qidirish  
  ▪ Rasm orqali qidirish  
  ▪ So'nggi yuklanganlar va eng ko'p ko'rilganlar  
  ▪ Bot 2x tez ishlash imkoniyati  
  ▪ Majburiy obuna talab qilmaydi  
  ▪ Anime tavsiya funksiyasi

🧑‍💻<b>Admin</b> - {ADMIN}
👨‍🔧<b>Dasturchi </b>: @dasturch1_asilbek

<b>🆔Botdagi ID ingiz :</b> <code>{user_id}</code>
"""
    
    elif lang == "ru":
        text = ""
        
    return text

def anime_serie_message(lang,serie_num,quality):
    if lang == "uz":
        text = f"""
------------------------
🎞Qism : {serie_num}
✨Sifati :{quality}
------------------------
"""
    elif lang == "ru":
        text = f""
        
    return text

def anime_menu_message(lang,anime_data):

    anime_lang = anime_data[0][1]
    anime_name = anime_data[0][3]
    anime_genre = anime_data[0][5]
    anime_dub = anime_data[0][7]
    anime_serie = anime_data[0][8]
    anime_film = anime_data[0][9]
    anime_status = anime_data[0][11]
    anime_views = anime_data[0][12]

    if lang == "uz":

        if anime_status == "loading":
            status = "🟡Davom etmoqda"
        elif anime_status == "finished":
            status = "🟢Tugallangan"
            
        if anime_lang == "uz":
            lang = "🇺🇿Ozbekcha"
        
        elif anime_lang == "ru":
            lang = "🇷🇺Ruscha"

        text = f"""
🏷<b>Nomi : </b>{anime_name}
-----------------------------------------------------
📑<b>Janri : </b>{anime_genre.replace(","," , ")}
🎙<b>Ovoz beruvchi :</b> {anime_dub}
-----------------------------------------------------
🎞<b>Seriyalar soni :</b> {anime_serie}
🎥<b>Filmlar soni :</b> {anime_film}
-----------------------------------------------------
💬<b>Tili : </b>{lang}
-----------------------------------------------------
📉<b>Status :</b> {status}
👁‍🗨<b>Ko'rishlar :</b> {anime_views}
"""
        
    elif lang == "ru":

        if anime_status == "loading":
            status = "🟡В ​​процессе"
        elif anime_status == "finished":
            status = "🟢Завершено"
            
        if anime_lang == "uz":
            lang = "🇺🇿Узбекский"
        
        elif anime_lang == "ru":
            lang = "🇷🇺Русский"

        text = f"""
🏷<b>Имя: </b>{anime_name}
📑<b>Жанр: </b>{anime_genre}
🎙<b>Голос:</b> {anime_dub}
--------------------
🎞<b>Количество серий:</b> {anime_serie}
🎥<b>Количество фильмов:</b> {anime_film}
--------------------
💬<b>Язык: </b>{lang}
--------------------
📉<b>Статус:</b> {status}
👁‍🗨<b>Просмотры:</b> {anime_views}"""
        
    return text

def film_menu_message(lang,film_data):

    film_lang = film_data[0][1]
    film_name = film_data[0][3]
    film_genre = film_data[0][5]
    film_dub = film_data[0][7]
    film_serie = film_data[0][8]
    film_status = film_data[0][9]
    film_views = film_data[0][10]

    if lang == "uz":

        if film_status == "loading":
            status = "🟡Davom etmoqda"
        elif film_status == "finished":
            status = "🟢Tugallangan"
            
        if film_lang == "uz":
            lang = "🇺🇿Ozbekcha"
        
        elif film_lang == "ru":
            lang = "🇷🇺Ruscha"

        text = f"""
🏷<b>Nomi : </b>{film_name}
-----------------------------------------------------
📑<b>Janri : </b>{film_genre.replace(","," , ")}
🎙<b>Ovoz beruvchi :</b> {film_dub}
-----------------------------------------------------
🎞<b>Seriyalar soni :</b> {film_serie}
-----------------------------------------------------
💬<b>Tili : </b>{lang}
-----------------------------------------------------
📉<b>Status :</b> {status}
👁‍🗨<b>Ko'rishlar :</b> {film_views}
"""
        
    elif lang == "ru":

        if film_status == "loading":
            status = "🟡В ​​процессе"
        elif film_status == "finished":
            status = "🟢Завершено"
            
        if film_lang == "uz":
            lang = "🇺🇿Узбекский"
        
        elif film_lang == "ru":
            lang = "🇷🇺Русский"

        text = f"""
🏷<b>Имя: </b>{film_name}
📑<b>Жанр: </b>{film_genre}
🎙<b>Голос:</b> {film_dub}
--------------------
🎞<b>Количество серий:</b> {film_serie}
--------------------
💬<b>Язык: </b>{lang}
--------------------
📉<b>Статус:</b> {status}
👁‍🗨<b>Просмотры:</b> {film_views}"""
        
    return text

def send_your_age_message(lang):
    if lang == "uz":
        text = "Yoshingizni nechchida ekanini yozib yuboring :"
    
    elif lang == "ru":
        text = "Напишите свой возраст :"
        
    return text

def start_message(lang):
    if lang == "uz":
        text = f"👋<b>{BOT_NAME}</b> botiga xush kelibsiz"
    
    elif lang == "ru":
        text = "👋Добро пожаловать в бот <b>AniDUble</b>"

    return text

def main_menu_message(lang):
    if lang == "uz":
        text = "🎛<b>Asosiy menu</b>"
    
    elif lang == "ru":
        text = ""

    return text

def contacting_message(lang,username):
    if lang == "uz":
        text = f"""
<i>Salom siz Reklama bo'limidasiz  🌸

Reklamalar bu ushbu bot uchun va asosiy kanalimiz uchun bo'ladi 📌

Yani sizni kanalingiz bo'lsa uni aktivini ko'tarishning eng yaxshi yo'li 📊 

Batafsil: {REKLAMA}</i>
"""
    
    elif lang == "ru":
        text = f"""
<i>Salom siz Reklama bo'limidasiz  🌸

Reklamalar bu ushbu bot uchun va asosiy kanalimiz uchun bo'ladi 📌

Yani sizni kanalingiz bo'lsa uni aktivini ko'tarishning eng yaxshi yo'li 📊 

Batafsil: {REKLAMA}</i>
"""

    return text