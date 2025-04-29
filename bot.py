from aiogram import executor
from dispatcher import dp
import handlers
from handlers.set_command import set_default_commands

async def on_startup(dispatcher):
    await set_default_commands(dispatcher)

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True , on_startup=on_startup)  

# import asyncio
# import logging
# from dispatcher import create_bot_and_dispatcher
# import handlers
# from config import BOT_TOKENS
# from handlers.set_command import set_default_commands

# async def on_startup(dispatcher):
#     await set_default_commands(dispatcher)

# async def start_bot(token):
#     bot, dp = create_bot_and_dispatcher(token)

#     # handlers.register_handlers(dp)

#     await on_startup(dp)
#     print(f"✅ Bot {token} ishga tushdi!")

#     try:

#         await dp.start_polling()
#     finally:
#         await bot.session.close()

# async def main():
#     tasks = [start_bot(token) for token in BOT_TOKENS]
#     await asyncio.gather(*tasks)

# if __name__ == "__main__":
#     logging.basicConfig(level=logging.INFO)
#     asyncio.run(main())
