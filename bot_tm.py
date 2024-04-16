import os
import redis
import json
from functools import partial


from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    Updater,
    CommandHandler,
    CallbackContext,
    MessageHandler,
    Filters,
    ConversationHandler,
    RegexHandler,
)
from dotenv import load_dotenv
from quizes_utils import get_questions
from quizes_utils import check_user_context
from quizes_utils import get_resignation_message
from quizes_utils import get_new_question
from quizes_utils import get_score_message
from quizes_utils import check_answer
from quizes_utils import clear_user_context


QUESTION, GAME = range(2)


def send_sessage(update: Update, message_text):
    custom_keyboard = [
        ['Мой счет', 'Сдаться'],
        ['Новый вопрос', 'Выйти']
    ]
    reply_markup = ReplyKeyboardMarkup(custom_keyboard, resize_keyboard=True)

    update.message.reply_text(message_text, reply_markup=reply_markup)


def start(update: Update, context: CallbackContext, r):
    user = update.effective_user
    check_user_context(user.id, r, 'tm')
    message_text = 'Привет! Я бот для викторин.'

    send_sessage(update, message_text)
    return GAME


def ask_new_question(update: Update, context: CallbackContext, r):
    user = update.effective_user
    max_question_num = int(r.get('max_question_num'))
    message_text = get_new_question(user.id, r, max_question_num, 'tm')

    send_sessage(update, message_text)
    return GAME


def handle_answer(update: Update, context: CallbackContext, r):
    user = update.effective_user
    user_text = update.message.text
    message_text = check_answer(user.id, r, user_text, 'tm')

    send_sessage(update, message_text)
    return GAME


def score(update: Update, context: CallbackContext, r):
    user = update.effective_user
    message_text = get_score_message(user.id, r, 'tm')

    send_sessage(update, message_text)
    return GAME


def resign(update: Update, context: CallbackContext, r):
    user = update.effective_user
    message_text = get_resignation_message(user.id, r, 'tm')

    send_sessage(update, message_text)
    return GAME


def quit(update: Update, context: CallbackContext, r):
    update.message.reply_text("Спасибо за игру! До встречи!")
    user = update.effective_user
    clear_user_context(user.id, r, 'tm')
    return ConversationHandler.END


def main():
    load_dotenv()
    r = redis.Redis(
        host=os.environ.get('REDIS_HOST', default='localhost'),
        port=os.environ.get('REDIS_PORT', default=6379),
        db=0
    )
    telegram_bot_token = os.environ.get('TELEGRAM_BOT_TOKEN')

    questions, max_question_num = get_questions(
        os.environ.get('PATH_QUIZES_JSON')
    )
    r.set('max_question_num', max_question_num)
    for i in range(max_question_num):
        r.set(f'question_{i+1}', json.dumps(questions[f'question_{i+1}']))

    redis_start = partial(start, r=r)
    redis_ask_question = partial(ask_new_question, r=r)
    redis_score = partial(score, r=r)
    redis_resign = partial(resign, r=r)
    redis_quit = partial(quit, r=r)
    redis_handle_answer = partial(handle_answer, r=r)

    updater = Updater(telegram_bot_token)
    dp = updater.dispatcher
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', redis_start)],
        states={
            GAME: [
                RegexHandler('^' + 'Новый вопрос' + '$', redis_ask_question),
                RegexHandler('^' + 'Мой счет' + '$', redis_score),
                RegexHandler('^' + 'Сдаться' + '$', redis_resign),
                RegexHandler('^' + 'Выйти' + '$', redis_quit),
                MessageHandler(Filters.text, redis_handle_answer),
            ],
        },
        fallbacks=[CommandHandler('start', start)],
    )
    dp.add_handler(conv_handler)

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
