import asyncio
from aiogram import types, Dispatcher
from aiogram.dispatcher.handler import CancelHandler
from aiogram.dispatcher.middlewares import BaseMiddleware
from aiogram.utils.exceptions import Throttled
from users_base import get_user_base

class ThrottlingMiddleware(BaseMiddleware):
    
    
    def __init__(self,limit: int = 0.9):
        BaseMiddleware.__init__(self)
        self.rate_limit = limit
        
    async def on_process_message(self,msg : types.Message , data : dict):
        dp = Dispatcher.get_current()
        
        try: 
            await dp.throttle(key="antiflood_message", rate=self.rate_limit)
        except Throttled as _t:
            await self.msg_throttle(msg,_t)
            raise CancelHandler()
    async def msg_throttle(self, msg:types.Message, throttled : Throttled):
        if throttled.exceeded_count <= 2:
            if not msg.sender_chat and str(msg.chat.id)[0] != "-":
                try:
                    user = get_user_base(msg.from_user.id)
                    lang = user[0][2]
                    is_admin = user[0][7] 
                    if is_admin != True:
                        if lang == "uz":
                            text = "⌛️Flud qilmang ! 5 soniyadan so'ng qayta urinib koring !"
                        elif lang == "ru":
                            text = "⌛️Не флюдьте! Пожалуйста, повторите попытку через 5 секунд !"
                            
                        await msg.reply(text)
                        await asyncio.sleep(6)
                except:
                    pass
                
           
            
