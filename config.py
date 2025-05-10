from dotenv import load_dotenv
import os
import sqlite3
import shutil
import re
import uuid
from users_base import *
# 1. Yozuvchilarni yuklash
load_dotenv()

BOT_OWNERS = os.getenv('BOT_OWNERS')
BOT_TOKEN = os.getenv('BOT_TOKEN')

KARTA_RAQAM = '9860 1201 6396 3172'
KARTA_NOMI = 'Umarbek Azimov'
REKLAMA = '@aniduble_rek'
ADMIN = '@Aniduble_admin'
ANIDUBLE = '@ANIDUBLE_RASMIY_BOT'
BOT_NAME = "Aniduble"
POST_KANAL =-1002023259288
# 2. Hamkorlar bazasini yaratish
BASE_DIR = os.path.dirname(os.path.abspath(__file__)) 
db_path = os.path.join(BASE_DIR, 'hamkor.db')

conn = sqlite3.connect(db_path, timeout=10)
cursor = conn.cursor()

def create_table():
    with sqlite3.connect(db_path, timeout=10) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS hamkor (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                token TEXT NOT NULL UNIQUE,
                reklama_kanal TEXT NOT NULL,
                admin TEXT NOT NULL,
                karta_nomi TEXT NOT NULL,
                karta_raqam TEXT NOT NULL,
                bot_username TEXT NOT NULL,
                kanal_nomi TEXT NOT NULL,
                post_kanal TEXT NOT NULL
            )
        """)
        conn.commit()
        print("Hamkor jadvali muvaffaqiyatli yaratildi yoki allaqachon mavjud.")

def insert_data(token, reklama_kanal, admin, karta_nomi, karta_raqam, bot_username, kanal_nomi, post_kanal):
    with sqlite3.connect(db_path, timeout=10) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO hamkor (token, reklama_kanal, admin, karta_nomi, karta_raqam, bot_username, kanal_nomi, post_kanal)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (token, reklama_kanal, admin, karta_nomi, karta_raqam, bot_username, kanal_nomi, post_kanal))
        conn.commit()

create_table()

# 3. Hamkor statelarni va maxsus kod bloklarini olib tashlash
def modify_admin_actions(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            code = f.read()
    except FileNotFoundError:
        print(f"Xato: {file_path} fayli topilmadi!")
        return None

    print(f"{file_path} fayli topildi. Original kod uzunligi: {len(code)}")

    # 3.1. `from config import ...` qatorini o'zgartirish
    import_pattern = r'from config import BOT_NAME,\s*BOT_TOKEN,\s*insert_data'
    if re.search(import_pattern, code):
        code = re.sub(import_pattern, 'from config import BOT_NAME, BOT_TOKEN', code)
        print("`insert_data` importdan o'chirildi")
    else:
        print("`from config import BOT_NAME, BOT_TOKEN, insert_data` topilmadi")

    # 3.2. Hamkor classidagi state nomlarini topamiz va handlerlarni o'chiramiz
    match = re.search(r'class Hamkor\(StatesGroup\):\s+((?:\s+\w+\s*=\s*State\(\)\s*)+)', code)
    if match:
        state_block = match.group(1)
        state_names = re.findall(r'(\w+)\s*=\s*State\(\)', state_block)
        state_names_lower = [s.lower() for s in state_names]

        # Hamkor state bilan bog'liq handlerlarni olib tashlash
        handler_pattern = r'(@dp\.(?:message_handler|callback_query_handler)[\s\S]+?async def [\s\S]+?\n(?:\s+.+\n)+)'
        blocks = re.findall(handler_pattern, code)
        for block in blocks:
            if any(state in block.lower() for state in state_names_lower):
                code = code.replace(block, '')
                print(f"Hamkor bilan bog'liq handler o'chirildi: {block[:50]}...")

    # 3.3. Maxsus elif bloklarini olib tashlash
    specific_blocks = [
        (
            r'''elif\s+text\s*==\s*"Hamkorlik dasturi"\s*:\s*\n\s*await\s+state\.finish\(\)\s*\n\s*await\s+msg\.answer\("Tanlang:",\s*reply_markup=hamkor_btn\(\)\)\s*\n*''',
            '"Hamkorlik dasturi" bloki'
        ),
        (
            r'''elif\s+text\s*==\s*"Qismli post"\s*:\s*\n\s*await\s+state\.finish\(\)\s*\n\s*await\s+Posting\.select_anime\.set\(\)\s*\n\s*await\s+msg\.answer\("Qaysi animeni qismini post qilamiz",\s*reply_markup=back_button_btn\(\)\)\s*\n*''',
            '"Qismli post" bloki'
        ),
        (
            r'''elif\s+text\s*==\s*"Kanal qo'shish"\s*:\s*\n\s*await\s+state\.finish\(\)\s*\n\s*await\s+Add_sponser\.add\.set\(\)\s*\n\s*await\s+msg\.answer\("Qo'shmoqchi bo'lgan kanal linkini yuboring",\s*reply_markup=back_button_btn\(\)\)\s*\n*''',
            '"Kanal qo\'shish" bloki'
        ),
        (
            r'''elif\s+text\s*==\s*"Kanal o'chirish"\s*:\s*\n\s*await\s+state\.finish\(\)\s*\n\s*await\s+Add_sponser\.remove\.set\(\)\s*\n\s*await\s+msg\.answer\("O'chirmoqchi bo'lgan kanal linkini yuboring",\s*reply_markup=back_button_btn\(\)\)\s*\n*''',
            '"Kanal o\'chirish" bloki'
        ),
        (
            r'''elif\s+text\s*==\s*"Kanallar"\s*:\s*\n\s*await\s+state\.finish\(\)\s*#\s*Stateni\s+tugatish\s*\n\s*channels\s*=\s*get_channels\(\)\s*\n\s*if\s*not\s*channels:\s*\n\s*await\s+msg\.answer\("Hozircha hech qanday kanal qo'shilmagan\."\)\s*\n\s*return\s*\n\s*text\s*=\s*"📢\s*<b>Kanallar\s*ro'yxati:</b>\n\n"\s*\n\s*for\s*ch\s*in\s*channels:\s*\n\s*text\s*\+=\s*\(\s*\n\s*f"🔹\s*<b>Nomi:</b>\s*{ch\[1\]}\n"\s*\n\s*f"🔗\s*<b>Havola:</b>\s*{ch\[2\]}\n"\s*\n\s*f"🕒\s*<b>Qo'shilgan\s*sana:</b>\s*{ch\[4\]}\n\n"\s*\n\s*\)\s*\n\s*await\s+msg\.answer\(text,\s*parse_mode="HTML"\)\s*\n\s*await\s+Admin\.menu\.set\(\)\s*\n*''',
            '"Kanallar" bloki'
        )
    ]

    for pattern, block_name in specific_blocks:
        if re.search(pattern, code, re.MULTILINE):
            code = re.sub(pattern, '', code, flags=re.MULTILINE)
            print(f"{block_name} o'chirildi")
        else:
            print(f"{block_name} regex bilan topilmadi, aniq moslik sinovi...")
            exact_block = {
                '"Hamkorlik dasturi" bloki': '''elif text == "Hamkorlik dasturi":
    await state.finish()
    await msg.answer("Tanlang:",reply_markup=hamkor_btn())
''',
                '"Qismli post" bloki': '''elif text == "Qismli post":
    await state.finish()
    await Posting.select_anime.set()
    await msg.answer("Qaysi animeni qismini post qilamiz",reply_markup=back_button_btn())
''',
                '"Kanal qo\'shish" bloki': '''elif text == "Kanal qo'shish":
    await state.finish()
    await Add_sponser.add.set()
    await msg.answer("Qo'shmoqchi bo'lgan kanal linkini yuboring",reply_markup=back_button_btn())
''',
                '"Kanal o\'chirish" bloki': '''elif text == "Kanal o'chirish":
    await state.finish()
    await Add_sponser.remove.set()
    await msg.answer("O'chirmoqchi bo'lgan kanal linkini yuboring",reply_markup=back_button_btn())
''',
                '"Kanallar" bloki': '''elif text == "Kanallar":
    await state.finish()  # Stateni tugatish
    channels = get_channels()
    if not channels:
        await msg.answer("Hozircha hech qanday kanal qo'shilmagan.")
        return
    text = "📢 <b>Kanallar ro'yxati:</b>\n\n"
    for ch in channels:
        text += (
            f"🔹 <b>Nomi:</b> {ch[1]}\n"
            f"🔗 <b>Havola:</b> {ch[2]}\n"
            f"🕒 <b>Qo'shilgan sana:</b> {ch[4]}\n\n"
        )

    await msg.answer(text, parse_mode="HTML")
    await Admin.menu.set()
'''
            }
            if exact_block[block_name] in code:
                code = code.replace(exact_block[block_name], '')
                print(f"{block_name} aniq moslik bilan o'chirildi")
            else:
                print(f"{block_name} kodda topilmadi")

    # Ortiqcha bo'sh qatorlarni tozalash
    code = re.sub(r'\n\s*\n+', '\n', code).strip()

    print(f"Yakuniy kod uzunligi: {len(code)}")
    return code

# 4. Fayllarni ko‘chirish
files_to_copy = [
    '.gitignore', 'handlers', 'media',
    'bot.py', 'database.db', 'dispatcher.py', 'filters.py',
    'requirements.txt', 'throttling.py', 'users_base.py'
]

target_root = os.path.join(BASE_DIR, 'Hamkorlik')

conn = sqlite3.connect(db_path)
cursor = conn.cursor()
cursor.execute("SELECT * FROM hamkor")
bots = cursor.fetchall()
conn.close()

    # database.db faylini tozalash
# db_path = os.path.join(BASE_DIR, 'database.db')
# try:
#     clear_users()  # Foydalanuvchilarni o‘chirish
# except Exception as e:
#     raise
# if not bots:
#     print("hamkor.db da botlar topilmadi. Skript to'xtatilmoqda.")
#     exit()

# for index, bot in enumerate(bots, start=1):
#     bot_folder = os.path.join(target_root, f'bot{index}')
#     os.makedirs(bot_folder, exist_ok=True)
#     print(f"Bot papkasi yaratilmoqda: {bot_folder}")

#     for item in files_to_copy:
#         src = os.path.join(BASE_DIR, item)
#         dst = os.path.join(bot_folder, item)

#         if os.path.isdir(src):
#             if item == 'handlers':
#                 # handlers direktoriyasini nusxalash va admin_actions.py ni o'zgartirish
#                 shutil.copytree(src, dst, dirs_exist_ok=True)
#                 print(f"Direktoriya nusxalandi: {item}")
#                 src_admin_actions = os.path.join(src, 'admin_actions.py')
#                 dst_admin_actions = os.path.join(dst, 'admin_actions.py')
#                 if os.path.exists(src_admin_actions):
#                     cleaned_code = modify_admin_actions(src_admin_actions)
#                     if cleaned_code is not None:
#                         with open(dst_admin_actions, 'w', encoding='utf-8') as f:
#                             f.write(cleaned_code)
#                         print(f"O'zgartirildi va nusxalandi: {dst_admin_actions}")
#                     else:
#                         print(f"Xato: {src_admin_actions} ni o'zgartirib bo'lmadi")
#                 else:
#                     print(f"Xato: {src_admin_actions} fayli topilmadi")
#             else:
#                 shutil.copytree(src, dst, dirs_exist_ok=True)
#                 print(f"Direktoriya nusxalandi: {item}")
#         else:
#             shutil.copy2(src, dst)
#             print(f"Fayl nusxalandi: {item}")

#     # config.py yozish
#     print(bot)
#     config_content = f'''BOT_TOKEN = "{bot[1]}"
# REKLAMA = "{bot[2]}"
# ADMIN = "{bot[3]}"
# KARTA_NOMI = "{bot[4]}"
# KARTA_RAQAM = "{bot[5]}"
# ANIDUBLE = "{bot[6]}"
# BOT_NAME = "{bot[7]}"
# BOT_OWNERS ="{[5306481482]}"
# POST_KANAL = "{bot[8]}"
# '''
#     config_path = os.path.join(bot_folder, 'config.py')
#     with open(config_path, 'w', encoding='utf-8') as f:
#         f.write(config_content)
#     print(f"Yaratildi: {config_path}")
