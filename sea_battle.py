from random import *
from SeaWarStrategies import *


def game(gamer_field, comp_field):
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
        while True:
            input_code = input('Ваш ход: ')
            check = check_move(field, input_code)
            if (check == 'incorrect'):
                print('Некорректный ход')
            elif (check == 'shot'):
                print('Вы сюда уже стреляли')
            else:
                return input_code

    def generate_code(field, cookie):
        print('Ход компьютера: ', end='')
        while True:
            ran_let = randint(0, 9)
            ran_num = randint(0, 9)
            gen_code = (chr(65 + ran_let) + str(ran_num + 1))
            check = check_move(field, gen_code)
            if (check == 'clear'):
                print(gen_code)
                return [gen_code, cookie]

    def make_move(field, code, powerlist):
        end = False
        change = False
        l = let(code)
        n = num(code)
        if field[l][n] == 0:
            print('Мимо')
            field[l][n] = 100
            change = True
        else:
            powerlist[field[l][n]] -= 1
            if (powerlist[field[l][n]] == 0):
                print('Убит')
            else:
                print('Ранен')
            field[l][n] = 200
        if sum(powerlist) == 0:
            end = True
        return ({"field": field, "powerlist": powerlist, "end": end, "change": change})

    print('Загрузка поля...')
    gsum = 20
    csum = 20
    g_power = [0, 1, 1, 1, 1, 2, 2, 2, 3, 3, 4]
    c_power = [0, 1, 1, 1, 1, 2, 2, 2, 3, 3, 4]
    g_field = sowing(gamer_field)
    c_field = sowing(comp_field)
    print('Готово')
    move = 'computer'
    cookie = ''
    print()
    while True:
        if move == 'gamer':
            result = make_move(c_field, input_code(c_field), c_power)
            c_field = result["field"]
            c_power = result["powerlist"]
            if (result["end"]):
                return 'Вы выиграли'
            if (result["change"]):
                move = 'computer'
                print()
        if move == 'computer':
            result = make_move(g_field, generate_code(g_field, cookie)[0], g_power)
            g_field = result["field"]
            g_power = result["powerlist"]
            if (result["end"]):
                return 'Вы проиграли'
            if (result["change"]):
                move = 'gamer'
                print()


a = ['a1d', 'a3d', 'a5d', 'a7d', 'c1r', 'c3r', 'c5r', 'c7r', 'a9r', 'g3d']
game(a, genesis('great_random'))
