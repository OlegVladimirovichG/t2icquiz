import json
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram import F
import asyncio

from config import TOKEN
from quiz_manager import QuizManager

# Загрузка вопросов из JSON файла
with open('quiz_data.json', 'r', encoding='utf-8') as f:
    quiz_data = json.load(f)

bot = Bot(token=TOKEN)
dp = Dispatcher()

# Инициализация QuizManager с набором вопросов из файла
quiz_manager = QuizManager(quiz_data)

# Обработчик команды /start
@dp.message(Command("start"))
async def start_quiz(message: types.Message):
    await message.answer("Привет! Добро пожаловать в викторину. Давайте начнем!")
    await quiz_manager.start_quiz(message, bot)

# Обработчик ответа и кнопки "Начать сначала"
@dp.message(F.text)
async def handle_answer(message: types.Message):
    if message.text == "Начать сначала":
        await start_quiz(message)
    elif quiz_manager.is_waiting_for_answer():
        await quiz_manager.check_answer(message, bot)

# Запуск бота
async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
