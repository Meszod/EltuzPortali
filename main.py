import asyncio
import logging
from datetime import datetime
from aiogram import Bot, Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command
from aiogram.utils import executor

# --- Sozlamalar ---
API_TOKEN = "8544367775:AAGSv3nppSasbh1HsfyhOs2dD_ti2WMRemA"
ADMIN_IDS = [8517530604, 6476871794]

logging.basicConfig(level=logging.INFO)

# Bot va dispatcher yaratish
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# Foydalanuvchi tillari
user_language = {}

# Til tanlash klaviaturasi
def language_keyboard():
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(text="🇺🇿 O'zbekcha", callback_data="lang_uz"))
    keyboard.add(types.InlineKeyboardButton(text="🇷🇺 Русский", callback_data="lang_ru"))
    return keyboard

# /start komandasi
@dp.message_handler(commands=['start'])
async def start_command(message: types.Message):
    await message.answer("Tilni tanlang / Выберите язык:", reply_markup=language_keyboard())

# Til tanlanganda
@dp.callback_query_handler(lambda callback: callback.data.startswith("lang_"))
async def language_chosen(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    lang = callback.data.split("_")[1]
    user_language[user_id] = lang

    if lang == "uz":
        text = (
            "Assalomu alaykum, bu Eltuz portalining murojaat boti.\n\n"
            "Ariza va shikoyatingiz yoki fosh etuvchi ma'lumotingiz bo'lsa, "
            "mazmunini qisqacha tushuntirib yozing. Hujjatlar, foto, audio va "
            "videolar bo'lsa ilova qilib yo'llang. Aloqa uchun telegram manzilingizni yozib yuboring."
        )
    else:
        text = (
            "Здравствуйте. Это бот для обращений портала Eltuz.\n\n"
            "Если у вас есть жалоба или разоблачающая информация, кратко опишите суть. "
            "Прикрепите документы, фото, аудио или видео, если имеются. "
            "Укажите ваш Telegram для связи."
        )

    await callback.message.answer(text)
    await callback.answer()

# Oddiy xabarlarni qabul qilish
@dp.message_handler(content_types=['text', 'photo', 'video', 'audio', 'document', 'voice'])
async def handle_message(message: types.Message):
    user_id = message.from_user.id
    lang = user_language.get(user_id, "uz")

    if lang == "uz":
        response_text = "✅ Murojaatingiz qabul qilindi. Adminlar ko'rib chiqadi."
    else:
        response_text = "✅ Ваше обращение принято. Администраторы рассмотрят его."

    await message.answer(response_text)

    # Admin uchun ma'lumotlar tayyorlash
    user = message.from_user
    username = f"@{user.username}" if user.username else "Yo'q"
    first_name = user.first_name if user.first_name else "Yo'q"
    last_name = user.last_name if user.last_name else "Yo'q"
    user_selected_lang = user_language.get(user_id, "uz")
    lang_display = "🇺🇿 O'zbekcha" if user_selected_lang == "uz" else "🇷🇺 Русский"

    user_info = (
        f"📋 YANGI MUROJAAT\n\n"
        f"👤 Foydalanuvchi ma'lumotlari:\n"
        f"• ID: {user.id}\n"
        f"• Username: {username}\n"
        f"• Ism: {first_name}\n"
        f"• Familiya: {last_name}\n"
        f"• Tanlagan til: {lang_display}\n\n"
        f"💬 Xabar turi: {message.content_type}\n"
        f"📅 Sana: {message.date.strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        f"📝 Xabar matni:"
    )

    # Adminlarga yuborish
    for admin_id in ADMIN_IDS:
        try:
            await bot.send_message(chat_id=admin_id, text=user_info)
            await bot.forward_message(
                chat_id=admin_id,
                from_chat_id=message.chat.id,
                message_id=message.message_id
            )
        except Exception as e:
            logging.error(f"Xabarni admin {admin_id} ga yuborishda xato: {e}")

# Botni ishga tushirish
if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
