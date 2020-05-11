# импортируем библиотеки
from flask import Flask, request
import logging
import os
# библиотека, которая нам понадобится для работы с JSON
import json
from data import db_session
from data.users import User
import hashlib
from sea_battle import *
from sea_war_strategies import genesis
app = Flask(__name__)

# Устанавливаем уровень логирования
logging.basicConfig(level=logging.INFO)

gsum = 20
csum = 20
g_power = None
c_power = None

user_field = ['a1d', 'a3d', 'a5d', 'a7d', 'c1r', 'c3r', 'c5r', 'c7r', 'a9r', 'g3d']
computer_field = None
g_field = None
c_field = None
sessionStorage = {}
firstname = None
state = 'menu'
auth_pos = 0
logged = False
pass_1 = None
pass_2 = None
id_ = None
move = None

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
    elif state == 'placement':
        ship_placement(user_id, res, req, False)
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
        state = 'placement'
        ship_placement(user_id, res, req, True)
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
    global user_field, computer_field, g_field, c_field, move, csum, gsum, c_power, g_power
    message = list()
    correct = False
    def let(s):
        s = s.lower()
        try:
            a = ord(s[0]) - ord('a')
            if (a < 10 and a >= 0):
                return a
            else:
                return 'none'
        except:
            return 'none'

    def num(s):
        s = s.lower()
        try:
            a = int(s[-1])
        except:
            s = s[0:-1]
        try:
            a = int(s[1:]) - 1
            if (a < 10 and a >= 0):
                return a
            else:
                return 'none'
        except:
            return 'none'

    def null_field():
        field = []
        for i in range(10):
            field.append([])
            for j in range(10):
                field[i].append(0)
        return field

    def sowing(ship_list):
        field = null_field()
        for i in range(10):
            field[let(ship_list[i])][num(ship_list[i])] = i + 1
        for i in [4, 5, 6, 7, 8, 9]:
            if (ship_list[i][-1] == 'r'):
                field[let(ship_list[i]) + 1][num(ship_list[i])] = i + 1
            else:
                field[let(ship_list[i])][num(ship_list[i]) + 1] = i + 1
        for i in [7, 8, 9]:
            if (ship_list[i][-1] == 'r'):
                field[let(ship_list[i]) + 2][num(ship_list[i])] = i + 1
            else:
                field[let(ship_list[i])][num(ship_list[i]) + 2] = i + 1
        for i in [10]:
            if (ship_list[9][-1] == 'r'):
                field[let(ship_list[9]) + 3][num(ship_list[9])] = 10
            else:
                field[let(ship_list[9])][num(ship_list[9]) + 3] = 10
        return field

    def check_move(field, code):
        if (let(code) == 'none' or num(code) == 'none'):
            return 'incorrect'
        elif (field[let(code)][num(code)] >= 100):
            return 'shot'
        else:
            return 'clear'

    def input_code(field):
        input_code = req['request']['original_utterance']
        check = check_move(field, input_code)
        if (check == 'incorrect'):
            message.append('Некорректный ход')
        elif (check == 'shot'):
            message.append('Вы сюда уже стреляли')
        else:
            correct = True
        return input_code, message

    def generate_code(field):
        while True:
            ran_let = randint(0, 9)
            ran_num = randint(0, 9)
            gen_code = (chr(65 + ran_let) + str(ran_num + 1))
            check = check_move(field, gen_code)
            if (check == 'clear'):
                message.append(gen_code)
                return [gen_code]

    def make_move(field, code, powerlist):
        end = False
        change = False
        l = let(code)
        n = num(code)
        if field[l][n] == 0:
            resultus = 'Мимо.'
            field[l][n] = 100
            change = True
        else:
            powerlist[field[l][n]] -= 1
            if (powerlist[field[l][n]] == 0):
                resultus = 'Убит.'
            else:
                resultus = 'Ранен.'
            field[l][n] = 200
        if sum(powerlist) == 0:
            end = True
        return ({"field": field, "powerlist": powerlist, "end": end, "change": change, "code": code, "resultus": resultus})

    logging.info(f"CALLED: {called}")
    if called:
        computer_field = genesis('great_random')
        #Загрузка поля...
        gsum = 20
        csum = 20
        g_power = [0, 1, 1, 1, 1, 2, 2, 2, 3, 3, 4]
        c_power = [0, 1, 1, 1, 1, 2, 2, 2, 3, 3, 4]
        g_field = sowing(user_field)
        c_field = sowing(computer_field)
        #Готово
        move = 'computer'
    logging.info(f"DATA:{c_power}, {g_power}, {g_field}, {c_field}")
    if move == 'gamer':
        message = list()
        result = make_move(c_field, input_code(c_field)[0], c_power)
        c_field = result["field"]
        c_power = result["powerlist"]
        message.append(result['resultus'])
        if (result["end"]):
            message.append('Вы выиграли')
        if (result["change"]):
            move = 'computer'

    if move == 'computer':
        result = make_move(g_field, generate_code(g_field)[0], g_power)
        g_field = result["field"]
        g_power = result["powerlist"]
        message.append(result['resultus'])

        if (result["end"]):
            message.append('Вы проиграли')
        if (result["change"]):
            move = 'gamer'

    res['response']['text'] = ' '.join(str(i) for i in message)

a = ['a1d', 'a3d', 'a5d', 'a7d', 'c1r', 'c3r', 'c5r', 'c7r', 'a9r', 'g3d']

def ship_placement(user_id, res, req, called):
    global state, user_field
    if called:
        res['response']['text'] = 'Введите координаты ваших кораблей'
        return
    user_field = (req['request']['original_utterance'].lower()).split()
    state = 'virtual'
    gameplay_virtual(user_id, res, req, True)
    return

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
    global state, logged, id_, auth_pos, pass_1, pass_2, firstname
    if not logged:
        if called:
            res['response']['text'] = 'Назовите своё имя'
            sessionStorage[user_id] = {
                'first_name': None
            }
            return
        if sessionStorage[user_id]['first_name'] is None:
            first_name = get_first_name(req)
        # если не нашли, то сообщаем пользователю что не расслышали.
            if first_name is None:
                res['response']['text'] = \
                    'Не расслышал имя. Повтори, пожалуйста!'
        if auth_pos == 0 and first_name:
            sessionStorage[user_id]['first_name'] = first_name
            firstname = first_name
            session = db_session.create_session()
            find_name = [user.name for user in session.query(User).filter((User.name == sessionStorage[user_id]['first_name'] ))]
            if find_name:
                res['response']['text'] = 'Назовите кодовое слово'
                auth_pos = 3
                return
            else:
                res['response']['text'] = 'Для регистрации назовите кодовую фразу дважды'
                auth_pos = 1
        elif auth_pos == 1:
            pass_1 = req['request']['original_utterance'].lower()
            res['response']['text'] = 'И ещё раз'
            auth_pos = 2
            return
        elif auth_pos == 2:
            pass_2 = req['request']['original_utterance'].lower()
            if pass_1 == pass_2:
                res['response']['text'] = 'Вы успешно зарегистрированы!'
                hash_object = hashlib.sha1(pass_1.encode())
                hex_dig = hash_object.hexdigest()
                session = db_session.create_session()
                user = User()
                user.name = sessionStorage[user_id]['first_name']
                user.hashed_password = hex_dig
                session.add(user)
                session.commit()
                logged = True
                auth_pos = 0
                state = 'menu'
                return
            else:
                res['response']['text'] = 'Пароли не совпадают. Попробуйте ещё раз'
                auth_pos = 0
                state = 'menu'
                return
        elif auth_pos == 3:
            pass_1 = req['request']['original_utterance'].lower()
            session = db_session.create_session()
            find_pass = [user.hashed_password for user in session.query(User).filter(
                (User.name == sessionStorage[user_id]['first_name']))]
            find_pass = find_pass[0]
            hash_object = hashlib.sha1(pass_1.encode())
            hex_dig = hash_object.hexdigest()
            if hex_dig == find_pass:
                res['response']['text'] = 'Вы успешно авторизовались!'
                logged = True
                auth_pos = 0
                state = 'menu'
                return
            else:
                res['response']['text'] = 'Пароль неверный'
                auth_pos = 0
                state = 'menu'
                return
    else:
        if called:
            res['response']['text'] = f"Вы уже вошли в аккаунт как {firstname}"
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
            return
        
        if req['request']['original_utterance'].lower() in ['выйти из аккаунта', 'выйти']:
            logged = False
            id_ = -1
            state = 'menu'
            main_menu(user_id, res, req, True)
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

def highscores(user_id, res, req, called):
    global state
    if called:
        sessionStorage[user_id] = {
            'suggests': [
                "Назад",
            ]
        }
        res['response']['text'] = 'Рекорды. Тут пока пусто.'
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
    db_session.global_init()
    if "PORT" in os.environ:
        app.run(host='0.0.0.0', port=os.environ["PORT"])
    else:
        app.run(host='127.0.0.1', port=5000)