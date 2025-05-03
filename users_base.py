import sqlite3
from difflib import SequenceMatcher
from datetime import datetime, timedelta
import random
import os 

BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # users_base.py joylashgan joy
db_path = os.path.join(BASE_DIR, 'database.db')

conn = sqlite3.connect(db_path, timeout=10)
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
        is_staff NUMERIC NOT NULL,
        free NUMERIC DEFAULT 0
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
    
    conn.execute("""CREATE TABLE IF NOT EXISTS statistics_new2(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            total_users INTEGER DEFAULT 0,
            active_users INTEGER DEFAULT 0,
            new_users_today INTEGER DEFAULT 0,
            total_vip_users INTEGER DEFAULT 0,
            blocked_users INTEGER DEFAULT 0,
            total_free_users INTEGER DEFAULT 0,
            total_anipass_users INTEGER DEFAULT 0,
            total_anime INTEGER DEFAULT 0,
            total_series INTEGER DEFAULT 0,
            total_views INTEGER DEFAULT 0,
            anime_views INTEGER DEFAULT 0,
            series_views INTEGER DEFAULT 0,
            sponsors_count INTEGER DEFAULT 0,
            top_anime_id INTEGER,
            updated_at TEXT
    )""")
    
    conn.execute("""CREATE TABLE IF NOT EXISTS channels (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        link TEXT NOT NULL UNIQUE,
        added_by INTEGER,
        date_added TEXT
    )
    """)
        # Eski FTS jadvalini o'chiramiz (agar mavjud bo'lsa)
    conn.execute("DROP TABLE IF EXISTS anime_fts")

    # Yangi FTS jadvalini yaratamiz
    conn.execute("""
    CREATE VIRTUAL TABLE anime_fts USING fts5(
        name, 
        genre,
        teg,
        content='anime', 
        content_rowid='anime_id'
    );
    """)

    # Triggerlar: FTS jadvalini anime jadvali bilan sinxronlashtirish
    conn.executescript("""
    CREATE TRIGGER IF NOT EXISTS anime_ai AFTER INSERT ON anime BEGIN
        INSERT INTO anime_fts(rowid, name, genre, teg)
        VALUES (new.anime_id, new.name, new.genre, new.teg);
    END;

    CREATE TRIGGER IF NOT EXISTS anime_ad AFTER DELETE ON anime BEGIN
        INSERT INTO anime_fts(anime_fts, rowid, name, genre, teg)
        VALUES('delete', old.anime_id, old.name, old.genre, old.teg);
    END;

    CREATE TRIGGER IF NOT EXISTS anime_au AFTER UPDATE ON anime BEGIN
        INSERT INTO anime_fts(anime_fts, rowid, name, genre, teg)
        VALUES('delete', old.anime_id, old.name, old.genre, old.teg);
        
        INSERT INTO anime_fts(rowid, name, genre, teg)
        VALUES (new.anime_id, new.name, new.genre, new.teg);
    END;
    """)

    # Mavjud anime jadvalidan ma'lumotlarni FTS jadvaliga ko'chirish
    conn.execute("""
    INSERT INTO anime_fts(rowid, name, genre, teg)
    SELECT anime_id, name, genre, teg FROM anime;
    """)


    conn.commit()
    
def user_exists(user_id):
    cursor.execute("SELECT 1 FROM about_user WHERE user_id = ?", (user_id,))
    return cursor.fetchone() is not None

def update_statistics():
    today = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # total users
    cursor.execute("SELECT COUNT(*) FROM about_user")
    total_users = cursor.fetchone()[0]

    # active users (misol uchun: so‘nggi 24 soat ichida free > 0 bo‘lganlar)
    cursor.execute("SELECT COUNT(*) FROM about_user WHERE free > 0")
    active_users = cursor.fetchone()[0]

    # new users today (user_id raqamidan kelib chiqib bugun qo‘shilganlarni aniqlash uchun, real loyihada date ustuni bo‘lishi kerak edi)
    # Hozircha misol sifatida so‘nggi 24 soat ichida free > 0 bo‘ganlarni olamiz
    cursor.execute("SELECT COUNT(*) FROM about_user WHERE free > 0")
    new_users_today = cursor.fetchone()[0]

    # total vip users
    cursor.execute("SELECT COUNT(*) FROM about_user WHERE is_vip != 0")
    total_vip_users = cursor.fetchone()[0]


    # blocked users
    cursor.execute("SELECT COUNT(*) FROM about_user WHERE is_blocked = 1")
    blocked_users = cursor.fetchone()[0]

    # total free users
    cursor.execute("SELECT COUNT(*) FROM about_user WHERE free > 0")
    total_free_users = cursor.fetchone()[0]

    # total anipass users
    cursor.execute("SELECT COUNT(*) FROM about_user WHERE is_vip != 0")
    total_anipass_users = cursor.fetchone()[0]

    # total anime
    cursor.execute("SELECT COUNT(*) FROM anime")
    total_anime = cursor.fetchone()[0]

    # total series
    cursor.execute("SELECT COUNT(*) FROM series")
    total_series = cursor.fetchone()[0]

    # total views
    cursor.execute("SELECT SUM(views) FROM anime")
    total_views = cursor.fetchone()[0] or 0

    # anime views (bir xil total_views bo‘ladi hozir)
    anime_views = total_views

    # series views (hozircha track qilinmagan, 0 qilamiz)
    series_views = 0

    # sponsors count
    cursor.execute("SELECT COUNT(*) FROM sponsor")
    sponsors_count = cursor.fetchone()[0]

    # top anime (eng ko‘p ko‘rilgan anime)
    cursor.execute("SELECT anime_id FROM anime ORDER BY views DESC LIMIT 1")
    result = cursor.fetchone()
    top_anime_id = result[0] if result else None

    # yozish
    cursor.execute("""
        INSERT INTO statistics_new2 (
            date, total_users, active_users, new_users_today, total_vip_users, blocked_users, 
            total_free_users, total_anipass_users, total_anime, total_series, total_views, 
            anime_views, series_views, sponsors_count, top_anime_id, updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        today, total_users, active_users, new_users_today, total_vip_users, blocked_users,
        total_free_users, total_anipass_users, total_anime, total_series, total_views,
        anime_views, series_views, sponsors_count, top_anime_id, today
    ))


    conn.commit()
    print("✅ Statistika yangilandi!")

def get_all_statistics():
    # Eng so'nggi statistik ma'lumotlarni olish
    cursor.execute("SELECT total_users, total_vip_users, total_free_users, total_anime, total_views, total_series, active_users, new_users_today, top_anime_id, updated_at FROM statistics_new2 ORDER BY id DESC LIMIT 1")
    latest_stats = cursor.fetchone()

    if latest_stats:
        total_users, total_vip_users, total_free_users, total_anime, total_views, total_series, active_users, new_users_today, top_anime_id, updated_at = latest_stats

        # Top anime nomini olish (agar mavjud bo'lsa)
        if top_anime_id:
            cursor.execute("SELECT name FROM anime WHERE anime_id = ?", (top_anime_id,))
            result = cursor.fetchone()  # Natijani saqlash
            most_watched_anime = result[0] if result else "Noma'lum"
        else:
            most_watched_anime = "Ma'lumot yo'q"

        return (total_users, total_vip_users, total_free_users, total_anime, total_views, total_series, active_users, new_users_today, most_watched_anime, None)  # eng faol foydalanuvchi hali yo'q

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

def add_channels_base(name , link,added_by,date_added):
    cursor.execute('INSERT INTO channels (name, link, added_by, date_added) VALUES (?, ?, ?, ?);',(name, link, added_by, date_added))
    conn.commit()

def remove_channel_base(link_or_username):
    # Tozalash
    if link_or_username.startswith("https://t.me/"):
        username = link_or_username.replace("https://t.me/", "")
    elif link_or_username.startswith("@"):
        username = link_or_username[1:]
    else:
        username = link_or_username

    # Bazadagi linklar to‘liq bo‘lishi mumkin, shuning uchun LIKE bilan izlaymiz
    cursor.execute("DELETE FROM channels WHERE link LIKE ?", (f"%{username}%",))
    conn.commit()

    return cursor.rowcount > 0

def update_channels(chat_id,link):
    cursor.execute(f"""UPDATE channels SET link = '{link}' WHERE channel_id = {chat_id} """)
    conn.commit()
    
def get_channels():
    cursor.execute("SELECT * FROM channels")
    data = cursor.fetchall()
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

def get_series_base2(anime_id):
    try:
        cursor.execute(f"""SELECT * FROM series WHERE serie_id = {anime_id}""")
        data = cursor.fetchall()
        conn.commit()
    except:
        data = []
    return data
    
def get_random_anime_sql():
    cursor.execute("SELECT * FROM anime ORDER BY RANDOM() LIMIT 1")
    result = cursor.fetchone()
    if result:
        return [result]  # Ro‘yxat shaklida qaytarilyapti
    else:
        return []

def similar(a, b):
    """Ikki matn o'rtasidagi o'xshashlikni hisoblash (0-1 oraliqda)."""
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()

def search_anime_base(prompt):
    prompt = prompt.strip().lower()
    cursor = conn.cursor()
    cursor.row_factory = sqlite3.Row

    if prompt.isdigit():
        anime_by_id = cursor.execute("SELECT * FROM anime WHERE anime_id = ?", (int(prompt),)).fetchone()
        if anime_by_id:
            return [anime_by_id]  
    fts_query = """
        SELECT anime.* FROM anime
        JOIN anime_fts ON anime.anime_id = anime_fts.rowid
        WHERE anime_fts MATCH ?
    """
    try:
        results = cursor.execute(fts_query, [prompt]).fetchall()
        if results:
            return results
    except Exception as e:
        print("FTS5 xato:", e)
    like_query = """
        SELECT * FROM anime
        WHERE LOWER(name) LIKE ? 
           OR LOWER(genre) LIKE ? 
           OR LOWER(teg) LIKE ?
    """
    like_results = cursor.execute(like_query, [f"%{prompt}%", f"%{prompt}%", f"%{prompt}%"]).fetchall()

    similar_results = []
    for row in like_results:
        name_words = row["name"].lower().split()
        genre_tags = str(row["genre"]).lower().split(",") if row["genre"] else []
        tegs = str(row["teg"]).lower().split(",") if row["teg"] else []

        found = False
        for tag in tegs:
            tag = tag.strip()
            if similar(prompt, tag) >= 0.6:
                similar_results.append(row)
                found = True
                break

        if not found:
            for word in name_words + genre_tags:
                word = word.strip()
                if similar(prompt, word) >= 0.6:
                    similar_results.append(row)
                    break

    similar_results.sort(key=lambda row: max(
        [similar(prompt, tag.strip()) for tag in str(row["teg"]).lower().split(",") if tag.strip()] +
        [similar(prompt, word.strip()) for word in row["name"].lower().split()] +
        [similar(prompt, genre.strip()) for genre in str(row["genre"]).lower().split(",") if genre.strip()]
    ), reverse=True)
    print(like_results)

    return similar_results

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

def update_free_status(user_id, free_value):
    try:
        conn.execute("""
            UPDATE about_user
            SET free = ?
            WHERE user_id = ?
        """, (free_value, user_id))
        conn.commit()
        return f"User {user_id} uchun 'free' qiymati {free_value} ga yangilandi."
    except Exception as e:
        return f"Xatolik yuz berdi: {e}"

def get_free_status(user_id):
    try:
        cursor = conn.execute("""
            SELECT free FROM about_user WHERE user_id = ?
        """, (user_id,))
        result = cursor.fetchone()
        if result:
            return result[0]
        else:
            print(f"User {user_id} topilmadi.")
            return None
    except Exception as e:
        print(f"Xatolik yuz berdi: {e}")
        return None

def add_column_if_not_exists(conn, table_name, column_name, column_type):
    cursor = conn.cursor()
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = [info[1] for info in cursor.fetchall()]
    if column_name not in columns:
        conn.execute(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type}")
        conn.commit()

def get_seria_id(which_anime_value,serie_num_value):
    cursor = conn.execute("""
        SELECT serie_id 
        FROM series 
        WHERE which_anime = ? AND serie_num = ?
    """, (which_anime_value, serie_num_value))

    result = cursor.fetchone()
    if result:
        serie_id = result[0]
        return serie_id
    else:
        return "Bunday malumot topilmadi"
    

add_column_if_not_exists(conn, 'about_user', 'free', 'INTEGER DEFAULT 0')
add_column_if_not_exists(conn, 'about_user', 'is_blocked', 'INTEGER DEFAULT 0')

creating_table()
update_statistics()  


quality = "720p"
cursor = conn.execute("SELECT anime_id FROM anime WHERE anime_id <= 71")
result = cursor.fetchall()
which_anime = [row[0] for row in result]

which_anime.sort(reverse=True)
serie_id = 1570
def get_series_by_anime_id(anime_id):
    cursor = conn.execute("SELECT series FROM anime WHERE anime_id = ?", (anime_id,))
    result = cursor.fetchone()
    if result:
        return result[0]  
    return None 


def check_series(anime_id, seria_num):
    cursor = conn.execute(
        "SELECT 1 FROM series WHERE which_anime = ? AND serie_num = ? LIMIT 1",
        (anime_id, seria_num)
    )
    result = cursor.fetchone()
    return result is not None

for i in which_anime:
    seria=get_series_by_anime_id(i)
    for j in range(1,seria+1):
        if check_series(i, j):
            continue
        else:
            add_serie_base(i, serie_id, j, quality)
            serie_id -= 1