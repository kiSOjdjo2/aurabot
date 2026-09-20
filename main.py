import asyncio
import io
import logging
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import CommandStart
from aiogram.utils.keyboard import InlineKeyboardBuilder
from google import genai
from PIL import Image

# ==================== ВСТАВЬ СВОИ КЛЮЧИ СЮДА ====================
TELEGRAM_TOKEN = "8819832817:AAHYVCoVfncgJlP9f-VQp2I62kkqer2j3H8"
GEMINI_API_KEY = "AQ.Ab8RN6JyhPRimolqRau74Jc6yF18zWQ57IOfo09KEdT1Uj-4ug"
# ================================================================

logging.basicConfig(level=logging.INFO)

bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher()
ai_client = genai.Client(api_key=GEMINI_API_KEY)

# Подробная инструкция для нейросети
PROMPT = """
Ты — профессиональный AI-стилист и консультант по Glow-Up.
Проанализируй селфи/фотографию человека и дай вежливый, объективный и поддерживающий разбор.

Формат ответа (строго соблюдай структуру и эмодзи):

📸 Твой AuraLook AI Разбор:

🌟 Главные плюсы:
• [Укажи 2-3 сильные стороны: глаза, улыбка, овал лица, волосы, кожа]

🔍 Особенности:
• [Укажи 2 особенности: форма лба, бровей, щек, подбородка]

📈 Общий балл внешности: [Честная оценка от 6.0 до 9.5]/10

💡 Glow-Up Советы (Что можно улучшить):
1. Прическа: [Совет по форме или укладке]
2. Уход/Брови: [Совет по коррекции, уходу за кожей или стилю]
3. Фишка: [Аксессуар, очки или нюанс в стиле]
"""

# Функция создания главного меню с кнопками
def get_main_keyboard():
    builder = InlineKeyboardBuilder()
    builder.button(text="📸 Как сделать идеальное фото", callback_data="guide")
    builder.button(text="💡 Как работает AuraLook AI", callback_data="about")
    builder.adjust(1)
    return builder.as_markup()

# Функция создания кнопки "Заново" после анализа
def get_retry_keyboard():
    builder = InlineKeyboardBuilder()
    builder.button(text="🔄 Оценить другое фото", callback_data="retry")
    return builder.as_markup()

# 1. ОБРАБОТКА КОМАНДЫ /start
@dp.message(CommandStart())
async def cmd_start(message: types.Message):
    await message.answer(
        "👋 Привет! Я AuraLook AI — твой персональный AI-стилист.\n\n"
        "Отправь мне свое селфи или четкое фото лица, и нейросеть за пару секунд:\n"
        "1. Подсветит твои главные плюсы ✨\n"
        "2. Выставит объективную оценку внешности 📊\n"
        "3. Даст 3 практических совета по прическе и уходу 💡\n\n"
        "👇 *Просто отправь фото прямо сейчас или воспользуйся меню:*",
        reply_markup=get_main_keyboard(),
        parse_mode="Markdown"
    )

# 2. ОБРАБОТКА НАЖАТИЙ НА КНОПКИ
@dp.callback_query(F.data == "guide")
async def process_guide(callback: types.CallbackQuery):
    await callback.message.answer(
        "📸 Как сделать фото для лучшего разбора:\n\n"
        "1. Хорошее дневное освещение (напротив окна).\n"
        "2. Лицо прямо в кадр, без сильных фильтров и масок.\n"
        "3. Четкое качество картинки.\n\n"
        "👇 *Жду твое фото!*"
    )
    await callback.answer()

@dp.callback_query(F.data == "about")
async def process_about(callback: types.CallbackQuery):
    await callback.message.answer(
        "💡 О проекте AuraLook AI:\n\n"
        "Бот работает на базе мультимодальной нейросети Google Gemini 1.5 Flash.\n"
        "Она сканирует пропорции лица, волосы, стиль и форму головы, а затем сравнивает их с рекомендациями топовых стилистов.\n\n"
        "👇 *Загружай селфи и проверяй!*"
    )
    await callback.answer()

@dp.callback_query(F.data == "retry")
async def process_retry(callback: types.CallbackQuery):
    await callback.message.answer("📸 *Жду новое фото! Отправляй прямо в чат.*", parse_mode="Markdown")
    await callback.answer()

# 3. ОБРАБОТКА ФОТОГРАФИИ
@dp.message(F.photo)
async def handle_photo(message: types.Message):
    await bot.send_chat_action(chat_id=message.chat.id, action="typing")
    status_msg = await message.answer("🔍 *AuraLook AI сканирует пропорции лица... Подожди 3-5 секунд* ⏳", parse_mode="Markdown")

    try:
        photo = message.photo[-1]
        file_info = await bot.get_file(photo.file_id)
        photo_bytes = await bot.download_file(file_info.file_path)
        image = Image.open(io.BytesIO(photo_bytes.read()))

        response = ai_client.models.generate_content(
            model='gemini-1.5-flash',
            contents=[PROMPT, image]
        )

        await status_msg.delete()
        await message.answer(response.text, reply_markup=get_retry_keyboard(), parse_mode="Markdown")

    except Exception as e:
        logging.error(f"Ошибка при обработке фото: {e}")
        await status_msg.edit_text("❌ Ошибка при анализе фото. Попробуй отправить другое четкое селфи!")

# 4. ЗАПУСК БОТА
async def main():
    print("🚀 AuraLook AI Бот успешно запущен и готов к работе!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())