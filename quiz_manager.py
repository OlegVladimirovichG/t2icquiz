import random
import logging
from aiogram import types

# Настройка логирования для записи только результатов
logging.basicConfig(filename='quiz_results.log', level=logging.INFO, format='%(asctime)s - Результат: %(message)s')


class QuizManager:
    def __init__(self, questions):
        self.questions = questions
        self.current_question = None
        self.correct_answer = None
        self.waiting_for_answer = False
        self.score = 0
        self.question_index = 0
        self.quiz_questions = []

    def start_new_quiz(self):
        # Сбрасываем данные и выбираем 10 случайных вопросов для новой викторины
        self.quiz_questions = random.sample(self.questions, 10)
        self.score = 0
        self.question_index = 0

    def is_waiting_for_answer(self):
        return self.waiting_for_answer

    async def start_quiz(self, message: types.Message, bot):
        self.start_new_quiz()
        await self.ask_next_question(message, bot)

    async def ask_next_question(self, message: types.Message, bot):
        if self.question_index < len(self.quiz_questions):
            # Выбираем текущий вопрос
            question_data = self.quiz_questions[self.question_index]
            self.current_question = question_data['question']
            self.correct_answer = question_data['answer']
            question_number = self.question_index + 1
            total_questions = len(self.quiz_questions)

            if question_data['type'] == 'multiple_choice':
                # Вопрос с вариантами ответа
                markup = types.ReplyKeyboardMarkup(
                    keyboard=[[types.KeyboardButton(text=option)] for option in question_data['options']],
                    resize_keyboard=True
                )
                await message.answer(f"Вопрос {question_number} из {total_questions}: {self.current_question}",
                                     reply_markup=markup)
            else:
                # Вопрос с текстовым ответом
                markup = types.ReplyKeyboardRemove()
                await message.answer(f"Вопрос {question_number} из {total_questions}: {self.current_question}",
                                     reply_markup=markup)

            self.waiting_for_answer = True
        else:
            # Все вопросы заданы, выводим результат
            markup = types.ReplyKeyboardMarkup(
                keyboard=[[types.KeyboardButton(text="Начать сначала")]],
                resize_keyboard=True
            )
            await message.answer(f"Викторина завершена! Ваш результат: {self.score} из 10.", reply_markup=markup)

            # Запись результата в лог-файл
            logging.info(f"{self.score} из 10")
            self.waiting_for_answer = False

    async def check_answer(self, message: types.Message, bot):
        user_answer = message.text.strip()

        if user_answer.lower() == self.correct_answer.lower():
            self.score += 1
            await message.answer("Правильно!")
        else:
            await message.answer(f"Неправильно. Правильный ответ: {self.correct_answer}")

        # Переходим к следующему вопросу
        self.waiting_for_answer = False
        self.question_index += 1
        await self.ask_next_question(message, bot)
