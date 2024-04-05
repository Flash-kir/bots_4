import os
import random
import redis
import glob
import json
import vk_api as vk
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.keyboard import VkKeyboard
from dotenv import load_dotenv


load_dotenv()
r = redis.Redis(host='localhost', port=6379, db=0)


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


def send_answer(event, vk_api, context):
    if event.type == VkEventType.MESSAGE_NEW and event.to_me:
        user_text = event.text
        message_text = ''

        if user_text == 'Сдаться':
            score = context['score']
            if r.get(event.user_id):
                message_text = f'Правильный ответ: {context["current"][1]}.\nСпасибо за игру, ваш счет {score}'
                r.set(event.user_id, "")
            else:
                message_text = f'Спасибо за игру, ваш счет {score}'
                r.set(event.user_id, "")
            context['current'] = None
            context['score'] = 0
            context['question_asked'] = False
        elif context['question_asked'] and context['current']:
            answer = context['current'][1]
            if user_text == answer:
                context['score'] += 1
                message_text = 'Правильно! Для продолжения нажмите "Новый вопрос"'
                context['question_asked'] = False
                context['current'] = None
            else:
                message_text = f'К сожалению это не правильный ответ..\nПопробуйте ещё раз.'
        elif user_text == 'Новый вопрос' and not context['current']:
            if not context['questions']:
                context['questions'] = get_questions()
            current, questions_list = set_first_question(context['questions'])
            context['current'] = current
            context['questions'] = questions_list
            print(current[1])
            message_text = current[0]
            context['question_asked'] = True
            r.set(event.user_id, message_text)
        elif user_text == 'Мой счет':
            score = context['score']
            message_text = f'Ваш счет {score}'

        if message_text == "":
            message_text = "Привет! Я бот, проводящий викторины, приступим?"

        kb = VkKeyboard(one_time=True)
        kb.add_button('Новый вопрос')
        kb.add_button('Сдаться')
        kb.add_line()
        kb.add_button('Мой счет')

        vk_api.messages.send(
            user_id=event.user_id,
            message=message_text,
            keyboard=kb.get_keyboard(),
            random_id=random.randint(1, 1000)
        )


def main():
    vk_session = vk.VkApi(token=os.environ.get('VK_GROUP_TOKEN'))
    vk_api = vk_session.get_api()
    longpoll = VkLongPoll(vk_session)

    context = {}
    context['score'] = 0
    context['questions'] = []
    context['question_asked'] = False
    context['current'] = None

    for event in longpoll.listen():
        send_answer(event, vk_api, context)


if __name__ == '__main__':
    main()
