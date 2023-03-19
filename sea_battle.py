from random import randint
from random import choice
from time import sleep
import os

# ===============================================================
# Зравстуйте.
# Я пытался код немного по другому написать, но к сожалению
# не получилось. Если не трудно посмотрите пожалуста. Я там с 
# ошибкой столкнулся, сам не смог разобраться. По ссылке код и 
# видео с ошибкой     https://cloud.mail.ru/public/qKfY/iMQAtJPaJ
# ================================================================

class Cell:

    d_contour = '🟨'
    d_miss = '⬜'
    d_damag = '💥'
    d_sea = '🟦'
    d_ship = '🟩'
    # d_sea = '0'
    # d_contour = '•'
    # d_miss = '✹'
    # d_damag = 'X'
    # # d_ship = '🞒'
    # d_ship = '■'


class Dot:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __repr__(self):
        return f"({self.x}, {self.y})"


class BoardException(Exception):
    pass


class BoardOutException(BoardException):
    def __str__(self):
        return "Вы пытаетесь выстрелить за доску!"


class BoardUsedException(BoardException):
    def __str__(self):
        return "Вы уже стреляли в эту клетку"


class BoardWrongShipException(BoardException):
    pass


class Ship:
    def __init__(self, position, ship_size, direction):
        self.position = position
        self.ship_size = ship_size
        self.direction = direction
        self.lives = ship_size

    @property
    def dots(self):
        ship_dots = []
        for i in range(self.ship_size):
            cur_x = self.position.x
            cur_y = self.position.y

            if self.direction == 0:
                cur_x += i

            elif self.direction == 1:
                cur_y += i

            ship_dots.append(Dot(cur_x, cur_y))

        return ship_dots

    def shooten(self, shot):
        return shot in self.dots


class Board:
    def __init__(self, hid=False, size=6):
        self.size = size
        self.hid = hid

        self.count = 0

        self.field = [[Cell.d_sea]*size for _ in range(size)]

        self.busy = []
        self.ships = []
        self.wounded_ship = 0
        self.wounded_dot = 0

    def add_ship(self, ship):

        for d in ship.dots:
            if self.out(d) or d in self.busy:
                raise BoardWrongShipException()
        for d in ship.dots:
            self.field[d.x][d.y] = Cell.d_ship
            self.busy.append(d)

        self.ships.append(ship)
        self.contour(ship)

    def contour(self, ship, verb=False):
        near = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1), (0, 0), (0, 1),
            (1, -1), (1, 0), (1, 1)
        ]
        for d in ship.dots:
            for dx, dy in near:
                cur = Dot(d.x + dx, d.y + dy)
                if not (self.out(cur)) and cur not in self.busy:
                    if verb:

                        self.field[cur.x][cur.y] = Cell.d_contour
                    self.busy.append(cur)

    def __str__(self):
        print("   1 2 3 4 5 6 " + ' ' * 14, end='')
        res = ''
        for i, row in enumerate(self.field):
            res += f"\n{i + 1} {''.join(row)}"
        if self.hid:
            res = res.replace(Cell.d_ship, Cell.d_sea)
        return res

    def out(self, d):
        return not ((0 <= d.x < self.size) and (0 <= d.y < self.size))

    def shot(self, d):
        if self.out(d):
            raise BoardOutException()

        if d in self.busy:
            raise BoardUsedException()

        self.busy.append(d)

        for ship in self.ships:
            if d in ship.dots:
                ship.lives -= 1
                self.wounded_ship = ship.lives
                self.field[d.x][d.y] = Cell.d_damag
                if ship.lives == 0:
                    self.count += 1
                    self.contour(ship, verb=True)
                    print('-' * 50)
                    print(" " * 16, "Корабль уничтожен!")
                    print('-' * 50)
                    sleep(2)
                    return True                  
                else:
                    print('-' * 50)
                    print(" " * 16, "Корабль ранен!")
                    print('-' * 50)
                    sleep(2)
                    self.wounded_dot = d
                    return True

        self.field[d.x][d.y] = Cell.d_miss
        miss = ['Мимо!', 'Промазал!', 'Перелет', 'Недолет',
            'Трубка 15. Прицел 120. Бац-бац и мимо...']
        print('-' * 50)
        print(" " * 17, choice(miss))
        print('-' * 50)
        sleep(2)
        return False

    def begin(self):
        self.busy = []


class Player:
    def __init__(self, board, enemy):
        self.board = board
        self.enemy = enemy

    def ask(self):
        raise NotimplementedError()

    def move(self):
        while True:
            try:
                target = self.ask()
                repeat = self.enemy.shot(target)
                return repeat
            except BoardException as e:
                print(e)


class AI(Player):
    def ask(self):
        if self.enemy.wounded_ship == 0:
            self.fix_shot_list = []
            d = Dot(randint(0, 5), randint(0, 5))
            print(f"Ход компьютера: {d.x+1} {d.y+1}")
            sleep(2)
            return d
        else:          #Добиваем подранка
            d = self.enemy.wounded_dot
            l = self.fix_shot_list
            if l == [] or l[0] != d:
                l.append(d)
            near = [(d.x + 1, d.y), (d.x - 1, d.y),
                    (d.x, d.y + 1), (d.x, d.y - 1)]
            if len(l) >= 2:
                if l[0].x == l[1].x:
                    near = [(d.x, d.y + 1), (d.x, d.y - 1), 
                        (d.x, d.y + 2), (d.x, d.y - 2)]
                else:
                    near = [(d.x + 1, d.y), (d.x - 1, d.y),
                        (d.x + 2, d.y), (d.x - 2, d.y)]
                # print('near',  near)
            dx, dy = choice(near)
            d = Dot(dx, dy)
            print(f"Ход компьютера: {d.x+1} {d.y+1}")
            sleep(2)
            return d
                

class User(Player):
    def ask(self):
        while True:
            cords = input(" " * 30 + "Ваш ход: ").split()
            sleep(1)

            if len(cords) != 2:
                print(" " * 30 + " Введите 2 координаты! ")
                continue

            x, y = cords

            if not (x.isdigit()) or not (y.isdigit()):
                print(" " * 30 + " Введите числа! ")
                continue

            x, y = int(x), int(y)

            return Dot(x-1, y-1)

class Game:
    def __init__(self, size=6):
        self.size = size
        pl = self.random_board()
        co = self.random_board()
        co.hid = True

        self.ai = AI(co, pl)
        self.us = User(pl, co)
        self.clear = lambda: os.system('cls')


    def random_board(self):
        board = None
        while board is None:
            board = self.random_place()
        return board

    def random_place(self):
        lens = [3, 2, 2, 1, 1, 1, 1]
        board = Board(size=self.size)
        attempts = 0
        for ship_size in lens:
            while True:
                attempts += 1
                if attempts > 2000:
                    return None
                ship = Ship(Dot(randint(0, self.size), randint(
                    0, self.size)), ship_size, randint(0, 1))
                try:
                    board.add_ship(ship)
                    break
                except BoardWrongShipException:
                    pass
        board.begin()
        return board

    def greet(self):
        print("****************************************************************************")
        print("░██████╗███████╗░█████╗░  ██████╗░░█████╗░████████╗████████╗██╗░░░░░███████╗")
        print("██╔════╝██╔════╝██╔══██╗  ██╔══██╗██╔══██╗╚══██╔══╝╚══██╔══╝██║░░░░░██╔════╝")
        print("╚█████╗░█████╗░░███████║  ██████╦╝███████║░░░██║░░░░░░██║░░░██║░░░░░█████╗░░")
        print("░╚═══██╗██╔══╝░░██╔══██║  ██╔══██╗██╔══██║░░░██║░░░░░░██║░░░██║░░░░░██╔══╝░░")
        print("██████╔╝███████╗██║░░██║  ██████╦╝██║░░██║░░░██║░░░░░░██║░░░███████╗███████╗")
        print("╚═════╝░╚══════╝╚═╝░░╚═╝  ╚═════╝░╚═╝░░╚═╝░░░╚═╝░░░░░░╚═╝░░░╚══════╝╚══════╝")
        print("****************************************************************************")
        print()
        print("  формат ввода: x y  x - номер строки  y - номер столбца")


    def show_board(self):
        print()
        print('      Наши' + ' '* 20, end="")
        print('Пра-а-тивники')
        for us, ai in zip(self.us.board.__str__().split('\n'), self.ai.board.__str__().split('\n')):
            print(us + ' ' * 15 + ai)

    def loop(self):
        num = 0
        while True:
            self.show_board()
            if num % 2 == 0:
                print(" " * 30 + "-"*20)
                print(" " * 30 + "Огонь!")
                repeat = self.us.move()
            else:
                print("-"*20)
                print("Ложись!")
                repeat = self.ai.move()
            if repeat:
                num -= 1

            if self.ai.board.count == 7:
                print("-"*20)
                print("Наши победили!")
                break

            if self.us.board.count == 7:
                print("-"*20)
                print("Мы им еще покажем!")
                break
            num += 1
            self.clear()
    def start(self):
        self.greet()
        self.loop()

g = Game()
g.start()
