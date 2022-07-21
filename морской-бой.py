from random import choice, randint
from time import sleep

class GameExceptions(Exception):
    pass

class BoardOutException(GameExceptions):
    def __str__(self):
        return 'ваш выбор вне диапазона доски'

class BoardBusyDotException(GameExceptions):
    def __str__(self):
        return 'вы пытаетесь выстрелить в занятую точку'


class Dot:
    x = 0
    y = 0

    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __repr__(self):
        return f'Dot({self.x}, {self.y})'

class Ship:
    length = 0
    nose_dot = Dot(0, 0)
    direction = True
    lives = 0

    def __init__(self, length, nose_dot, direction):
        self.length = length
        self.nose_dot = nose_dot
        self.direction = direction
        self.lives = length

    def __str__(self):
        if self.length == 1:
            return 'однопалубник'
        else:
            return f'{self.length}-х палубник'

    @property
    def shipdots(self):
        ship_dots = []
        x = self.nose_dot.x
        y = self.nose_dot.y
        if self.direction:
            for i in range(self.length):
                ship_dots.append(Dot(x, y + i))
        else:
            for i in range(self.length):
                ship_dots.append(Dot(x + i, y))
        return ship_dots

    def shooten(self, shot):
        if shot in self.shipdots:
            self.lives -= 1
            return True
        else:
            return False



class Board:
    hid = False
    shipslist = []
    aliveships = 0
    def __init__(self, size, hid=False, aliveships = 0):
        self.size = size
        self.hid = hid
        self.shipslist = []
        self.aliveships = aliveships
        self.field = [['O'] * self.size for i in range(self.size)]
        self.shipsbusydots = []
        self.contbusydots = []
        self.dotsofshots = []
    def __str__(self):
        field_str = '   |'
        probel = '----' * (self.size + 1)
        for i in range(self.size):
            if i + 1 >= 10:
                addstring = f' {i + 1}|'
                field_str += addstring
            else:
                addstring = f' {i + 1} |'
                field_str += addstring
        field_str += f'\n{probel}'

        for i, j in enumerate(self.field):
            if i + 1 >= 10:
                info_row = f"{i + 1} | {' | '.join(j)} |"
                field_str += f'\n{info_row}'
                field_str += f'\n{probel}'
            else:
                info_row = f" {i + 1} | {' | '.join(j)} |"
                field_str += f'\n{info_row}'
                field_str += f'\n{probel}'
        if self.hid:
            field_str = field_str.replace('■', '0')
        return field_str

    def add_ship(self, ship):
        for dot in ship.shipdots:
            if self.out(dot) or (dot in self.shipsbusydots) or (dot in self.contbusydots):
                raise BoardOutException
        for dot in ship.shipdots:
            self.field[dot.x][dot.y] = '■'
            self.shipsbusydots.append(dot)
        self.shipslist.append(ship)
        self.aliveships += 1
        self.contour(ship, False)

    def out(self, dot):
        return dot.x >= self.size or dot.x < 0 or dot.y >= self.size or dot.y < 0

    def contour(self, ship, print_=True):
        around = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
        for dot in ship.shipdots:
            for dot_ in around:
                cont_d = Dot((dot.x + dot_[0]), (dot.y + dot_[1]))
                if not self.out(cont_d) and cont_d not in self.shipsbusydots and self.field[cont_d.x][cont_d.y] != 'X':
                    if print_:
                        self.field[cont_d.x][cont_d.y] = '*'
                        self.contbusydots.append(cont_d)
                    else:
                        self.contbusydots.append(cont_d)

    def shot(self, dot):
        if any([self.out(dot),
                dot in self.dotsofshots,
                # self.field[dot.x][dot.y] == 'T',
                # self.field[dot.x][dot.y] == 'X',
                self.field[dot.x][dot.y] == '*']):
            raise BoardBusyDotException
        else:
            for ship in self.shipslist:
                if ship.shooten(dot):
                    if ship.lives == 0:
                        self.field[dot.x][dot.y] = 'X'
                        self.contour(ship, True)
                        self.aliveships -= 1
                        self.dotsofshots.append(dot)
                        print('корабль убит!')
                    else:
                        self.field[dot.x][dot.y] = 'X'
                        self.dotsofshots.append(dot)
                        print('корабль ранен')
                    return True
            self.field[dot.x][dot.y] = 'T'
            self.dotsofshots.append(dot)
            print('в молоко!')
            return False

class Player:
    myBoard = Board
    enemyBoard = Board
    def __init__(self, myBoard, enemyBoard):
        self.myBoard = myBoard
        self.enemyBoard = enemyBoard

    def ask(self):
        pass

    def move(self):
        pass

class User(Player):
    def ask(self):
        while True:
            x = input('введите номер строки для хода - ')
            y = input('введите номер столбца для хода - ')
            try:
                x, y = int(x), int(y)
            except ValueError:
                print('Некорректный ввод. Повторите')
                continue
            if self.enemyBoard.out(Dot((x - 1), (y - 1))):
                raise BoardOutException
            break
        return Dot(x - 1, y - 1)

    def move(self):
        while True:
            try:
                usershot = self.enemyBoard.shot(self.ask())
            except GameExceptions as e:
                print(e)
                continue
            return usershot

class AI(Player):
    def ask(self):
        AIshot = Dot(randint(0, self.enemyBoard.size - 1), randint(0, self.enemyBoard.size - 1))
        return AIshot

    def move(self):
        while True:
            try:
                shot = self.enemyBoard.shot(self.ask())
            except GameExceptions:
                continue
            print(f'выстрел в точку ({self.enemyBoard.dotsofshots[-1].x + 1}, {self.enemyBoard.dotsofshots[-1].y + 1})')
            print(self.enemyBoard)
            return shot

class Game:
    size = 0
    user = User
    ai = AI
    userboard = Board
    aiboard = Board

    def __init__(self, size):
        self.size = size

    def random_board(self, hid=False):
        if self.size > 6:
            lens = [4, 3, 2, 2, 1, 1, 1, 1]
        else:
            lens = [3, 2, 2, 1, 1, 1, 1]
        board = Board(self.size, hid)
        for i in lens:
            attempts = 0
            while attempts < 1000:
                attempts += 1
                ship = Ship(i, Dot(randint(0, self.size - 1), randint(0, self.size - 1)), choice([True, False]))
                try:
                    board.add_ship(ship)
                except BoardOutException:
                    continue
                break
        if self.size == 6:
            if board.aliveships == 7:
                return board
            else:
                return False
        else:
            if board.aliveships == 8:
                return board
            else:
                return False

    def create_board(self, hid=False):
        board = False
        while not board:
            board = self.random_board(hid)
        return board

    def great(self):
        print('     Добро пожаловать в игру     ')
        print('           морской-бой!          ')
        print('---------------------------------')
        print('       вы стреляете первым!      ')
        print('для выстрела введите номер строки')
        print('        затем номер столбца      ')
        print('-------------------------------- ')
        print('если игрок попал или убил корабль')
        print('        ход повторяется          ')

    def loop(self):
        userBoard = self.create_board(False)
        aiBoard = self.create_board(True)
        user = User(userBoard, aiBoard)
        ai = AI(aiBoard, userBoard)

        print(' ')
        print('          ваше поле         ')
        print('----' * (self.size + 1))
        print(userBoard)

        while True:
            uMove = True
            aiMove = True
            sleep(2)
            while uMove:
                print('\nваш ход \n ')
                print('      поле компьютера       ')
                print(aiBoard)
                uMove = user.move()
                sleep(2)
                if aiBoard.aliveships == 0:
                    print('Поздравляем, вы победили!')
                    break
            if aiBoard.aliveships == 0:
                break

            while aiMove:
                print('\nход компьютера')
                aiMove = ai.move()
                sleep(3)
                if userBoard.aliveships == 0:
                    print('Победил компьютер!')
                    break
            if userBoard.aliveships == 0:
                break
        print('конец игры')

    def start(self):
        self.great()
        self.loop()

z = int(input('введите размер поля - 6 или больше\n'))

g = Game(z)
g.start()

