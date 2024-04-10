import random
import glob
import json


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
