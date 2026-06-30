import os
import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.enums import ChatMemberStatus
from dateutil.relativedelta import relativedelta
from datetime import datetime, date

# Kanal ID
CHANNEL_ID = "@xushboqovblog"
dp = Dispatcher()

# --- Yordamchi Funksiyalar ---
def is_leap(year):
    return year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)

def get_muchal(year):
    muchallar = ["Sichqon", "Sigir", "Yo'lbars", "Quyon", "Ajdar", "Ilon", "Ot", "Qo'y", "Maymun", "Tovuq", "It", "To'ng'iz"]
    return muchallar[(year - 1900) % 12]

def get_zodiac(day, month):
    zodiacs = [
        ((1, 20), (2, 18), "Dalv (Qovg'a)"), ((2, 19), (3, 20), "Hut (Baliq)"),
        ((3, 21), (4, 19), "Hamal (Qo'y)"), ((4, 20), (5, 20), "Savr (Buzoq)"),
        ((5, 21), (6, 20), "Javzo (Egizaklar)"), ((6, 21), (7, 22), "Saraton (Qisqichbaqa)"),
        ((7, 23), (8, 22), "Asad (Arslon)"), ((8, 23), (9, 22), "Sunbula (Parizod)"),
        ((9, 23), (10, 22), "Mezon (Tarozi)"), ((10, 23), (11, 21), "Aqrab (Chayon)"),
        ((11, 22), (12, 21), "Qavs (O'qotar)"), ((12, 22), (1, 19), "Jadi (Tog' echkisi)")
    ]
    for start, end, name in zodiacs:
        if (month == start[0] and day >= start[1]) or (month == end[0] and day <= end[1]):
            return name
    return "Noma'lum"

async def is_subscribed(user_id):
    try:
        member = await bot.get_chat_member(chat_id=CHANNEL_ID, user_id=user_id)
        return member.status in [ChatMemberStatus.MEMBER, ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.CREATOR]
    except:except Exception as e:
    print(e)
    await message.answer("Xatolik! Sanani to'g'ri formatda kiriting (Masalan: 31.01.2010)")

# --- Handlerlar ---
@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    if await is_subscribed(message.from_user.id):
        await message.answer("Xush kelibsiz! Tug'ilgan sanangizni DD.MM.YYYY formatida yozing (masalan: 31.01.2010):")
    else:
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📢 Telegram kanal", url="https://t.me/xushboqovblog")],
            [InlineKeyboardButton(text="📸 Instagram sahifa", url="https://instagram.com/javohir.ftbl")],
            [InlineKeyboardButton(text="✅ Tekshirish", callback_data="check_subs")]
        ])
        await message.answer("Botdan foydalanish uchun kanal va sahifamizga obuna bo'ling:", reply_markup=kb)

@dp.callback_query(F.data == "check_subs")
async def check_subs(callback: types.CallbackQuery):
    if await is_subscribed(callback.from_user.id):
        await callback.message.edit_text("Ajoyib! Endi tug'ilgan sanangizni yozing (DD.MM.YYYY):")
    else:
        await callback.answer("Siz hali obuna bo'lmadingiz!", show_alert=True)

@dp.message(F.text.regexp(r"\d{2}\.\d{2}\.\d{4}"))
async def process_date(message: types.Message):
    try:
        bd = datetime.strptime(message.text, "%d.%m.%Y").date()
        today = date.today()
        
        # Yoshni aniq hisoblash
        delta = relativedelta(today, bd)
        total_days = (today - bd).days
        total_weeks = total_days // 7
        total_months = delta.years * 12 + delta.months
        
        # 29-fevral mantiqi (Keyingi tug'ilgan kun)
        if bd.month == 2 and bd.day == 29:
            next_year = today.year if is_leap(today.year) and today < date(today.year, 2, 29) else today.year + 1
            while not is_leap(next_year):
                next_year += 1
            next_bd = date(next_year, 2, 29)
        else:
            next_bd = date(today.year, bd.month, bd.day)
            if next_bd < today:
                next_bd = next_bd.replace(year=today.year + 1)
        
        days_to_bd = (next_bd - today).days
        
        # Haftani aniqlash
        days_uz = ["Dushanba", "Seshanba", "Chorshanba", "Payshanba", "Juma", "Shanba", "Yakshanba"]
        weekday = days_uz[bd.weekday()]
        
        res = (
            f"👤 Ism: {message.from_user.full_name}\n"
            f"🎂 Tug'ilgan sana: {message.text}\n\n"
            f"📅 Yoshingiz:\n• {delta.years} yil\n• {delta.months} oy\n• {delta.days} kun\n\n"
            f"📆 Jami:\n• {total_days} kun\n• {total_months} oy\n• {total_weeks} hafta\n\n"
            f"🗓 Tug'ilgan kun: {weekday}\n"
            f"🎉 Keyingi tug'ilgan kuningizga: {days_to_bd} kun\n"
            f"♈ Burjingiz: {get_zodiac(bd.day, bd.month)}\n"
            f"🐯 Muchalingiz: {get_muchal(bd.year)}"
        )
        await message.answer(res)
    except:
        await message.answer("Xatolik! Sanani to'g'ri formatda kiriting (Masalan: 31.01.2010)")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
