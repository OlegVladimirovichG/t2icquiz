import json
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from quiz_manager import QuizManager
from config import TOKEN

# Загрузка вопросов из JSON файла
with open('quiz_data.json', 'r', encoding='utf-8') as f:
    quiz_data = json.load(f)

# Инициализация бота и диспетчера
bot = Bot(token=TOKEN)
dp = Dispatcher()
#lol
# Укажите свой Telegram chat_id, куда будет отправляться статистика после каждой викторины
ADMIN_CHAT_ID = "1222943667"

# Инициализация QuizManager с набором вопросов из файла
quiz_manager = QuizManager(quiz_data, admin_chat_id=1222943667)

# Инициализация планировщика задач
scheduler = AsyncIOScheduler()

# Команда для начала викторины
@dp.message(Command("start"))
async def start_quiz(message: types.Message):
    await message.answer("Привет! Добро пожаловать в викторину. Давайте начнем!")
    await quiz_manager.start_quiz(message, bot)

# Обработчик ответов и кнопки "Начать сначала"
@dp.message(lambda message: True)
async def handle_answer(message: types.Message):
    if message.text == "Начать сначала":
        await start_quiz(message)
    elif quiz_manager.is_waiting_for_answer():
        await quiz_manager.check_answer(message, bot)

# Ежедневная отправка отчета в 22:00
async def send_daily_report():
    await quiz_manager.send_daily_report(bot, chat_id=1222943667)

# Планировщик на ежедневное выполнение задачи в 22:00
scheduler.add_job(send_daily_report, 'cron', hour=22, minute=0)
scheduler.start()

# Основной цикл бота
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
