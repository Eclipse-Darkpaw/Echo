from board import Board
from main import read_line, read

def connect_four(self):
    while True:
        row = readInt("How many rows?")
        while row <= 4:
            row = readInt("That's too small. How many rows?")
        col = readInt("How many columns?")
        while col <= 4 or col > 20:
            if col <= 4:
                 col = readInt("That's too small. How many columns?")
            else:
                col = readInt("Thats too large. How many columns?")
        board = Board('x', 'o', row, col)
        game = Game(board);
        game.play()
        if input("Play again?\n[Y]es or [N]o") == "N":
            break
    
def displayBoard(board):
    print = "";
    for r in range(board.rows()):
        print = print + "|"
        for c in range(board.cols()):
            print = print + " " + board.getSpot(r, c) + " "
        print = print + "\n"

    add = ''
    for i in range(board.cols() + 1):
        print = print + "---"
    print = print + "\n ";

    for i in range(board.cols()):
        add = " ";
        add = add + str(i)
        while(len(add) < 3):
            add = add + " "
        print = print + add
    return print

def readLine(out=''):
    output(out)
    return input(out)


def readInt(out=''):
    num = 0
    if out is not '':
        output(out)

    parsed = False
    while not parsed:
        input = False
        inp = readLine()
        while len(inp) == 0:
            inp = readLine()
        num = 0

        try:
            num = int(inp)
            parsed = True
        except NumberFormatException:
            output("Thats not a valid number! Try again!");
            parsed = False
    return num
