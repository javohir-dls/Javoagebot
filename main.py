from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.enums import ChatMemberStatus

TOKEN = "YOUR_BOT_TOKEN_HERE"
CHANNEL_ID = "@xushboqovblog" # Sizning kanal manzilingiz

bot = Bot(token=TOKEN)
dp = Dispatcher()

# Obuna tugmalari
def get_subs_kb():
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📢 Telegram kanal", url="https://t.me/xushboqovblog")],
        [InlineKeyboardButton(text="📸 Instagram sahifa", url="https://instagram.com/javohir.ftbl")],
        [InlineKeyboardButton(text="✅ Tekshirish", callback_data="check_subs")]
    ])
    return kb

# Obunani tekshirish funksiyasi
async def is_subscribed(user_id):
    try:
        member = await bot.get_chat_member(chat_id=CHANNEL_ID, user_id=user_id)
        if member.status in [ChatMemberStatus.MEMBER, ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.CREATOR]:
            return True
    except Exception:
        return False
    return False

@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    if await is_subscribed(message.from_user.id):
        await message.answer("Xush kelibsiz! Tug'ilgan sanangizni yozing (DD.MM.YYYY):")
    else:
        await message.answer("Botdan foydalanish uchun avval kanalimiz va sahifamizga obuna bo'ling!", reply_markup=get_subs_kb())

@dp.callback_query(F.data == "check_subs")
async def check_subs_callback(callback: types.CallbackQuery):
    if await is_subscribed(callback.from_user.id):
        await callback.message.edit_text("Ajoyib! Endi tug'ilgan sanangizni yozishingiz mumkin (DD.MM.YYYY).")
    else:
        await callback.answer("Siz hali kanalga obuna bo'lmadingiz!", show_alert=True)

