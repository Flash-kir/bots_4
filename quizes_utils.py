import random
import json


def get_questions(path):
    questions = {}
    with open(f'{path}questions.json', 'r') as file:
        questions = json.loads(file.read())

    return questions, questions['quantity']


def get_user_context(r, user_id, social_web):
    user_context = r.get(f'user_{social_web}_{user_id}')
    if user_context:
        return json.loads(user_context)
    else:
        return {
            'score': 0,
            'last_asked_question': '',
            'asked_questions': [],
        }


def set_user_context(r, user_id, social_web, user_context):
    if not user_context:
        user_context = {
            'score': 0,
            'last_asked_question': '',
            'asked_questions': [],
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


def get_question_number(max_num, asked_questions):
    if max_num == len(asked_questions):
        return None
    while True:
        number = random.randint(1, max_num)
        if number not in asked_questions:
            return number


def ask_question_handler(user_id, r, max_question_num, social_web):
    message = ''
    user_context = get_user_context(r, user_id, social_web)
    if user_context:
        if user_context['last_asked_question']:
            message = 'Вам уже задан вопрос, пожалуйста ответьте на него'
        else:
            question_number = get_question_number(
                max_question_num,
                user_context['asked_questions']
            )
            if question_number:
                question = json.loads(r.get(f'question_{question_number}'))
                message = question['question']
                user_context['last_asked_question'] = f'question_{question_number}'
                user_context['asked_questions'].append(question_number)
                set_user_context(r, user_id, social_web, user_context)
            else:
                score_message = get_score_message(user_id, r, social_web)
                message = f'Поздравляем, вы ответили на все \
                    вопросы.\n{score_message}\nВикторина начнется заново.'
                set_user_context(r, user_id, social_web, None)
    return message


def check_answer_handler(user_id, r, user_answer, social_web):
    message = ''
    user_context = get_user_context(r, user_id, social_web)
    if user_context:
        if user_context['last_asked_question']:
            last_question = json.loads(r.get(user_context['last_asked_question']))
            if user_answer == last_question['answer']:
                message = 'Поздравляю, это \
                    правильный ответ!\nДля продолжения нажмите кнопку "Новый вопрос"'
                user_context['score'] = user_context['score'] + 1
                user_context['last_asked_question'] = ''
                set_user_context(r, user_id, social_web, user_context)
            else:
                message = 'К сожалению это не правильный ответ..\nПопробуйте ещё раз.'
        else:
            message = 'Не понимаю о чем Вы.\nНажмите кнопку "Новый вопрос"'
    return message


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
