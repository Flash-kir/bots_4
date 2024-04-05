import glob
import json
import os


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
    quiz_fields = [
        'Чемпионат',
        'URL',
        'Дата',
        'Редактор',
        'Инфо',
        'Автор',
    ]
    question_fields = [
        'Ответ',
        'Комментарий',
        'Источник',
        'Автор',
        'Зачет'
    ]
    current_tour = {}
    current_question = ''
    quize_blocks = quize_text.split('\n\n')
    for block in quize_blocks:
        (block_text, name, short_name) = parse_block(block)
#        print((block_text, name, short_name))
        if short_name in quiz_fields and not current_tour:
            quiz[name] = block_text
        elif short_name == 'Тур':
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
        elif short_name in question_fields:
            if not current_question:
                current_question = 'Вопрос'
                current_tour[current_question] = {
                    'Вопрос': '',
                }
            current_tour[current_question][name] = block_text
    if current_tour:
        quiz['Tours'].append(current_tour)
    return quiz


def create_quizes_json():
    n = 1
    quizes = {}
    for filename in glob.glob("quizes/*.txt"):
        if n >= 1:
            with open(filename, "r", encoding='KOI8-R') as my_file:
                file_contents = my_file.read()
            print(n, filename)
            quizes[filename] = parse_quize(file_contents)
            with open(f'json_quizes/{n}.json', 'w') as file:
                json.dump(quizes[filename], file)
            n += 1
        else:
            break


def main():
    create_quizes_json()


if __name__ == '__main__':
    main()
