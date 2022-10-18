"""Х-0"""
import random
from time import sleep

po = ['-'] * 3 * 3


def pole():
    """ Печатаем поле """
    for i in range(3):
        for j in range(3):
            print(str(po[i * 3 + j]).rjust(3), end='')
        print()


def inp(x_o):
    """ Ручной ввод координат """
    while True:
        x, y = input(f"введите через пробел координаты для {x_o}:  ").split()
        if not x.isdigit() or not y.isdigit():
            print('введено не верно')
            continue
        x = int(x) - 1
        y = int(y) - 1
        if x not in [0, 1, 2] or y not in [0, 1, 2]:
            print('за пределами поля')
            continue
        if po[x * 3 + y] != '-':
            print('клетка занята')
            continue
        po[x * 3 + y] = x_o
        break


def stepsInf(x):
    """ Определяем индексы клеток, занятых значением (x) """
    steps = []
    for i in range(len(po)):
        if po[i] == x:
            steps.append(i)
    return steps


def win_combs():
    """
    базы победных комбинаций:
    win  - все победные комбинации
    win1 - словарь. до победы 1 ход. ключи - кортежи из двух эл., значение = побед. комб. из 3 эл
    win2 - список списков. индекс = индекс поля,
           значение (список) - все индексы можно сходить если занята клетка po[n], чтобы оставить 1 ход до победы
    """
    win = [[0, 1, 2], [3, 4, 5], [6, 7, 8], [0, 3, 6], [1, 4, 7], [2, 5, 8], [0, 4, 8], [2, 4, 6]]
    win1 = {}      # {(0,1):[0,1,2],(0,2):[0,1,2],(1,2):[0,1,2],,,,}
    for i in win:               # создаем словарь win1
        for j in range(3):      # ключ - кортеж из двух индексов
            m = i.pop(j)        # его значение - победная комбинация, использующая эти два индекса
            kort = tuple(i)
            i.insert(j, m)
            win1[kort] = i
    win2 = [[] for _ in range(9)]
    for l in win1.keys():        # пробег по кортежам списка [(0,1),(0,2),(1,2)...] (1 шаг до победы)
        win2[l[0]].append(l[1])  # берем первый элемент из кортежа, делаем его индексом в win2
        win2[l[1]].append(l[0])  # а второй элемент добавляем к списку под этим индексом
    return win1, win2


def comp(stEnemy, stMy, win1, win2, x_o):
    """
    Шаги компьютера (от лица компьютера)
    Enemy - соперник компьютера (игрок)
    My - компьютер
    проверяет на следующий выигрышный ход, если может победить - ставит туда
    если не может, но в следующем ходу может выиграть противник - перекрывает ему ход
    если ни то, ни другое - ставит рандомом так, чтобы остался 1 ход до победы
    если и это не выходит, то ставит просто рандомом, проверяя занятые
    """

    def step1Computer(steps):
        """
        первые 2 шага:
        - вычисление клетки где до победы 1 шаг.
        - потом при вызове функции проверка до победы кого (передаются списки с ходами игрока или компьютера).
        если до победы компа 1 ход - важность хода 1 (st1)
        если до победы игрока 1 ход - важность хода 2 (st2)
        """
        stepComp1 = []  # список c возможными ходами
        # пробегаем по кортежам из 2х эл (1 шаг до победы)
        # если такие шаги есть на доске, записываем третий шаг в stepComp1
        for i, j in win1.keys():
            if i in steps and j in steps:
                el = list(set(win1[(i, j)]).difference({i, j}))[0]
                if po[el] != '-':
                    continue
                else:
                    stepComp1.append(el)
        if len(stepComp1) > 0:  # если есть куда ходить
            step1 = random.choice(stepComp1)  # шагу присваивается рандомный вариант
        else:
            step1 = -1  # если элементов нет, присваивается отрицательное значение, что значит переход к другому шагу
        return step1

    def step2Computer():
        """
        третий шаг (st3):
        вычисляет, где есть свободные две клетки для выиграшной комбинации, используя имеющиеся ходы
        и записывает результат в список
        """
        step2Comp = []
        # список из индексов для 2го хода и дальнейшей победы
        if len(stMy) <= 0:  # если у компьютера не было шагов возвращает -1 = переход к следующему шагу
            return -1
        for i in stMy:         # перебор имеющихся шагов компьютера
            for j in win2[i]:  # перебор возможных вторых ходов для имеющегося хода для построения выигрышной комбинации
                if (i, j) in win1 or (j, i) in win1:  # i и j обязательно есть в ключах словаря win1
                    win_comb = win1.get((i, j)) or win1.get((j, i))
                    element = list( set(win_comb).difference({i, j}) )[0]
                    if po[j] == po[element] == '-':  # проверяем возможную комбинацию на свободность
                        step2Comp.append(element)  # в список добавл. индекс хода для построения выигрыша i, j, element
        if len(step2Comp) > 0:  # если есть предполагаемые ходы чтобы потом построить победную комбинацию
            step2 = random.choice(step2Comp)  # выбираем рандомом ход
        else:
            return -1  # -1 = переход к следующему шагу
        return step2

    # список с предполагаемыми ходами для 4 шага. сначала пробегаем по приоритетным углам и центру
    step4Comp = [i for i in (0, 2, 4, 6, 8) if po[i] == '-']
    if len(step4Comp) > 0:  # если список с предполагаемыми приоритетными ходами не пуст
        st4 = random.choice(step4Comp)  # то выбирается случайный ход из свободных
    else:
        step4Comp = [i for i in (1, 3, 5, 7) if po[i] == '-']
        st4 = random.choice(step4Comp)  # выбирается случайный ход

    st1 = step1Computer(stMy)  # первый шаг - обрабатывается список ходов компьютера
    st2 = step1Computer(stEnemy)  # второй шаг-обрабатывется список ходов игрока
    st3 = step2Computer()
    # третий шаг-получаем индекс для дальнейшей победы (есть минимум 1 ход и свобод. поля для использования комбинации)

    if st1 >= 0:
        comp_step = st1
    elif st2 >= 0:
        comp_step = st2
    elif st3 >= 0:
        comp_step = st3
    else:
        comp_step = st4
    po[comp_step] = x_o  # значению клетки поля с соответствующмим индексом присваивается  - компьютер сходил.
    yy = comp_step % 3 + 1
    xx = comp_step // 3 + 1
    print('ход компьютера:', xx, yy)


def check():
    """
    пока возвращает 1 игра проджолжается
    -1 ничья
    либо возвращает значение занятой клетки - победитель
    """
    for x in (0, 3, 6):
        if po[x] == po[x + 1] == po[x + 2] != '-':
            return po[x]
    for x in (0, 1, 2):
        if po[x] == po[x + 3] == po[x + 6] != '-':
            return po[x]
    if po[0] == po[4] == po[8] != '-' or po[2] == po[4] == po[6] != '-':
        return po[4]
    if '-' not in po:
        return -1
    return 1


def startGame():
    print('Добро пожаловать в крестики-нолики!')
    sleep(0.8)
    print('Координаты нужно вводить через пробел: сначала строка, затем столбец')
    sleep(0.8)
    print('1 - первая, 3 - последняя')
    sleep(1)
    while True:
        player_comp = int(input('с кем играем? 1 - человек, 2 - компьютер:  '))
        if player_comp in (1, 2):
            break
        else:
            print('Ты промахнулся, воин!')

    pole()  # печатаем поле
    if player_comp == 2:
        sleep(0.4)
        print('Удачи тебе, воин!')
        sleep(0.4)
        whoX = random.randrange(2)  # 0: X игрок, 0 комп/ 1: X комп, 0 игрок
        if whoX:
            print('Первым ходит компьютер')
        else:
            print('Первым ходит игрок')
    fin = 1
    win1, win2 = win_combs()

    count = 1
    while fin == 1:
        sleep(1)
        print(f':::: шаг № {count} ::::')
        for xoxo in ('X', '0'):
            if player_comp == 1:
                step_func = inp
                args = xoxo
            else:
                if (whoX == 0 and xoxo == 'X') or (whoX == 1 and xoxo == '0'):
                    step_func = inp
                    args = xoxo
                elif whoX == 0 and xoxo == '0':
                    step_func = comp
                    args = (stepsInf('X'), stepsInf('0'), win1, win2, '0')
                elif whoX == 1 and xoxo == 'X':
                    step_func = comp
                    args = (stepsInf('0'), stepsInf('X'), win1, win2, 'X')
            step_func(*args)
            pole()
            fin = check()  # проверка на победу
            if fin != 1:  # если возщвращается не 1 то прерывается
                break
        count += 1

    if fin == -1:
        print('победила дружба')
    else:
        print('ПОБЕДИТЕЛЬ:', fin)


startGame()  # вызов игры

