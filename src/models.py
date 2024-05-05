from copy import deepcopy
from random import choice


class Piece:

    def chess_arith(square, vec, steps):
        file = "abcdefgh".index(square[0]) + steps * vec[0]
        rank = "12345678".index(square[1]) + steps * vec[1]
        if file in range(0, 8) and rank in range(0, 8):
            return "abcdefgh"[file] + "12345678"[rank]
        else:
            return None

    def rook(square):
        target = []
        for vec in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            direc = []
            for steps in range(1, 8):
                des = Piece.chess_arith(square, vec, steps)
                if des:
                    direc.append(des)
                else:
                    break
            if direc != []:
                target.append(direc)
        return target

    def knight(square):
        target = []
        file, rank = "abcdefgh".index(square[0]), "12345678".index(square[1])
        for i in [
            (file + 2, rank + 1),
            (file + 2, rank - 1),
            (file - 2, rank + 1),
            (file - 2, rank - 1),
            (file + 1, rank + 2),
            (file + 1, rank - 2),
            (file - 1, rank + 2),
            (file - 1, rank - 2),
        ]:
            if i[0] in range(0, 8) and i[1] in range(0, 8):
                target.append("abcdefgh"[i[0]] + "12345678"[i[1]])
        return target

    def biship(square):
        target = []
        for vec in [(1, 1), (-1, -1), (-1, 1), (1, -1)]:
            direc = []
            for steps in range(1, 8):
                des = Piece.chess_arith(square, vec, steps)
                if des:
                    direc.append(des)
                else:
                    break
            if direc != []:
                target.append(direc)
        return target

    def queen(square):
        target = []
        for vec in [
            (1, 1),
            (-1, -1),
            (-1, 1),
            (1, -1),
            (-1, 0),
            (1, 0),
            (0, -1),
            (0, 1),
        ]:
            direc = []
            for steps in range(1, 8):
                des = Piece.chess_arith(square, vec, steps)
                if des:
                    direc.append(des)
                else:
                    break
            if direc != []:
                target.append(direc)
        return target

    def king(square):
        target = []
        for vec in [
            (1, 1),
            (-1, -1),
            (-1, 1),
            (1, -1),
            (-1, 0),
            (1, 0),
            (0, -1),
            (0, 1),
        ]:
            _target = Piece.chess_arith(square, vec, 1)
            if _target:
                target.append(_target)
        return target

    def b_pawn(square):
        target = []
        straight = []
        capture = []

        des = Piece.chess_arith(square, (0, -1), 1)
        straight.append(des)

        if square[1] == "7":
            straight.append(Piece.chess_arith(square, (0, -1), 2))

        for vec in [(-1, -1), (1, -1)]:
            _target = Piece.chess_arith(square, vec, 1)
            if _target:
                capture.append(_target)

        target.append(straight)
        target.append(capture)
        return target

    def w_pawn(square):
        target = []
        straight = []
        capture = []

        straight.append(Piece.chess_arith(square, (0, 1), 1))

        if square[1] == "2":
            straight.append(Piece.chess_arith(square, (0, 1), 2))

        for vec in [(-1, 1), (1, 1)]:
            _target = Piece.chess_arith(square, vec, 1)
            if _target:
                capture.append(_target)

        target.append(straight)
        target.append(capture)
        return target


class ChessLib:
    def __init__(self):
        self.chess_dict = self.gen_chess_dict()

    def gen_chess_dict(self):

        target_dict = {}
        for i in "RNBQKPrnbqkp":
            target_dict[i] = {}

        squares = []
        for file in "abcdefgh":
            for rank in "12345678":
                squares.append(file + rank)

        for i in squares:
            target_dict["R"][i] = Piece.rook(i)
            target_dict["N"][i] = Piece.knight(i)
            target_dict["B"][i] = Piece.biship(i)
            target_dict["Q"][i] = Piece.queen(i)
            target_dict["K"][i] = Piece.king(i)
            target_dict["r"][i] = Piece.rook(i)
            target_dict["n"][i] = Piece.knight(i)
            target_dict["b"][i] = Piece.biship(i)
            target_dict["q"][i] = Piece.queen(i)
            target_dict["k"][i] = Piece.king(i)
            if i[1] not in "18":
                target_dict["P"][i] = Piece.w_pawn(i)
                target_dict["p"][i] = Piece.b_pawn(i)

        blank = {}
        for i in squares:
            blank[i] = {}
            resi = [rank + i[1] for rank in "abcdefgh"["abcdefgh".index(i[0]) :]]
            for j in range(len(resi)):
                blank[i][str(j + 1)] = resi[: j + 1]

        castle = {
            "K": [["e1", "f1", "g1"], ["f1", "g1"]],
            "Q": [["e1", "d1", "c1"], ["b1", "d1", "c1"]],
            "k": [["e8", "f8", "g8"], ["f8", "g8"]],
            "q": [["e8", "d8", "c8"], ["b8", "d8", "c8"]],
        }

        castle_move = {
            "K": {"O-O": ["e1", "g1"], "O-O-O": ["e1", "c1"]},
            "k": {"O-O": ["e8", "g8"], "O-O-O": ["e8", "c8"]},
            "R": {"O-O": ["h1", "f1"], "O-O-O": ["a1", "d1"]},
            "r": {"O-O": ["h8", "f8"], "O-O-O": ["a8", "d8"]},
        }

        passers = [
            "a3",
            "b3",
            "c3",
            "d3",
            "e3",
            "f3",
            "g3",
            "h3",
            "a6",
            "b6",
            "c6",
            "d6",
            "e6",
            "f6",
            "g6",
            "h6",
        ]

        passer_nbr = {
            "a3": ["b4"],
            "b3": ["a4", "c4"],
            "c3": ["b4", "d4"],
            "d3": ["c4", "e4"],
            "e3": ["d4", "f4"],
            "f3": ["e4", "g4"],
            "g3": ["f4", "h4"],
            "h3": ["g4"],
            "a6": ["b5"],
            "b6": ["a5", "c5"],
            "c6": ["b5", "d5"],
            "d6": ["c5", "e5"],
            "e6": ["d5", "f5"],
            "f6": ["e5", "g5"],
            "g6": ["f5", "h5"],
            "h6": ["g5"],
        }
        passer_pawn = {
            "a3": "a4",
            "b3": "b4",
            "c3": "c4",
            "d3": "d4",
            "e3": "e4",
            "f3": "f4",
            "g3": "g4",
            "h3": "h4",
            "a6": "a5",
            "b6": "b5",
            "c6": "c5",
            "d6": "d5",
            "e6": "e5",
            "f6": "f5",
            "g6": "g5",
            "h6": "h5",
        }

        return {
            "target_dict": target_dict,
            "blank": blank,
            "castle": castle,
            "castle_move": castle_move,
            "passers": passers,
            "passer_nbr": passer_nbr,
            "passer_pawn": passer_pawn,
        }

    def convert(self, fen):
        fen = fen.split()
        # a unchecked fen must have 6 parts
        if len(fen) != 6:
            return False
        else:
            chess = {
                "pieces": {},
                "blank": [],
                "w": [],
                "b": [],
                "turn": fen[1],
                "castle": [],
                "passer": fen[3],
                "half": int(fen[4]),
                "full": int(fen[5]),
                "K": "",
                "k": "",
            }

        # fen[0] is pieces, which is main part
        pieces = fen[0]
        packed = [
            list("eeeeeeee"),
            list("eeeeeeee"),
            list("eeeeeeee"),
            list("eeeeeeee"),
            list("eeeeeeee"),
            list("eeeeeeee"),
            list("eeeeeeee"),
            list("eeeeeeee"),
        ]

        kings = {"k": 0, "K": 0}
        rank, file = 8, 0

        # scan the pieces
        for i in pieces:
            if i == "/":
                rank -= 1
                if rank < 1 or file != 8:
                    return False
                file = 0

            elif i in "12345678":
                # alter "blank squares" in chess
                if file == 8:
                    return False
                square = "abcdefgh"[file] + "12345678"[rank - 1]
                file = file + int(i)
                if file > 8:
                    return False
                chess["blank"] += self.chess_dict["blank"][square][str(int(i))]

            elif i in "rbnqkpRBNQKP":
                # alter the packed when meets with a piece
                file += 1
                if file > 8:
                    return False
                packed[8 - rank][file - 1] = i

                # fill pieces and their squares in chess
                square = "abcdefgh"[file - 1] + "12345678"[rank - 1]

                # when meets with a king, fill in the information in chess
                if i in "kK":
                    kings[i] += 1
                    chess[i] = square

                chess["pieces"][square] = i
                if i in "rbnqkp":
                    chess["b"].append(square)
                else:
                    chess["w"].append(square)
            else:
                return False

        if rank != 1:
            # pieces must have exactly 7 "/"
            return False

        if not ((kings["K"] == 1) and (kings["k"] == 1)):
            # there are one and only one king of each side among pieces
            return False

        for p in "Pp":
            # pawns can not in the "line 1" or the "line 8"
            if p in packed[0] or p in packed[7]:
                return False

        # fen[1] shows which side to move
        if fen[1] not in "wb":
            return False
        else:
            chess["turn"] = fen[1]

        # fen[2] shows information of castling
        if fen[2] != "-":
            if packed[7][4] == "K":
                if packed[7][7] == "R":
                    chess["castle"].append("K")
                if packed[7][0] == "R":
                    chess["castle"].append("Q")

            if packed[0][4] == "k":
                if packed[0][7] == "r":
                    chess["castle"].append("k")
                if packed[0][0] == "r":
                    chess["castle"].append("q")

            if chess["castle"]:
                castling = "".join(chess["castle"])
            else:
                castling = "-"

            for i in fen[2]:
                if i not in castling:
                    return False

        # fen[3] shows information of passer
        passer = fen[3]
        if passer != "-":
            if passer not in self.chess_dict["passers"]:
                # passers only appears at certain squares
                return False
            else:
                # passer must has at least one opposite pawn neighbor
                flag = False
                pawn = "P" if chess["turn"] == "w" else "p"
                for square in self.chess_dict["passer_nbr"][passer]:
                    if square in chess[chess["turn"]]:
                        if chess["pieces"][square] == pawn:
                            flag = True
                            break
                if not flag:
                    return False

        return chess

    def is_reachable(self, chess, target, side):
        if target in chess[side]:
            return False

        for square in chess[side]:
            symbol = chess["pieces"][square]
            _targets = self.chess_dict["target_dict"][symbol][square]

            if symbol in "RBQrbq":
                for direc in _targets:
                    for i in direc:
                        if i == target:
                            return True
                        elif i not in chess["blank"]:
                            break

            elif symbol in "KNkn":
                for i in _targets:
                    if i == target:
                        return True

            else:
                for i in _targets[1]:
                    if i == target:
                        return True
        return False

    def is_checked(self, chess):
        result = {"w": False, "b": False}
        result["w"] = self.is_reachable(chess, chess["K"], "b")
        result["b"] = self.is_reachable(chess, chess["k"], "w")
        return result

    def gather_unrestrained_moves(self, chess):
        unrestrained = []
        oppo_side = "w" if chess["turn"] == "b" else "b"

        for square in chess[chess["turn"]]:
            symbol = chess["pieces"][square]
            targets = self.chess_dict["target_dict"][symbol][square]
            symbol = symbol.upper()

            if symbol in "RBQ":
                # Rock, Biship, Queen
                for direc in targets:
                    for i in direc:
                        if i in chess["blank"]:
                            unrestrained.append(symbol + square + i)
                        elif i in chess[oppo_side]:
                            unrestrained.append(symbol + square + "x" + i)
                            break
                        else:
                            break

            elif symbol == "K":
                # King
                for i in targets:
                    if i in chess["blank"]:
                        unrestrained.append("K" + square + i)
                    elif i in chess[oppo_side]:
                        unrestrained.append("K" + square + "x" + i)

            elif symbol == "N":
                # Knight
                for i in targets:
                    if i in chess["blank"]:
                        unrestrained.append("N" + square + i)
                    elif i in chess[oppo_side]:
                        unrestrained.append("N" + square + "x" + i)

            else:
                # pawns
                for i in targets[0]:
                    if i in chess["blank"]:
                        if i[1] in "18":
                            # pawn promotion
                            for asc in "RNBQ":
                                unrestrained.append("P" + square + i + "=" + asc)
                        else:
                            unrestrained.append("P" + square + i)
                    else:
                        break

                for i in targets[1]:
                    if i in chess[oppo_side]:
                        if i[1] in "18":
                            # pawn promotion
                            for asc in "RNBQ":
                                unrestrained.append("P" + square + "x" + i + "=" + asc)
                        else:
                            unrestrained.append("P" + square + "x" + i)
                    elif i == chess["passer"]:
                        unrestrained.append("P" + square + "x" + i)

        # castling
        symbols = "KQ" if oppo_side == "b" else "kq"
        infeasible = ""

        for i in symbols:
            if i not in chess["castle"]:
                infeasible += i
                continue

            for square in self.chess_dict["castle"][i][0]:
                if self.is_reachable(chess, square, oppo_side):
                    infeasible += i
                    break

            for square in self.chess_dict["castle"][i][1]:
                if square not in chess["blank"]:
                    infeasible += i
                    break

        if symbols[0] not in infeasible:
            unrestrained.append("O-O")
        if symbols[1] not in infeasible:
            unrestrained.append("O-O-O")

        return unrestrained

    def take_a_move(self, chess, move):
        chess = deepcopy(chess)
        oppo_side = "w" if chess["turn"] == "b" else "b"

        if move in ["O-O", "O-O-O"]:
            # castling kings
            if chess["turn"] == "w":
                symbol = "K"
                square, target = self.chess_dict["castle_move"][symbol][move]
                chess[symbol] = target

                for i in "KQ":
                    if i in chess["castle"]:
                        chess["castle"].remove(i)
            else:
                symbol = "k"
                square, target = self.chess_dict["castle_move"][symbol][move]
                chess["k"] = target

                for i in "kq":
                    if i in chess["castle"]:
                        chess["castle"].remove(i)

            chess["blank"].append(square)
            chess["blank"].remove(target)
            chess[chess["turn"]].append(target)
            chess[chess["turn"]].remove(square)
            del chess["pieces"][square]
            chess["pieces"][target] = symbol

            # castling rocks
            if chess["turn"] == "w":
                symbol = "R"
            else:
                symbol = "r"

            square, target = self.chess_dict["castle_move"][symbol][move]

            chess["blank"].append(square)
            chess["blank"].remove(target)
            chess[chess["turn"]].append(target)
            chess[chess["turn"]].remove(square)
            del chess["pieces"][square]
            chess["pieces"][target] = symbol

        else:
            # normal moves and eat passers
            if "x" in move:
                symbol, square, target = move[0], move[1:3], move[4:6]
            else:
                symbol, square, target = move[0], move[1:3], move[3:5]
                chess["blank"].remove(target)

            if chess["turn"] == "b":
                symbol = symbol.lower()

            chess[chess["turn"]].remove(square)
            chess[chess["turn"]].append(target)
            chess["blank"].append(square)
            del chess["pieces"][square]

            # alter target square in chess
            if "=" in move:
                # pawn promotion
                if chess["turn"] == "w":
                    chess["pieces"][target] = move[move.index("=") + 1]
                else:
                    chess["pieces"][target] = move[move.index("=") + 1].lower()
            else:
                chess["pieces"][target] = symbol

            if symbol in "Pp" and target == chess["passer"]:
                # eat passers-by
                _target = self.chess_dict["passer_pawn"][target]
                del chess["pieces"][_target]
                chess[oppo_side].remove(_target)

            elif "x" in move:
                chess[oppo_side].remove(target)

            if symbol in "Kk":
                # king position should be refreashed
                chess[symbol] = target

                # castling is not possible after the king has moved
                to_be_moved = "KQ" if symbol == "K" else "kq"
                for i in to_be_moved:
                    if i in chess["castle"]:
                        chess["castle"].remove(i)

            elif symbol in "Rr":
                # castling is segmentally not possible after the rock has moved
                if symbol == "R" and square == "a1" and "Q" in chess["castle"]:
                    chess["castle"].remove("Q")
                elif symbol == "R" and square == "h1" and "K" in chess["castle"]:
                    chess["castle"].remove("K")
                elif symbol == "r" and square == "a8" and "q" in chess["castle"]:
                    chess["castle"].remove("q")
                elif symbol == "r" and square == "h8" and "k" in chess["castle"]:
                    chess["castle"].remove("k")

        chess["passer"] = "-"

        if move[0] == "P" and move[2] == "2" and move[4] == "4":
            passer = move[1] + "3"
            for square in self.chess_dict["passer_nbr"][passer]:
                if square in chess[oppo_side]:
                    if chess["pieces"][square] == "p":
                        chess["passer"] = passer

        if move[0] == "p" and move[2] == "7" and move[4] == "5":
            passer = move[1] + "6"
            for square in self.chess_dict["passer_nbr"][passer]:
                if square in chess[oppo_side]:
                    if chess["pieces"][square] == passer:
                        chess["passer"] = passer

        # alter turn
        chess["turn"] = "b" if chess["turn"] == "w" else "w"

        # alter half
        if move[0] in "Pp" or "x" in move:
            chess["half"] = "0"
        else:
            chess["half"] = str(int(chess["half"]) + 1)

        # alter full
        if chess["turn"] == "w":
            chess["full"] = str(int(chess["full"]) + 1)

        return chess

    def format_moves(self, chess, unrestrained):
        formatted = {}
        repe = {}

        pieces = list(chess["pieces"].values())
        index = "RNBQK" if chess["turn"] == "w" else "rnbqk"
        for i in index:
            if i in pieces:
                pieces.remove(i)

        for file in "abcdefgh":
            for rank in "12345678":
                repe[file + rank] = []

        for move in unrestrained:
            if move in ["O-O-O", "O-O"]:
                formatted[move] = move
            elif move[0] == "P":
                if move[3] != "x":
                    formatted[move[3:]] = move
                else:
                    formatted[move[1] + "x" + move[4:]] = move
            elif move[0] == "K":
                # there is only one king
                formatted["K" + move[3:]] = move

            else:
                if move[0] in pieces:
                    if "+" in move or "#" in move:
                        repe[move[-3:-1]].append(move)
                    else:
                        repe[move[-2:]].append(move)
                else:
                    formatted[move[0] + move[3:]] = move

        for square in repe.keys():
            length = len(repe[square])

            if length == 1:
                move = repe[square][0]
                formatted[move[0] + move[3:]] = move

            elif length > 1:
                for i in repe[square]:
                    flag = ""

                    for j in repe[square]:
                        if i != j and i[0] == j[0]:
                            flag += "0"
                            if i[1] == j[1]:
                                flag += "1"

                    if "0" in flag:
                        if "1" in flag:
                            formatted[i] = i
                        else:
                            formatted[i[0:2] + i[3:]] = i
                    else:
                        formatted[i[0] + i[3:]] = i
        return formatted

    def gather_unchecked_moves(self, chess):
        unrestrained = self.gather_unrestrained_moves(chess)
        unchecked = []

        for move in unrestrained:
            _chess = self.take_a_move(chess, move)
            _is_checked = self.is_checked(_chess)
            oppo_side = "b" if chess["turn"] == "w" else "w"
            if _is_checked[chess["turn"]]:
                continue
            elif _is_checked[oppo_side]:
                unchecked.append(move + "+")
            else:
                unchecked.append(move)

        return self.format_moves(chess, unchecked)

    def gather_legal_moves(self, chess):
        unchecked = self.gather_unchecked_moves(chess)
        legal_moves = {}
        for move in unchecked.keys():
            if "+" in move:
                _chess = self.take_a_move(chess, unchecked[move])
                if not self.gather_unchecked_moves(_chess):
                    legal_moves[move[0:-1] + "#"] = unchecked[move][0:-1] + "#"
                else:
                    legal_moves[move] = unchecked[move]
            else:
                legal_moves[move] = unchecked[move]
        return legal_moves

    def gen_fen(self, chess):
        fen = ""
        for rank in "87654321":
            empty = 0
            for file in "abcdefgh":
                square = file + rank
                if square in chess["blank"]:
                    empty += 1
                else:
                    if empty:
                        fen += str(empty)
                        empty = 0
                    fen += chess["pieces"][square]
                if file == "h":
                    if empty:
                        fen += str(empty)
                    fen += "/"
                    empty = 0
        fen = fen[0:-1]

        if chess["castle"]:
            castling = "".join(chess["castle"])
        else:
            castling = "-"

        fen += " {} {} {} {} {}".format(
            chess["turn"], castling, chess["passer"], chess["half"], chess["full"]
        )
        return fen

    def judge(self, chess, move, move_history):

        status = ""

        if "#" in move:
            status = "checkmate"

        unchecked_moves = self.gather_unchecked_moves(chess)
        if unchecked_moves == {}:
            status = "stalemate"

        if chess["half"] == "100":
            status = "50 moves draw"

        # rep3 draw
        placement = list(move_history.values())
        placement.reverse()
        repeated = 0
        for i in placement:
            if i == fen:
                repeated += 1
                if repeated == 3:
                    status = "3rep draw"

        # insufficient force
        if len(chess["blank"]) == 62:
            status = "insufficient force"

        elif len(chess["blank"]) == 61:
            for i in chess["pieces"].values():
                if i in "BbNn":
                    status = "insufficient force"

        return status

    def is_game_unplayable(self, chess):

        if chess:
            turn = chess["turn"]
            oppo = "b" if turn == "w" else "w"
            is_checked = self.is_checked(chess)

            if is_checked[oppo]:
                return "illegal fen"
            else:
                if is_checked[turn]:
                    if not self.gather_unchecked_moves(chess):
                        return "checkmate"
                    else:
                        return False
                else:
                    if not self.gather_unchecked_moves(chess):
                        return "stalemate"
                    else:
                        return False
        else:
            return "illegal fen"


from time import sleep
from random import random


def engine(chess):
    sleep(0.3)
    cb = ChessLib()
    legal_moves = cb.gather_legal_moves(chess)
    capture = []
    check = []
    king = []
    others = []
    move = ""
    for i in list(legal_moves.keys()):
        if "x" in i:
            capture.append(i)
        elif "+" in i:
            check.append(i)
        elif "K" in i:
            king.append(i)
        else:
            others.append(i)

    if capture:
        if random() > 0.3:
            move = choice(capture)
    elif check:
        if random() > 0.2:
            move = choice(check)
    elif others:
        if random() > 0.5:
            move = choice(others)
    elif king:
        if random() > 0.9:
            move = choice(king)

    if move:
        return move, cb.take_a_move(chess, legal_moves[move])
    else:
        move = choice(list(legal_moves.keys()))
        return move, cb.take_a_move(chess, legal_moves[move])


if __name__ == "__main__":
    fen = "7k/7P/7K/8/3B4/8/8/8 b - - 1 1"
    cl = ChessLib()
    print(cl.is_game_unplayable(fen))
    # chess = cl.convert(fen)
    # print(chess)
    # unchecked = cl.gather_unchecked_moves(chess)
    # legal_moves = cl.gather_legal_moves(chess, unchecked)
    # print(legal_moves)

    # from vfunc import *

    # vfunc(cl.convert, (fen,))
