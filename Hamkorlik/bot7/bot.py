# bot.py
from aiogram import executor
from dispatcher import dp
from handlers.set_command import set_default_commands
from handlers.admin_actions import schedule_expired_check  # shu yerga import qiling
import asyncio

async def on_startup(dispatcher):
    await set_default_commands(dispatcher)
    asyncio.create_task(schedule_expired_check())  # to‘g‘ri joy

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
    