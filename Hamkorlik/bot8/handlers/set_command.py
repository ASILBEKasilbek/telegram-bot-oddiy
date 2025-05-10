from aiogram import types

async def set_default_commands(dp):
    await dp.bot.set_my_commands(
        [
            types.BotCommand("start", "⚪️Botni ishga tushirish | 🟡Botni yangilash"),
            types.BotCommand("help", "📚Qo'llanma | Botdan qanday foydalanish"),
        ]
    )
