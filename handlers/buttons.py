from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from .languages import *

def user_button_btn(lang,is_vip):
    
    buttons = user_button(lang)
    
    cheker = ReplyKeyboardMarkup()
    if is_vip=="True":
        cheker.add(KeyboardButton(buttons[0]),KeyboardButton(buttons[3]))
        cheker.add(KeyboardButton(buttons[4]),KeyboardButton(buttons[5]))
        cheker.add(KeyboardButton(buttons[1]),KeyboardButton(buttons[2]))
        cheker.resize_keyboard = True  
        return cheker
    elif is_vip=="False" or is_vip=="None" or is_vip=='Nonetype' or is_vip==0 or is_vip=="0":
        cheker.add(KeyboardButton(buttons[0]),KeyboardButton(buttons[3]))
        cheker.add(KeyboardButton(buttons[1]),KeyboardButton(buttons[2]))
        cheker.add(KeyboardButton(buttons[5]))
        cheker.resize_keyboard = True  
        return cheker


def admin_button_btn():
    
    cheker = ReplyKeyboardMarkup()
    cheker.add(KeyboardButton("🆕Anime qo'shish")) 
    cheker.add(KeyboardButton("➕Seriya qo'shish"))
    cheker.add(KeyboardButton("✏️Animeni tahrirlash"),KeyboardButton("✏️Seriani tahrirlash"))
    cheker.add(KeyboardButton("📊Statik ma'lumotlar"))
    cheker.add(KeyboardButton("💬Xabar yuborish"),KeyboardButton("👤Alohida xabar"))
    cheker.add(KeyboardButton("🔐Majburiy a'zo"),KeyboardButton("👔Staff qo'shish"))
    cheker.add(KeyboardButton("👁‍🗨Post qilish"),KeyboardButton("🎞Seriani post qilish"))
    cheker.add(KeyboardButton("Qismli post"))
    cheker.add(KeyboardButton("Kanal qo'shish"),KeyboardButton("Kanal o'chirish"))
    cheker.add(KeyboardButton("Kanallar"))
    cheker.add(KeyboardButton("🔙Chiqish"))
    cheker.resize_keyboard = True  
    
    return cheker

def back_user_button_btn(lang):
    cheker = ReplyKeyboardMarkup()
    if lang == "uz":
        cheker.add(KeyboardButton("🔙Ortga"))
    cheker.resize_keyboard = True  

    return cheker

def back_button_btn():
    
    cheker = ReplyKeyboardMarkup()
    cheker.add(KeyboardButton("🔙Ortga"))
    cheker.resize_keyboard = True  
    
    return cheker