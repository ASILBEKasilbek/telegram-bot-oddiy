from dotenv import load_dotenv
import os

load_dotenv()


BOT_TOKEN =os.getenv('BOT_TOKEN')
BOT_OWNERS = os.getenv('BOT_OWNERS')

# from dotenv import load_dotenv
# import os

# load_dotenv()

# BOT_TOKEN = os.getenv('BOT_TOKEN').split(',')
# ANIDUBLE='ANIDUBLE_RASMIY_BOT'
# # Ownerlar ko‘p bo‘lsa, list qilib olamiz, hatto bitta bo‘lsa ham split qilsa yaxshi
# BOT_OWNERS = os.getenv('BOT_OWNERS')
