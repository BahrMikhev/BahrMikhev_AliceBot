from random import *


def genesis(power):
    def choose_dir():
        direct = randint(0, 1);
        if direct == 1:
            direct = 'r'
        else:
            direct = 'd'
        return direct

    def pl_check(field, let, num, direct, size):
        if (direct == 'r'):
            ll = 1
            nn = 0
        else:
            nn = 1
            ll = 0
        for i in range(size):
            for q in [let - 1, let, let + 1]:
                for p in [num - 1, num, num + 1]:
                    if (q < 10 and p < 10 and q > -1 and p > -1):
                        if (field[q][p] != 0):
                            return False
            let += ll
            num += nn
        return True

    def place(field, let, num, direct, size, cnt):
        if (direct == 'r'):
            ll = 1
            nn = 0
        else:
            nn = 1
            ll = 0
        for i in range(size):
            field[let + ll * i][num + nn * i] = cnt
        return field

    def null_field():
        field = []
        for i in range(10):
            field.append([])
            for j in range(10):
                field[i].append(0)
        return field

    def great_random():
        answer = []
        for i in range(10): answer.append('')
        field = null_field()
        for i in range(10):
            flag = 0
            size = 1
            if i < 6: size += 1
            if i < 3: size += 1
            if i < 1: size += 1
            fall = 5000 // size
            while flag < fall:
                flag += 1
                direct = choose_dir()
                if (direct == 'r'):
                    let = randint(0, 10 - size)
                    num = randint(0, 9)
                else:
                    let = randint(0, 9)
                    num = randint(0, 10 - size)
                if (pl_check(field, let, num, direct, size)):
                    answer[9 - i] = chr(65 + let) + str(num + 1) + direct
                    field = place(field, let, num, direct, size, i + 1)
                    break
            if flag >= fall: return ['fail']
        return answer

    if power == 'great_random':
        res = great_random()
        while (res[0] == 'fail'):
            res = great_random()
        return res
