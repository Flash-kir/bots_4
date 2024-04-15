import os
import random
import redis
import json
import vk_api as vk

from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.keyboard import VkKeyboard
from dotenv import load_dotenv
from quizes_utils import get_questions
from quizes_utils import check_user_context
from quizes_utils import set_question
from quizes_utils import get_resignation_message
from quizes_utils import get_new_question
from quizes_utils import get_score_message
from quizes_utils import check_answer


def send_message(user_id, vk_api, text, kb):
    vk_api.messages.send(
        user_id=user_id,
        message=text,
        keyboard=kb.get_keyboard(),
        random_id=random.randint(1, 1000)
    )


def catch_message(event, vk_api, kb, r, max_question_num, social_web):
    user_text = event.text
    message_text = ''

    check_user_context(event.user_id, r, social_web)
    
    if user_text == 'Сдаться':
        message_text = get_resignation_message(event.user_id, r, social_web)
    elif user_text == 'Новый вопрос':
        message_text = get_new_question(event.user_id, r, max_question_num, social_web)
    elif user_text == 'Мой счет':
        message_text = get_score_message(event.user_id, r, social_web)
    else:
        message_text = check_answer(event.user_id, r, user_text, social_web)

    if message_text == '':
        message_text = 'Привет! Я бот, проводящий викторины, приступим?'

    send_message(event.user_id, vk_api, message_text, kb)


def main():
    load_dotenv()
    r = redis.Redis(
        host=os.environ.get('REDIS_HOST', default='localhost'),
        port=os.environ.get('REDIS_PORT', default=6379),
        db=0
    )
    
    questions, max_question_num = get_questions(os.environ.get('PATH_QUIZES_JSON'))
    for i in range(max_question_num):
        set_question(r, i+1, questions[f'question_{i+1}'])

    vk_session = vk.VkApi(token=os.environ.get('VK_GROUP_TOKEN'))
    vk_api = vk_session.get_api()
    longpoll = VkLongPoll(vk_session)

    kb = VkKeyboard(one_time=True)
    kb.add_button('Новый вопрос')
    kb.add_button('Сдаться')
    kb.add_line()
    kb.add_button('Мой счет')

    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
            catch_message(event, vk_api, kb, r, max_question_num, 'vk')


if __name__ == '__main__':
    main()
