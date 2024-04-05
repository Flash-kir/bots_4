import os
import random
import glob
import json
import redis

from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    Updater,
    CommandHandler,
    CallbackContext,
    MessageHandler,
    Filters,
    ConversationHandler,
)
from dotenv import load_dotenv

load_dotenv()
r = redis.Redis(host='localhost', port=6379, db=0)

QUESTION, SOLUTION, QUIT = range(3)


def get_questions():
    n = random.randint(1, len(glob.glob('json_quizes/*.json')))
    with open(f'json_quizes/{n}.json', 'r') as file:
        quiz = json.loads(file.read())

    questions = []
    for tour in quiz['Tours']:
        for question_name in tour.keys():
            if not question_name == 'name':
                question = tour[question_name]['Вопрос']
                answer = tour[question_name]['Ответ']
                questions.append((question, answer))
    return questions


def set_first_question(questions_list):
    return questions_list.pop(0), questions_list


def start(update: Update, context: CallbackContext):
    """Send a message when the command /start is issued."""
    user = update.effective_user
    context.chat_data['questions'] = get_questions()
    context.chat_data['score'] = 0

    custom_keyboard = [
        ['Новый вопрос', 'Выйти']
    ]
    reply_markup = ReplyKeyboardMarkup(custom_keyboard, resize_keyboard=True)
    context.bot.send_message(
                            chat_id=update.effective_chat.id,
                            text="Привет! Я бот для викторин.",
                            reply_markup=reply_markup,
    )
    return QUESTION


def handle_new_question_request(update: Update, context: CallbackContext):
    user_text = update.message.text
    message_text = ""

    if user_text == "Мой счет":
        message_text = f"Ваш счет {context.chat_data['score']}."
        print(r.get(update.effective_user.id).decode())
        update.message.reply_text(message_text)
        if r.get(update.effective_user.id).decode() == "":
            return QUESTION

    if not context.chat_data['questions']:
        context.chat_data['questions'] = get_questions()

    if user_text == "Новый вопрос" or r.get(update.effective_user.id).decode():
        current, questions_list = set_first_question(
            context.chat_data['questions']
        )
        context.chat_data['questions'] = questions_list
        r.set(update.effective_user.id, current[1])
        print(current[1])
        message_text = current[0]

    if user_text == "Выйти":
        context.chat_data['questions'] = []
        context.chat_data['score'] = 0
        update.message.reply_text("Спасибо за игру! До встречи!")
        return QUIT

    custom_keyboard = [
        ['Мой счет', 'Сдаться'],
        ['Выйти'],
    ]
    reply_markup = ReplyKeyboardMarkup(custom_keyboard, resize_keyboard=True)

    update.message.reply_text(message_text, reply_markup=reply_markup)
    return SOLUTION


def handle_solution_attempt(update: Update, context: CallbackContext):
    user_text = update.message.text
    message_text = ""

    if user_text == "Мой счет":
        message_text = f"Ваш счет {context.chat_data['score']}."
        update.message.reply_text(message_text)
        if r.get(update.effective_user.id).decode() == "":
            return QUESTION

    if user_text == "Сдаться":
        custom_keyboard = [
            ['Новый вопрос'],
            ['Мой счет', 'Выйти']
        ]
        answer = r.get(update.effective_user.id).decode()
        message_text = f"Правильный ответ '{answer}'. Попробуем ещё раз?"
        r.set(update.effective_user.id, "")
        reply_markup = ReplyKeyboardMarkup(
            custom_keyboard,
            resize_keyboard=True
        )

        update.message.reply_text(message_text, reply_markup=reply_markup)
        return QUESTION

    if user_text == r.get(update.effective_user.id).decode():
        custom_keyboard = [
            ['Новый вопрос'],
            ['Мой счет', 'Выйти']
        ]
        message_text = f"Это правильный ответ, поздравляю!!! Ещё вопрос?"
        context.chat_data['score'] = context.chat_data['score'] + 1
        r.set(update.effective_user.id, "")
        reply_markup = ReplyKeyboardMarkup(
            custom_keyboard,
            resize_keyboard=True
        )

        update.message.reply_text(message_text, reply_markup=reply_markup)
        return QUESTION

    if user_text != r.get(update.effective_user.id).decode():
        custom_keyboard = [
            ['Мой счет', 'Сдаться'],
            ['Выйти'],
        ]
        message_text = f"Это неверный ответ, попробуйте снова."
        reply_markup = ReplyKeyboardMarkup(
            custom_keyboard,
            resize_keyboard=True
        )

        update.message.reply_text(message_text, reply_markup=reply_markup)
        return SOLUTION

    if user_text == "Выйти":
        context.chat_data['questions'] = []
        context.chat_data['score'] = 0
        update.message.reply_text("Спасибо за игру! До встречи!")
        return QUIT


def quit(update: Update, context: CallbackContext):
    return ConversationHandler.END


def main():
    telegram_bot_token = os.environ.get('TELEGRAM_BOT_TOKEN')

    updater = Updater(telegram_bot_token)

    dp = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            QUESTION: [
                MessageHandler(Filters.text, handle_new_question_request),
            ],
            SOLUTION: [
                MessageHandler(Filters.text, handle_solution_attempt),
            ],
            QUIT: [
                CommandHandler('end', quit),
            ],
        },
        fallbacks=[CommandHandler('start', start)],
    )
    dp.add_handler(conv_handler)

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
