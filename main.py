import asyncio
import logging

from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.enums import ChatMemberStatus
from dateutil.relativedelta import relativedelta
from datetime import datetime

from config import BOT_TOKEN, CHANNEL_ID, INSTAGRAM_URL

logging.basicConfig(level=logging.INFO)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
# --- Yordamchi funksiyalar ---
def get_muchal(year):
    muchallar = ["Sichqon", "Sigir", "Yo'lbars", "Quyon", "Ajdar", "Ilon", "Ot", "Qo'y", "Maymun", "Tovuq", "It", "To'ng'iz"]
    return muchallar[(year - 1900) % 12]

def get_zodiac(day, month):
    if (month == 3 and day >= 21) or (month == 4 and day <= 19): return "Hamal (Qo'y)"
    if (month == 4 and day >= 20) or (month == 5 and day <= 20): return "Savr (Buzoq)"
    if (month == 5 and day >= 21) or (month == 6 and day <= 20): return "Javzo (Egizaklar)"
    if (month == 6 and day >= 21) or (month == 7 and day <= 22): return "Saraton (Qisqichbaqa)"
    if (month == 7 and day >= 23) or (month == 8 and day <= 22): return "Asad (Arslon)"
    if (month == 8 and day >= 23) or (month == 9 and day <= 22): return "Sunbula (Parizod)"
    if (month == 9 and day >= 23) or (month == 10 and day <= 22): return "Mezon (Tarozi)"
    if (month == 10 and day >= 23) or (month == 11 and day <= 21): return "Aqrab (Chayon)"
    if (month == 11 and day >= 22) or (month == 12 and day <= 21): return "Qavs (O'qotar)"
    if (month == 12 and day >= 22) or (month == 1 and day <= 19): return "Jadi (Tog' echkisi)"
    if (month == 1 and day >= 20) or (month == 2 and day <= 18): return "Dalv (Qovg'a)"
    if (month == 2 and day >= 19) or (month == 3 and day <= 20): return "Hut (Baliq)"
    return "Noma'lum"

async def is_subscribed(user_id):
    try:
        member = await bot.get_chat_member(chat_id=CHANNEL_ID, user_id=user_id)
        return member.status in [ChatMemberStatus.MEMBER, ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.CREATOR]
    except:
        return False

# --- Handlerlar ---
@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    if await is_subscribed(message.from_user.id):
        await message.answer("Xush kelibsiz! Tug'ilgan sanangizni DD.MM.YYYY formatida yozing (masalan: 15.05.2000).")
    else:
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📢 Telegram kanal", url="https://t.me/xushboqovblog")],
            [InlineKeyboardButton(text="📸 Instagram sahifa", url="https://instagram.com/javohir.ftbl")],
            [InlineKeyboardButton(text="✅ Tekshirish", callback_data="check_subs")]
        ])
        await message.answer("Botdan foydalanish uchun kanal va sahifamizga obuna bo'ling:", reply_markup=kb)

@dp.callback_query(F.data == "check_subs")
async def check_subs_callback(callback: types.CallbackQuery):
    if await is_subscribed(callback.from_user.id):
        await callback.message.edit_text("Ajoyib! Endi tug'ilgan sanangizni yozing (DD.MM.YYYY).")
    else:
        await callback.answer("Siz hali obuna bo'lmadingiz!", show_alert=True)

@dp.message(F.text.regexp(r"\d{2}\.\d{2}\.\d{4}"))
async def handle_date(message: types.Message):
    try:
        birth_date = datetime.strptime(message.text, "%d.%m.%Y")
        today = datetime.now()
        diff = relativedelta(today, birth_date)
        
        # Keyingi tug'ilgan kun
        next_bd = birth_date.replace(year=today.year)
        if next_bd < today: next_bd = next_bd.replace(year=today.year + 1)
        days_to_bd = (next_bd - today).days

        response = (
            f"📅 Siz {diff.years} yil, {diff.months} oy, {diff.days} kun yashadingiz.\n"
            f"✨ Muchalingiz: {get_muchal(birth_date.year)}\n"
            f"♈️ Burjingiz: {get_zodiac(birth_date.day, birth_date.month)}\n"
            f"🎂 Keyingi tug'ilgan kuningizga {days_to_bd} kun qoldi."
        )
        await message.answer(response)
    except:
        await message.answer("Xatolik! Sanani to'g'ri kiriting (masalan: 15.05.2000).")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
