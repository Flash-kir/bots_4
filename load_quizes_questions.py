import glob
import json
import os
import redis
from dotenv import load_dotenv


def parse_block(block_text):
    block = block_text.split(':\n')
    if len(block) >= 2:
        name = block[0]
        short_name = block[0].split(' ')[0]
        text = block[1]
        return (text, name, short_name)
    return (None, None, None)


def load_quize(quize_text, n, r):
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
            question = {}
            question['question'] = current_question
            question['answer'] = current_answer
            r.set(f'question_{n}', json.dumps(question))
            current_question = ''
            current_answer = ''
    return n


def main():
    load_dotenv()
    r = redis.Redis(
        host=os.environ.get('REDIS_HOST', default='localhost'),
        port=os.environ.get('REDIS_PORT', default=6379),
        db=0
    )

    path_txt = os.environ.get('PATH_QUIZES_TXT')
    n = 0
    for filename in glob.glob(f"{path_txt}*.txt"):
        with open(filename, "r", encoding='KOI8-R') as original_quiz_file:
            file_contents = original_quiz_file.read()
        n = load_quize(file_contents, n, r)

    r.set('max_question_num', n)


if __name__ == '__main__':
    main()
