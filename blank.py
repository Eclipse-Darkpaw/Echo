class MartianChess:
    def __init__(self, player1, player2):
        self.player1 = player1
        self.player2 = player2
        self.board = None
        self.gen_board()


    def gen_board(self):

                       # 4 player game
        else:
            return -1               # invalid player number. error code -1

    def play(self):
        pass


class Piece:

    def move(self):
        raise NotImplementedError('Method not implemented by inherited class')

class Pawn(Piece):
    def move(self):
        pass

class Drone(Piece):
    pass

class Queen(Piece):
    def move(self,):


