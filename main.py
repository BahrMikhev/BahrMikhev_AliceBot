# импортируем библиотеки
from flask import Flask, request
import logging
import os
# библиотека, которая нам понадобится для работы с JSON
import json

# создаём приложение
# мы передаём __name__, в нем содержится информация,
# в каком модуле мы находимся.
# В данном случае там содержится '__main__',
# так как мы обращаемся к переменной из запущенного модуля.
# если бы такое обращение, например,
# произошло внутри модуля logging, то мы бы получили 'logging'
app = Flask(__name__)

# Устанавливаем уровень логирования
logging.basicConfig(level=logging.INFO)

# Создадим словарь, чтобы для каждой сессии общения
# с навыком хранились подсказки, которые видел пользователь.
# Это поможет нам немного разнообразить подсказки ответов
# (buttons в JSON ответа).
# Когда новый пользователь напишет нашему навыку,
# то мы сохраним в этот словарь запись формата
# sessionStorage[user_id] = {'suggests': ["Не хочу.", "Не буду.", "Отстань!" ]}
# Такая запись говорит, что мы показали пользователю эти три подсказки.
# Когда он откажется купить слона,
# то мы уберем одну подсказку. Как будто что-то меняется :)
sessionStorage = {}
state = 'menu'

@app.route('/post', methods=['POST'])
# Функция получает тело запроса и возвращает ответ.
# Внутри функции доступен request.json - это JSON,
# который отправила нам Алиса в запросе POST
def main():
    logging.info(f'Request: {request.json!r}')
    # Начинаем формировать ответ, согласно документации
    # мы собираем словарь, который потом при помощи
    # библиотеки json преобразуем в JSON и отдадим Алисе
    response = {
        'session': request.json['session'],
        'version': request.json['version'],
        'response': {
            'end_session': False
        }
    }

    # Отправляем request.json и response в функцию handle_dialog.
    # Она сформирует оставшиеся поля JSON, которые отвечают
    # непосредственно за ведение диалога
    print(request.json, response, state)
    handle_dialog(request.json, response, state)

    logging.info(f'Response:  {response!r}')

    # Преобразовываем в JSON и возвращаем
    return json.dumps(response)


def handle_dialog(req, res):
    user_id = req['session']['user_id']

    if state == 'menu':
        main_menu(user_id, res, req)

    if state == 'virtual':
        gameplay_virtual(user_id, res, req)

    if state == 'paper':
        gameplay_paper(user_id, res, req)

    if state == 'auth':
        auth(user_id, res, req)

    if state == 'scores':
        highscores(user_id, res, req)

    if state == 'help':
        highscores(user_id, res, req)




def main_menu(user_id, res, req):
    sessionStorage[user_id] = {
        'suggests': [
            "Новая игра",
            "Авторизация",
            "Рекорды",
            "Помощь",
        ]
    }
    # Заполняем текст ответа
    if req['session']['new']:
        res['response']['text'] = 'Привет! Давай поиграем в морской бой!'
    # Получим подсказки
        res['response']['buttons'] = sessionStorage[user_id]
    print(req, res, state)
    if req['request']['original_utterance'].lower() in ['новая игра', 'играть', 'сыграем']:
        state == 'new'
        return
    if req['request']['original_utterance'].lower() in ['авторизация', 'логин', 'войти']:
        state == 'auth'
        return
    if req['request']['original_utterance'].lower() == 'рекорды':
        state == 'scores'
        return
    if req['request']['original_utterance'].lower() in ['помощь', 'помоги', 'что делать']:
        state == 'help'
        return

def new_game(user_id, res, req):
    pass

def gameplay_virtual(user_id, res, req):
    pass

def gameplay_paper(user_id, res, req):
    pass

def auth(user_id, res, req):
    pass

def highscores(user_id, res, req):
    pass

def help(user_id, res, req):
    pass

if __name__ == '__main__':
    if "PORT" in os.environ:
        app.run(host='0.0.0.0', port=os.environ["PORT"])
    else:
        app.run(host='127.0.0.1', port=5000)