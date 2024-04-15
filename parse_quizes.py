import glob
import json
import os
from dotenv import load_dotenv


def parse_block(block_text):
    block = block_text.split(':\n')
    if len(block) >= 2:
        name = block[0]
        short_name = block[0].split(' ')[0]
        text = block[1]
        return (text, name, short_name)
    return (None, None, None)


def parse_quize(quize_text, n, questions):
    current_question = ''
    current_answer = ''
    quize_blocks = quize_text.split('\n\n')
    for block in quize_blocks:
        block_text, name, short_name = parse_block(block)
        if short_name == 'Тур':
            current_question = ''
            current_answer = ''
        elif short_name == 'Вопрос':
            current_question = block_text
        elif short_name == 'Ответ':
            current_answer = block_text

        if current_question != '' and current_answer != '':
            n = n + 1
            questions[f'question_{n}'] = {}
            questions[f'question_{n}']['question'] = current_question
            questions[f'question_{n}']['answer'] = current_answer
            current_question = ''
            current_answer = ''
    return questions, n


def main():
    load_dotenv()
    path_txt = os.environ.get('PATH_QUIZES_TXT')
    path_json = os.environ.get('PATH_QUIZES_JSON')
    n = 0
    questions = {}
    for filename in glob.glob(f"{path_txt}*.txt"):
        with open(filename, "r", encoding='KOI8-R') as original_quiz_file:
            file_contents = original_quiz_file.read()
        questions, n = parse_quize(file_contents, n, questions)

    questions['quantity'] = n
    dir_name = os.path.dirname(f'{path_json}{n}.json')
    if not os.path.exists(dir_name):
        os.mkdir(dir_name)
    with open(f'{path_json}questions.json', 'w') as file:
        json.dump(questions, file)


if __name__ == '__main__':
    main()
