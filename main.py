import os
import asyncio
import logging
from aiohttp import web
from datetime import datetime, date

from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.enums import ChatMemberStatus
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from dateutil.relativedelta import relativedelta

from config import TOKEN, CHANNEL_ID, RENDER_URL

logging.basicConfig(level=logging.INFO)

bot = Bot(token=TOKEN)
dp = Dispatcher()

WEBHOOK_PATH = f"/bot/{TOKEN}"
WEBHOOK_URL = f"{RENDER_URL.rstrip('/')}{WEBHOOK_PATH}"

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
    except Exception:
        return False

@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    if await is_subscribed(message.from_user.id):
        await message.answer("Xush kelibsiz! Tug'ilgan sanangizni DD.MM.YYYY formatida yozing.")
    else:
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📢 Kanal", url="https://t.me/xushboqovblog")],
            [InlineKeyboardButton(text="📸 Instagram", url="https://instagram.com/javohir.ftbl")],
            [InlineKeyboardButton(text="✅ Tekshirish", callback_data="check_subs")]
        ])
        await message.answer("Botdan foydalanish uchun obuna bo'ling:", reply_markup=kb)

@dp.callback_query(F.data == "check_subs")
async def check_subs(callback: types.CallbackQuery):
    if await is_subscribed(callback.from_user.id):
        await callback.message.edit_text("Ajoyib! Endi tug'ilgan sanangizni yozing (DD.MM.YYYY):")
    else:
        await callback.answer("Hali obuna bo'lmagansiz!", show_alert=True)

@dp.message(F.text.regexp(r"^\d{2}\.\d{2}\.\d{4}$"))
async def process_date(message: types.Message):
    try:
        bd = datetime.strptime(message.text, "%d.%m.%Y").date()
        today = date.today()
        delta = relativedelta(today, bd)
        
        total_days = (today - bd).days
        total_weeks = total_days // 7
        total_months = delta.years * 12 + delta.months
        
        try:
            next_bd = bd.replace(year=today.year)
        except ValueError:
            next_bd = date(today.year, 3, 1)
        if next_bd < today:
            try:
                next_bd = bd.replace(year=today.year + 1)
            except ValueError:
                next_bd = date(today.year + 1, 3, 1)
        
        days_to_bd = (next_bd - today).days
        days_uz = ["Dushanba", "Seshanba", "Chorshanba", "Payshanba", "Juma", "Shanba", "Yakshanba"]
        
        res = (
            f"👤 Ism: {message.from_user.full_name}\n"
            f"🎂 Tug'ilgan sana: {message.text}\n\n"
            f"📅 Yoshingiz: {delta.years} yil, {delta.months} oy, {delta.days} kun\n"
            f"📆 Jami yashagan kun: {total_days:,} kun\n"
            f"🗓 Jami yashagan hafta: {total_weeks:,} hafta\n"
            f"📅 Jami yashagan oy: {total_months:,} oy\n\n"
            f"🗓 Tug'ilgan kun haftasi: {days_uz[bd.weekday()]}\n"
            f"🎉 Tug'ilgunga qadar: {days_to_bd} kun\n"
            f"♈ Burjingiz: {get_zodiac(bd.day, bd.month)}\n"
            f"🐯 Muchalingiz: {get_muchal(bd.year)}"
        )
        await message.answer(res)
    except Exception:
        await message.answer("Xatolik! Sanani to'g'ri formatda kiriting (Masalan: 31.01.2010).")

async def on_startup(bot: Bot):
    await bot.delete_webhook(drop_pending_updates=True)
    await bot.set_webhook(WEBHOOK_URL)

async def on_shutdown(bot: Bot):
    await bot.delete_webhook()

async def main():
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)
    app = web.Application()
    SimpleRequestHandler(dispatcher=dp, bot=bot).register(app, path=WEBHOOK_PATH)
    setup_application(app, dp, bot=bot)
    
    async def health(request):
        return web.Response(text="Bot ishlayapti!")
    
    app.router.add_get("/", health)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', int(os.getenv("PORT", 8080)))
    await site.start()
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())
