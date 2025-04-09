import sqlite3
from difflib import SequenceMatcher
from datetime import datetime, timedelta
import random


conn = sqlite3.connect('database.db', timeout=10)
cursor = conn.cursor()

def creating_table():
    # Jadval yaratish va yangi ustunlar qo'shish
    conn.execute("""CREATE TABLE IF NOT EXISTS about_user(
        user_id INTEGER UNIQUE PRIMARY KEY NOT NULL,
        username TEXT,
        lang TEXT,
        gender TEXT,
        age TEXT,
        is_vip TEXT,
        is_lux TEXT,
        is_admin NUMERIC NOT NULL,
        is_staff NUMERIC NOT NULL
    )""")
    
    conn.execute("""CREATE TABLE IF NOT EXISTS anime(
        anime_id INTEGER PRIMARY KEY AUTOINCREMENT,
        lang TEXT,
        treller_id INTEGER,
        name TEXT,
        about TEXT,
        genre TEXT,
        teg TEXT,
        dub TEXT,
        series INTEGER,
        films INTEGER,
        is_vip NUMERIC,
        status TEXT,
        views INTEGER
    )""")
    
    conn.execute("""CREATE TABLE IF NOT EXISTS series(
        which_anime INTEGER NOT NULL,
        serie_id INTEGER,
        serie_num INTEGER NOT NULL,
        quality TEXT
    )""")
    
    conn.execute("""CREATE TABLE IF NOT EXISTS sponsor(
        channel_id INTEGER, 
        name TEXT,
        link TEXT
    )""")

    # 'statistics_new' jadvalini yaratish
    cursor.execute("""CREATE TABLE IF NOT EXISTS statistics_new (
        name TEXT UNIQUE, 
        bot_users INTEGER,
        anime_count INTEGER,
        vip_users INTEGER DEFAULT 0,
        lux_users INTEGER DEFAULT 0,
        anime_views INTEGER DEFAULT 0,
        series_count INTEGER DEFAULT 0,
        active_users INTEGER DEFAULT 0,
        new_users INTEGER DEFAULT 0,
        most_watched_anime TEXT DEFAULT 'None',
        most_active_user TEXT DEFAULT 'None'
    )""")
    conn.commit()

def get_all_statistics():
    cursor.execute("""SELECT * FROM statistics_new WHERE name = 'AniDuble'""")
    data = cursor.fetchall()

    # Agar ma'lumotlar mavjud bo'lsa, qaytarish
    print(data)
    if data:
        print(f"Ma'lumotlar mavjud: {data[0]}")
        return data[0]  # Birinchi qatorni qaytaradi
    else:
        print("Ma'lumotlar mavjud emas.")
        return None

def get_random_anime():
    cursor.execute("SELECT * FROM anime")
    all_animes = cursor.fetchall()
    
    if not all_animes:
        return "Hech qanday anime topilmadi."
    
    random_anime = random.choice(all_animes)
    return random_anime



def update_statistics_user_base():
    cursor.execute(f"""UPDATE statistics_new SET bot_users = bot_users + 1 WHERE name = 'AniDuble' """)
    conn.commit()

def update_most_watched_active():
    # Eng ko‘p tomosha qilingan anime
    cursor.execute("""
        SELECT name FROM anime 
        ORDER BY views DESC 
        LIMIT 1
    """)
    most_watched = cursor.fetchone()[0]

    # Eng faol foydalanuvchi (eng ko‘p botdan foydalangan)
    cursor.execute("""
        SELECT user_id FROM about_user 
        ORDER BY last_active DESC 
        LIMIT 1
    """)
    most_active = cursor.fetchone()[0]

    cursor.execute("""
        UPDATE statistics 
        SET most_watched_anime = ?, 
            most_active_user = ?
        WHERE name = 'AniDuble'
    """, (most_watched, most_active))
    conn.commit()

# Foydalanuvchi qo‘shilganda
def add_user_base(user_id, username, lang, gender=None, age=0, is_vip=0, is_lux=0, is_admin=False, is_staff=False):
    cursor.execute('INSERT INTO about_user (user_id, username, lang, gender, age, is_vip, is_lux, is_admin, is_staff, created_at, last_active) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP);', (user_id, username, lang, gender, age, is_vip, is_lux, is_admin, is_staff))
    conn.commit()
    update_total_users()
    update_vip_lux_users()
    update_active_new_users()

def update_total_users():
    cursor.execute("""
        UPDATE statistics_new 
        SET total_anime = (SELECT COUNT(*) FROM anime),
            bot_users = (SELECT COUNT(*) FROM about_user)
        WHERE name = 'AniDuble'
    """)
    conn.commit()


def update_vip_lux_users():
    cursor.execute("""
        UPDATE statistics_new 
        SET vip_users = (SELECT COUNT(*) FROM about_user WHERE is_vip != '0'),
            lux_users = (SELECT COUNT(*) FROM about_user WHERE is_lux != '0')
        WHERE name = 'AniDuble'
    """)
    conn.commit()

def update_total_anime_series():
    cursor.execute("""
        UPDATE statistics_new 
        SET total_anime = (SELECT COUNT(*) FROM anime),
            series_count = (SELECT COUNT(*) FROM series)
        WHERE name = 'AniDuble'
    """)
    conn.commit()


def update_anime_views(anime_id):
    cursor.execute(f"""UPDATE anime SET views = views + 1 WHERE anime_id = {anime_id}""")
    cursor.execute("""
        UPDATE statistics_new
        SET anime_views = (SELECT SUM(views) FROM anime)
        WHERE name = 'AniDuble'
    """)
    conn.commit()

def update_active_new_users():
    current_time = datetime.now()
    last_24h = current_time - timedelta(hours=24)
    last_7d = current_time - timedelta(days=7)

    cursor.execute("""
        UPDATE statistics_new 
        SET active_users = (SELECT COUNT(*) FROM about_user 
                           WHERE last_active > ?),
            new_users = (SELECT COUNT(*) FROM about_user 
                        WHERE created_at > ?)
        WHERE name = 'AniDuble'
    """, (last_24h, last_7d))
    conn.commit()

def add_extended_statistics():
    # AniDuble statistikasi mavjud bo'lmasa, uni qo'shish
    cursor.execute("""
        SELECT COUNT(*) FROM statistics_new WHERE name = 'AniDuble'
    """)
    count = cursor.fetchone()[0]

    if count == 0:  # Agar AniDuble statistikasi mavjud bo'lmasa
        cursor.execute("""
            INSERT INTO statistics_new (name, bot_users, anime_count, vip_users, lux_users, anime_views, series_count, active_users, new_users, most_watched_anime, most_active_user)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, ("AniDuble", 0, 0, 0, 0, 0, 0, 0, 0, "None", "None"))
        print("AniDuble statistikasi yaratildi.")
    else:
        print("AniDuble statistikasi allaqachon mavjud.")
    
    conn.commit()


def update_statistics_anime_base():
    cursor.execute(f"""UPDATE statistics_new SET anime_count = anime_count + 1 WHERE name = 'AniDuble' """)
    conn.commit()

def update_user_username_base(user_id,username):
    cursor.execute(f"""UPDATE about_user SET username = "{username}" WHERE user_id = {user_id} """)
    conn.commit()

def update_statistics_minus_anime_base():
    cursor.execute(f"""UPDATE statistics_new SET anime_count = anime_count - 1 WHERE name = 'AniDuble' """)
    conn.commit()

def get_statistic_base():
    cursor.execute(f"""SELECT * FROM statistics_new WHERE name = 'AniDuble' """)
    data = cursor.fetchall()
    conn.commit()
    return data    

def get_user_is_vip_base(user_id):
    cursor.execute(f"""SELECT is_vip FROM about_user WHERE user_id = {user_id} """)
    data = cursor.fetchall()
    conn.commit()

    return data

def get_user_is_lux_base(user_id):
    cursor.execute(f"""SELECT is_lux FROM about_user WHERE user_id = {user_id} """)
    data = cursor.fetchall()
    conn.commit()

    return data

def update_user_vip_over_base(time):
    cursor.execute(f"""SELECT user_id FROM about_user WHERE is_vip = "{time}" """)
    data = cursor.fetchall()
    conn.commit()
    for i in data:
        cursor.execute(f"""UPDATE about_user SET is_vip = 0 WHERE user_id = {i[0]} """)
        conn.commit()

    return data

def get_animes_base():
    cursor.execute(f"""SELECT anime_id,name,genre FROM anime""")
    data = cursor.fetchall()
    conn.commit()

    return data

def get_animes_ongoing_base():
    cursor.execute(f"""SELECT anime_id,name,genre FROM anime WHERE status = "loading" """)
    data = cursor.fetchall()
    conn.commit()

    return data

def update_user_vip_base(user_id,time):
    cursor.execute(f"""UPDATE about_user SET is_vip = "{time}" WHERE user_id = {user_id} """)
    conn.commit()

def update_user_lux_base(user_id,time):
    cursor.execute(f"""UPDATE about_user SET is_lux = "{time}" WHERE user_id = {user_id} """)
    conn.commit()

def update_user_free_base(user_id):
    cursor.execute(f"""UPDATE about_user SET is_vip = "0" WHERE user_id = {user_id} """)
    conn.commit()

def update_user_free_lux_base(user_id):
    cursor.execute(f"""UPDATE about_user SET is_lux = "0" WHERE user_id = {user_id} """)
    conn.commit()

def get_staff_base():
    cursor.execute(f"""SELECT user_id,username FROM about_user WHERE is_staff = 1""")
    data = cursor.fetchall()
    conn.commit()
    return data

def get_sponsor():
    cursor.execute(f"""SELECT * FROM sponsor""")
    data = cursor.fetchall()
    conn.commit()
    return data

def delete_sponsor(id):
    cursor.execute(f"""DELETE FROM sponsor WHERE channel_id = {id} """)
    conn.commit()

def update_sponsor(chat_id,link):
    cursor.execute(f"""UPDATE sponsor SET link = '{link}' WHERE channel_id = {chat_id} """)
    conn.commit()

def update_user_staff_base(user_id):
    cursor.execute(f"""UPDATE about_user SET is_staff = 1 WHERE user_id = {user_id} """)
    conn.commit()

def update_user_staff_delete_base(user_id):
    cursor.execute(f"""UPDATE about_user SET is_staff = 0 WHERE user_id = {user_id} """)
    conn.commit()

def get_user_is_admin_base(user_id):
    cursor.execute(f"""SELECT is_admin FROM about_user WHERE user_id = {user_id}""")
    data = cursor.fetchall()
    conn.commit()
    return data

def add_sponsor_base(channel_id,name , link):
    
    cursor.execute('INSERT INTO sponsor (channel_id , name , link) VALUES (? ,?, ?);', (channel_id , name , link))
    conn.commit()
    
def get_sponsor_base():
    cursor.execute(f"""SELECT * FROM sponsor""")
    data = cursor.fetchall()
    conn.commit()
    return data

def delete_sponsor_base(id):
    cursor.execute(f"""DELETE FROM sponsor WHERE channel_id = {id} """)
    conn.commit()

def get_last_serie_base(anime_id):
    cursor.execute(f"""SELECT serie_id FROM series WHERE which_anime = {anime_id} ORDER BY serie_num DESC """)
    data = cursor.fetchall()
    conn.commit()
    return data[0][0]

def get_id_to_num_serie_base(serie_id):
    cursor.execute(f"""SELECT serie_num FROM series WHERE serie_id = {serie_id} """)
    data = cursor.fetchall()
    conn.commit()
    return data[0][0]

def update_anime_informations_base(anime_id,key,text):
    cursor.execute(f"""UPDATE anime SET "{key}" = "{text}" WHERE anime_id = {anime_id} """)
    conn.commit()

def update_anime_serie_count_base(anime_id,key):
    cursor.execute(f"""UPDATE anime SET "{key}" = "{key}" + 1 WHERE anime_id = {anime_id} """)
    conn.commit()

def update_anime_serie_count_minus_base(anime_id):
    cursor.execute(f"""UPDATE anime SET series = series - 1 WHERE anime_id = {anime_id} """)
    conn.commit()

def update_anime_status_base(anime_id):
    cursor.execute(f"""UPDATE anime SET status = "finished" WHERE anime_id = {anime_id} """)
    conn.commit()

def add_serie_base(which_anime,serie_id,serie_num,quality):
    cursor.execute('INSERT INTO series (which_anime,serie_id,serie_num,quality) VALUES (?, ?, ?, ?);', (which_anime,serie_id,serie_num,quality))
    conn.commit()

def update_serie_base(old_serie,new_serie_id,quality):
    cursor.execute(f"""UPDATE series SET serie_id = {new_serie_id} , quality = "{quality}" WHERE serie_id = {old_serie} """)
    conn.commit()
   
def get_anime_base(anime_id):
    cursor.execute(f"""SELECT * FROM anime WHERE anime_id = {anime_id} """)
    data = cursor.fetchall()
    conn.commit()
    return data

def get_anime_about_base(anime_id):
    cursor.execute(f"""SELECT about FROM anime WHERE anime_id = {anime_id} """)
    data = cursor.fetchall()
    conn.commit()
    return data

def get_anime_series_base(anime_id):
    cursor.execute(f"""SELECT * FROM series WHERE which_anime = {anime_id} """)
    data = cursor.fetchall()
    conn.commit()
    return data

def delete_serie_base(serie_id):
    cursor.execute(f"""DELETE FROM series WHERE serie_id = {serie_id} """)
    conn.commit()

def delete_anime_base(anime_id):
    cursor.execute(f"""DELETE FROM anime WHERE anime_id = {anime_id} """)
    cursor.execute(f"""DELETE FROM series WHERE which_anime = {anime_id} """)
    conn.commit()

def get_series_base(anime_id):
    try:
        cursor.execute(f"""SELECT * FROM series WHERE which_anime = {anime_id}""")
        data = cursor.fetchall()
        conn.commit()
    except:
        data = []
    return data
    
def get_random_anime_sql():
    cursor.execute("SELECT * FROM anime ORDER BY RANDOM() LIMIT 1")
    result = cursor.fetchone()
    if result:
        return result
    else:
        return "Hech qanday anime topilmadi."
    
from difflib import SequenceMatcher

from difflib import SequenceMatcher

def search_anime_base(prompt):
    print("🔍 Kiritilgan prompt:", repr(prompt))

    query = "SELECT * FROM anime WHERE 1=1"
    parameters = []

    prompt = prompt.strip()
    is_int = prompt.isdigit()
    is_bool = prompt.lower() in ["true", "false"]
    is_lang = prompt.lower() in ["uz", "ru", "jp", "en"]
    is_status = prompt.lower() in ["ongoing", "completed", "paused"]

    print(f"📊 Turi aniqlandi: is_int={is_int}, is_bool={is_bool}, is_lang={is_lang}, is_status={is_status}")

    if is_int:
        query += " AND anime_id = ?"
        parameters.append(int(prompt))
    elif is_bool:
        query += " AND is_vip = ?"
        parameters.append(prompt.lower() == "true")
    elif is_lang:
        query += " AND lang = ?"
        parameters.append(prompt.lower())
    elif is_status:
        query += " AND status = ?"
        parameters.append(prompt.lower())
    else:
        query += " AND (name LIKE ? OR genre LIKE ?)"
        parameters.append(f"%{prompt}%")
        parameters.append(f"%{prompt}%")

    print("📝 SQL so‘rov:", query)
    print("📦 Parametrlar:", parameters)

    # SQL so‘rovni bajarish
    try:
        cursor.execute(query, parameters)
        results = cursor.fetchall()
        print(f"📥 SQL natija soni: {len(results)}")
    except Exception as e:
        print("❌ SQL xatolik:", e)
        return []

    # 🛠️ is_int va boshqalar bo‘lsa similarity kerak emas
    if is_int or is_bool or is_lang or is_status:
        print(f"✅ Yakuniy natijalar: {len(results)} ta topildi. (similarity yo‘q)")
        return results

    # 🔍 Similarity funksiyasi (faqat name/genre uchun)
    def similar(a, b):
        return SequenceMatcher(None, a.lower(), b.lower()).ratio()

    similar_anime = []

    for row in results:
        name_similarity = similar(prompt, row[3])  # row[3] = name
        if name_similarity >= 0.7:
            similar_anime.append(row)
            continue
        for tag in str(row[6]).split(","):  # row[6] = genre
            if similar(prompt, tag.strip()) >= 0.7:
                similar_anime.append(row)
                break

    print(f"✅ Yakuniy natijalar: {len(similar_anime)} ta topildi.")
    return similar_anime


# def search_anime_base(prompt):
#     cursor.execute(f"""SELECT * FROM anime """)
#     data = cursor.fetchall()
#     conn.commit()
    
#     def similar(a, b):
#         return SequenceMatcher(None, a, b).ratio()
    
#     similar_anime = []
    
#     for i in data:
#         similarity = similar(prompt,i[3])

#         if similarity < 0.7:
#             tegs = str(i[6]).split(",")
#             for a in tegs:
#                 similarity = similar(prompt,a)
            
#                 if similarity > 0.7:
#                     similar_anime.append(i)
#                     break
#         else:
#             similar_anime.append(i)
        
#     return similar_anime

def add_anime_base(lang,treller_id,name,about,genre,teg,dub,series = 0,films = 0,is_vip = 0,status = "loading",views = 0):
    cursor.execute('INSERT INTO anime (lang,treller_id,name,about,genre,teg,dub,series,films,is_vip,status,views) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);', (lang,treller_id,name,about,genre,teg,dub,series,films,is_vip,status,views))
    conn.commit()

def get_user_base(user_id):
    cursor.execute(f"""SELECT * FROM about_user WHERE user_id = {user_id}""")
    data = cursor.fetchall()
    conn.commit()
    return data

def get_user_by_username_base(username):
    cursor.execute(f"""SELECT * FROM about_user WHERE username = "{username}" """)
    data = cursor.fetchall()
    conn.commit()
    return data

def get_all_user_base():
    cursor.execute(f"""SELECT * FROM about_user""")
    data = cursor.fetchall()
    conn.commit()
    return data

def add_user_base(user_id,username,lang,gender = None,age = 0,is_vip = 0,is_lux = 0,is_admin = False,is_staff = False):
    cursor.execute('INSERT INTO about_user (user_id,username,lang,gender,age,is_vip,is_lux,is_admin,is_staff) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ? );', (user_id,username,lang,gender,age,is_vip,is_lux,is_admin,is_staff))
    conn.commit()

def update_user_lang_base(new_lang,user_id):
    cursor.execute(f"""UPDATE about_user SET lang = "{new_lang}" WHERE user_id = {user_id} """)
    conn.commit()

def update_anime_views_base(anime_id):
    cursor.execute(f"""UPDATE anime SET views = views + 1 WHERE anime_id = {anime_id} """)
    conn.commit()

# creating_table()
# add_statistics_base()

a = "321"
print(a.split("serie"))
