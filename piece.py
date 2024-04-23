from copy import deepcopy
from time import time

ds_path = "C:/Users/17818/Music/chess_engine.py/feasible_moves.json"

with open(ds_path, "r", encoding="UTF-8") as f:
    fea_moves = json.load(f)


class Kqbr:
    def __init__(self, symbol):
        self.symbol = symbol
        self.symbol_upper = symbol.upper()
        self.side = "b" if symbol == "b" else "w"

    def show_legal_moves(self, pos, board, blank):
        moves = []
        fea = fea_moves[self.symbol_upper][pos]
        for direc in fea:
            for des in direc:
                if des in blank:
                    moves.append(self.symbol_upper + pos + des)
                else:
                    if board[des].side != self.side:
                        moves.append(self.symbol_upper + pos + "x" + des)
                    break


class Knight:
    def __init__(self, symbol):
        self.symbol = symbol
        self.symbol_upper = "N"
        self.side = "b" if symbol == "b" else "w"

    def show_legal_moves(self, pos, board, blank):
        moves = []
        fea = fea_moves[self.symbol][pos]
        for des in fea:
            if des in blank:
                moves.append(self.symbol_upper + pos + des)
            else:
                if board[des].side != self.side:
                    moves.append(self.symbol_upper + pos + "x" + des)
                break
