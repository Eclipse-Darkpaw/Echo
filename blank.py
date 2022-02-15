class MartianChess:
    def __init__(self, player1, player2):
        self.player1 = player1
        self.player2 = player2
        self.board = None
        self.gen_board()


    def gen_board(self):
        if len(self.players) == 2:
            pass                    # 2 player game
        elif len(self.players) == 4:
            pass                    # 4 player game
        else:
            return -1               # invalid player number. error code -1

    def play(self):
        pass

class Piece:
