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


def parse_quize(quize_text):
    quiz = {
        'Tours': [],
    }
    current_tour = {}
    current_question = ''
    quize_blocks = quize_text.split('\n\n')
    for block in quize_blocks:
        block_text, name, short_name = parse_block(block)
        if short_name == 'Тур':
            if current_tour:
                quiz['Tours'].append(current_tour)
            current_tour = {
                'name': block_text,
            }
            current_question = ''
        elif short_name == 'Вопрос':
            current_tour[name] = {
                'Вопрос': block_text,
            }
            current_question = name
        elif short_name == 'Ответ':
            if not current_question:
                current_question = 'Вопрос'
                current_tour[current_question] = {
                    'Вопрос': '',
                }
            current_tour[current_question][name] = block_text

    if current_tour:
        quiz['Tours'].append(current_tour)
    return quiz


def main():
    load_dotenv()
    path_txt = os.environ.get('PATH_QUIZES_TXT')
    path_json = os.environ.get('PATH_QUIZES_JSON')
    n = 1
    quizes = {}
    for filename in glob.glob(f"{path_txt}*.txt"):
        if n >= 1:
            with open(filename, "r", encoding='KOI8-R') as my_file:
                file_contents = my_file.read()
            quizes[filename] = parse_quize(file_contents)

            dir_name = os.path.dirname(f'{path_json}{n}.json')
            if not os.path.exists(dir_name):
                os.mkdir(dir_name)
            with open(f'{path_json}{n}.json', 'w') as file:
                json.dump(quizes[filename], file)
            n += 1
        else:
            break


if __name__ == '__main__':
    main()
