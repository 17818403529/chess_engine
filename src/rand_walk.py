from models import *
from random import choice


class RandWalk:
    def __init__(self, side):
        self.side = side
        self.chess_dict = Chess.gen_chess_dict()

    def start_a_game(self):
        while True:
            fen = input("FEN: ")
            board = Chess.convert(fen, self.chess_dict)
            if board:
                break
            else:
                print("illegal")

        while True:
            if self.side == board["turn"]:
                legal_moves = Chess.gather_legal_moves(board, self.chess_dict)
                move = choice(list(legal_moves.keys()))
                board = Chess.take_a_move(board, legal_moves[move], self.chess_dict)
                print(move)
            else:
                while True:
                    move = input("your move:")
                    legal_moves = Chess.gather_legal_moves(board, self.chess_dict)
                    if move not in legal_moves.keys():
                        if move=="?":
                            print(legal_moves)
                        else:
                            print("illegal")
                    else:
                        board = Chess.take_a_move(board, legal_moves[move], self.chess_dict)
                        break

    def send_a_move(self, move):
        pass


fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"

rw = RandWalk("b")
rw.start_a_game()
