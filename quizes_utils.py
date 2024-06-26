import random
import json


def get_user_context(r, user_id, social_web):
    user_context = r.get(f'user_{social_web}_{user_id}')
    if user_context:
        return json.loads(user_context)
    else:
        return {
            'score': 0,
            'last_asked_question': '',
        }


def set_user_context(r, user_id, social_web, user_context):
    if not user_context:
        user_context = {
            'score': 0,
            'last_asked_question': '',
        }
    r.set(f'user_{social_web}_{user_id}', json.dumps(user_context))
    return user_context


def get_answer(user_id, r, social_web):
    answer = ''
    user_context = get_user_context(r, user_id, social_web)
    if user_context['last_asked_question']:
        question = json.loads(r.get(user_context['last_asked_question']))
        answer = question['answer']
    return answer


def get_score_message(user_id, r, social_web):
    score = 0
    user_context = get_user_context(r, user_id, social_web)
    if user_context['score']:
        score = user_context['score']
    return f'Ваш счет {score}.'


def ask_question_handler(user_id, r, max_question_num, social_web):
    user_context = get_user_context(r, user_id, social_web)
    if user_context['last_asked_question']:
        return 'Вам уже задан вопрос, пожалуйста ответьте на него'

    question_number = random.randint(1, max_question_num)
    question = json.loads(r.get(f'question_{question_number}'))

    user_context['last_asked_question'] = f'question_{question_number}'
    set_user_context(r, user_id, social_web, user_context)
    return question['question']


def check_answer_handler(user_id, r, user_answer, social_web):
    user_context = get_user_context(r, user_id, social_web)

    if not user_context['last_asked_question']:
        return 'Не понимаю о чем Вы.\nНажмите кнопку "Новый вопрос"'

    last_question = json.loads(r.get(user_context['last_asked_question']))

    if user_answer != last_question['answer']:
        return 'К сожалению это не правильный ответ..\nПопробуйте ещё раз.'

    user_context['score'] = user_context['score'] + 1
    user_context['last_asked_question'] = ''
    set_user_context(r, user_id, social_web, user_context)
    return 'Поздравляю, это \
        правильный ответ!\nДля продолжения нажмите кнопку "Новый вопрос"'


def get_resignation_message(user_id, r, social_web):
    message_text = ''
    score_message = get_score_message(user_id, r, social_web)
    answer = get_answer(user_id, r, social_web)
    if answer:
        message_text = f'Правильный ответ: {answer}.\n{score_message}.'
    else:
        message_text = score_message
    user_context = get_user_context(r, user_id, social_web)
    user_context['last_asked_question'] = ''
    set_user_context(r, user_id, social_web, user_context)
    return message_text
