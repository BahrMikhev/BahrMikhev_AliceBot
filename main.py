# импортируем библиотеки
from flask import Flask, request
import logging
import os
# библиотека, которая нам понадобится для работы с JSON
import json
from data import db_session
from data.users import User

app = Flask(__name__)

# Устанавливаем уровень логирования
logging.basicConfig(level=logging.INFO)

sessionStorage = {}
state = 'menu'
logged = False
id_ = None

@app.route('/post', methods=['POST'])
# Функция получает тело запроса и возвращает ответ.
# Внутри функции доступен request.json - это JSON,
# который отправила нам Алиса в запросе POST
def main():
    logging.info(f'Request: {request.json!r}, state: {state}')
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
    handle_dialog(request.json, response)

    logging.info(f'Response:  {response!r}, state: {state}')

    # Преобразовываем в JSON и возвращаем
    return json.dumps(response)


def handle_dialog(req, res):
    user_id = req['session']['user_id']
    if state == 'menu':
        main_menu(user_id, res, req, False)
    elif state == 'new':
        new_game(user_id, res, req, False)
    elif state == 'virtual':
        gameplay_virtual(user_id, res, req, False)
    elif state == 'paper':
        gameplay_paper(user_id, res, req, False)
    elif state == 'auth':
        auth(user_id, res, req, False)
    elif state == 'scores':
        highscores(user_id, res, req, False)
    elif state == 'help':
        help(user_id, res, req, False)
    logging.info(f"RESPONSE handle_2 TEXT: {res['response']['text']}")



def main_menu(user_id, res, req, called):
    global state
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
        # Кнопки
        suggests = [
            {'title': suggest, 'hide': True}
            for suggest in sessionStorage[user_id]['suggests']
        ]
        res['response']['buttons'] = suggests
    elif req['request']['original_utterance'].lower() in ['новая игра', 'играть', 'сыграем']:
        state = 'new'
        new_game(user_id, res, req, True)
        logging.info(f"RESPONSE menu TEXT: {res['response']['text']}")
        return
    elif req['request']['original_utterance'].lower() in ['авторизация', 'логин', 'войти']:
        state = 'auth'
        auth(user_id, res, req, True)
        return
    elif req['request']['original_utterance'].lower() == 'рекорды':
        state = 'scores'
        highscores(user_id, res, req, True)
        return
    elif req['request']['original_utterance'].lower() in ['помощь', 'помоги', 'что делать']:
        state = 'help'
        help(user_id, res, req, True)
        return
    else:
        res['response']['text'] = 'Что вы хотите сделать?'
        suggests = [
            {'title': suggest, 'hide': True}
            for suggest in sessionStorage[user_id]['suggests']
        ]
        res['response']['buttons'] = suggests

def new_game(user_id, res, req, called):
    global state
    if called:
        sessionStorage[user_id] = {
            'suggests': [
                "Игра на бумаге",
                "Игра без бумаги",
                "Назад",
            ]
        }
        # Заполняем текст ответа
        res['response']['text'] = '''Для того, чтобы начать новую игру выбери один из режимов:
                                     игра на листе бумаги, или на экране телефона'''
        logging.info(f"RESPONSE TEXT: {res['response']['text']}")
        # Кнопки
        suggests = [
            {'title': suggest, 'hide': True}
            for suggest in sessionStorage[user_id]['suggests']
        ]
        res['response']['buttons'] = suggests
        logging.info(f"RESPONSE new TEXT: {res['response']['text']}")
        return
    if req['request']['original_utterance'].lower() == 'игра на бумаге':
        state = 'paper'
        gameplay_paper(user_id, res, req, True)
        return
    elif req['request']['original_utterance'].lower() == 'игра без бумаги':
        state = 'virtual'
        gameplay_virtual(user_id, res, req, True)
        return
    elif req['request']['original_utterance'].lower() == 'назад':
        state = 'menu'
        main_menu(user_id, res, req, True)
        return
    else:
        res['response']['text'] = 'Что вы хотите сделать?'
        suggests = [
            {'title': suggest, 'hide': True}
            for suggest in sessionStorage[user_id]['suggests']
        ]
        res['response']['buttons'] = suggests


def gameplay_virtual(user_id, res, req, called):
    global state
    if called:
        res['response']['text'] = 'Виртуальная игра!'
        return
    if req['request']['original_utterance'].lower() == 'назад':
        state = 'menu'
        main_menu(user_id, res, req, True)
        return
    else:
        res['response']['text'] = 'Что вы хотите сделать?'

def gameplay_paper(user_id, res, req, called):
    global state
    if called:
        res['response']['text'] = 'Игра на бумаге'
        return
    if req['request']['original_utterance'].lower() == 'назад':
        state = 'menu'
        main_menu(user_id, res, req, True)
        return
    else:
        res['response']['text'] = 'Что вы хотите сделать?'

def auth(user_id, res, req, called):
    global state
    if not logged:
        if called:
            res['response']['text'] = 'Назовите своё имя'
            return
    else:
        session = db_session.create_session()
        find_id = [user.name for user in session.query(User).filter((User.id == id_))]
        username = find_id[0]
        res['response']['text'] = f'Вы уже вошли в аккаунт как {username}'
        sessionStorage[user_id] = {
            'suggests': [
                "Выйти из аккаунта",
                "Назад",
            ]
        }
        # Кнопки
        suggests = [
            {'title': suggest, 'hide': True}
            for suggest in sessionStorage[user_id]['suggests']
        ]
        res['response']['buttons'] = suggests

        if req['request']['original_utterance'].lower() in ['выйти из аккаунта', 'выйти']:
            logged = False
            id_ = -1
            state = 'menu'
            return
        elif req['request']['original_utterance'].lower() == 'назад':
            state = 'menu'
            return
        else:
            res['response']['text'] = 'Что вы хотите сделать?'
            suggests = [
                {'title': suggest, 'hide': True}
                for suggest in sessionStorage[user_id]['suggests']
            ]
            res['response']['buttons'] = suggests

def highscores(user_id, res, req, called):
    global state
    if called:
        res['response']['text'] = 'Рекорды'
    if req['request']['original_utterance'].lower() == 'назад':
        state = 'menu'
        main_menu(user_id, res, req, True)
        return
    else:
        res['response']['text'] = 'Что вы хотите сделать?'
        suggests = [
            {'title': suggest, 'hide': True}
            for suggest in sessionStorage[user_id]['suggests']
        ]
        res['response']['buttons'] = suggests

def help(user_id, res, req, called):
    global state
    if called:
        res['response']['text'] = '''В игре "морской бой" вам необходимо уничтожить вражескую флотилию за как можно меньшее количество ходов.
                                     В игре без бумаги вам необходимо вначале расставить корабли на виртуальном поле, называя координату, количество палуб и ориентацию корабля (вверх, вниз, вправо, влево). Однопалубные корабли ориентировать не нужно.
                                     Так же в этом режиме вам не требуется смотреть за попаданиями в ваши корабли.
                                     Приятной игры!'''
        sessionStorage[user_id] = {
            'suggests': [
                "Назад",
            ]
        }
        # Кнопки
        logging.info(f"RESPONSE TEXT: {res['response']['text']}")
        suggests = [
            {'title': suggest, 'hide': True}
            for suggest in sessionStorage[user_id]['suggests']
        ]
        res['response']['buttons'] = suggests
        return
    if req['request']['original_utterance'].lower() == 'назад':
        state = 'menu'
        main_menu(user_id, res, req, True)
        return
    else:
        res['response']['text'] = 'Что вы хотите сделать?'
        suggests = [
            {'title': suggest, 'hide': True}
            for suggest in sessionStorage[user_id]['suggests']
        ]
        res['response']['buttons'] = suggests


def get_first_name(req):
    # перебираем сущности
    for entity in req['request']['nlu']['entities']:
        # находим сущность с типом 'YANDEX.FIO'
        if entity['type'] == 'YANDEX.FIO':
            # Если есть сущность с ключом 'first_name', то возвращаем её значение.
            # Во всех остальных случаях возвращаем None.
            return entity['value'].get('first_name', None)

if __name__ == '__main__':
    if "PORT" in os.environ:
        app.run(host='0.0.0.0', port=os.environ["PORT"])
    else:
        app.run(host='127.0.0.1', port=5000)