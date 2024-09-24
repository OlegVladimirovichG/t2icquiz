import random
import logging
from aiogram import types

# Настройка логирования для записи только результатов
logging.basicConfig(filename='quiz_results.log', level=logging.INFO, format='%(asctime)s - %(message)s')


class QuizManager:
    def __init__(self, questions, admin_chat_id):
        self.questions = questions
        self.used_questions = []
        self.current_question = None
        self.correct_answer = None
        self.waiting_for_answer = False
        self.score = 0
        self.question_index = 0
        self.quiz_questions = []
        self.user_sessions = set()  # Хранение уникальных пользователей
        self.usage_count = 0  # Количество обращений
        self.quiz_completed = 0  # Количество завершённых викторин
        self.admin_chat_id = admin_chat_id  # ID для отправки сообщений админу

    def refresh_questions(self):
        """Перезагружает вопросы, если осталось меньше 10 вопросов"""
        if len(self.questions) < 10:
            # Если в списке осталось меньше 10 вопросов, восстанавливаем использованные вопросы
            self.questions.extend(self.used_questions)
            self.used_questions.clear()

    def start_new_quiz(self):
        # Обновляем список вопросов, если их осталось меньше 10
        self.refresh_questions()

        # Выбираем 10 случайных уникальных вопросов для новой викторины
        self.quiz_questions = random.sample(self.questions, 10)

        # Добавляем эти вопросы в список использованных
        self.used_questions.extend(self.quiz_questions)

        # Удаляем выбранные вопросы из основного списка
        self.questions = [q for q in self.questions if q not in self.quiz_questions]

        self.score = 0
        self.question_index = 0
        logging.info("Новая викторина начата")

    def is_waiting_for_answer(self):
        return self.waiting_for_answer

    async def start_quiz(self, message: types.Message, bot):
        self.user_sessions.add(message.from_user.id)  # Добавляем пользователя в список уникальных пользователей
        self.usage_count += 1  # Увеличиваем количество обращений
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

            # Отправка результата админу
            await bot.send_message(chat_id=self.admin_chat_id,
                                   text=f"Пользователь {message.from_user.id} завершил викторину с результатом {self.score} из 10.")

            # Анонс функции "Начать сначала"
            await message.answer("Вы можете начать викторину заново, нажав на кнопку 'Начать сначала'.")

            # Увеличиваем счетчик завершённых викторин
            self.quiz_completed += 1

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

    async def send_daily_report(self, bot, chat_id):
        """Отправка ежедневного отчета в 22:00"""
        message = f"Сегодня ботом пользовались {self.usage_count} раз, {len(self.user_sessions)} уникальных пользователей, завершено {self.quiz_completed} викторин."
        await bot.send_message(chat_id=chat_id, text=message)
