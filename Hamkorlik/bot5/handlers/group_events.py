from aiogram import types
from dispatcher import dp
from users_base import *
from .admin_actions import *
from datetime import *
from dateutil.relativedelta import relativedelta

@dp.callback_query_handler(text_contains = "vip",state="*")
async def qosh(call: types.CallbackQuery,state : FSMContext):

    command = call.data.split(",")[1]

    if command == "activate":

        user_id = int(call.data.split(",")[2])
        
        date_1 = datetime.now().strftime("%Y-%m-%d")
        date_1 = datetime.strptime(date_1, "%Y-%m-%d")
        result = date_1 + relativedelta(months= +1)
        result = str(result)[:-9]
        
        update_user_vip_base(user_id,result)
        
        try:
            text = f"""
✅<b>Sizga 1 oyga ⚡️AniPass aktivlashtirildi</b>
<b>⏳Tugash muddati :</b> {result}
"""
            a = await dp.bot.send_message(chat_id=user_id,text=text)
            await dp.bot.unpin_all_chat_messages(chat_id=user_id)
            await a.pin()

        except:
            pass
        
        text = f"""
<b>ID :</b> <code>{user_id}</code>
-
<b>⚡️AniPass ✅Tasdiqlandi</b>
"""
    
        await call.message.edit_text(text)

    else:
        user_id = int(call.data.split(",")[2])

        try:
            await dp.bot.send_message(chat_id=user_id,text=f"<b>⚡️AniPass uchun yuborgan so'rovingiz qabul qilinmadi❌</b>")
        except:
            pass
        
        text = f"""
<b>ID :</b> <code>{user_id}</code>
-
<b>⚡️AniPass ❌Bekor qilindi</b>
"""
        await call.message.edit_text(text)

@dp.callback_query_handler(text_contains = "lux",state="*")
async def qosh(call: types.CallbackQuery,state : FSMContext):

    month = call.data.split(",")[1]

    if month != "cancel":

        user_id = int(call.data.split(",")[2])
        
        date_1 = datetime.now().strftime("%Y-%m-%d")
        date_1 = datetime.strptime(date_1, "%Y-%m-%d")
        result1 = date_1 + relativedelta(months= +1)
        result = str(result1)[:-9]
        
        update_user_lux_base(user_id,result)

        try:
            await dp.bot.unban_chat_member(chat_id=-1002131546047,user_id=user_id)
        except:
            pass

        link = await dp.bot.create_chat_invite_link(chat_id=-1002131546047,member_limit = 1,expire_date=result1)
        
        try:
            text = f"""
✅<b>Sizga {month} oyga 💎Lux obuna aktivlashtirildi</b>
<b>⏳Tugash muddati :</b> {result}
-
<b>💎Lux kanalga qo'shilish uchun 1 martalik link : {link.invite_link}</b> 
"""
            a = await dp.bot.send_message(chat_id=user_id,text=text)
            await dp.bot.unpin_all_chat_messages(chat_id=user_id)
            await a.pin()

        except:
            pass
        
        text = f"""
<b>ID :</b> <code>{user_id}</code>
-
<b>💎Lux obuna ✅Tasdiqlandi</b>
"""
    
        await call.message.edit_text(text)

    else:
        user_id = int(call.data.split(",")[2])

        try:
            await dp.bot.send_message(chat_id=user_id,text=f"<b>💎Lux obuna uchun yuborgan so'rovingiz qabul qilinmadi❌</b>")
        except:
            pass
        
        text = f"""
<b>ID :</b> <code>{user_id}</code>
-
<b>💎Lux obuna ❌Bekor qilindi</b>
"""
        await call.message.edit_text(text)