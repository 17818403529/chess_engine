from copy import deepcopy
from random import choice


class Piece:

    def chess_arith(square, vec, steps):
        hori = "abcdefgh".index(square[0]) + steps * vec[0]
        vert = "12345678".index(square[1]) + steps * vec[1]
        if hori in range(0, 8) and vert in range(0, 8):
            return "abcdefgh"[hori] + "12345678"[vert]
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
        hori, vert = "abcdefgh".index(square[0]), "12345678".index(square[1])
        for i in [
            (hori + 2, vert + 1),
            (hori + 2, vert - 1),
            (hori - 2, vert + 1),
            (hori - 2, vert - 1),
            (hori + 1, vert + 2),
            (hori + 1, vert - 2),
            (hori - 1, vert + 2),
            (hori - 1, vert - 2),
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


class Chess:

    def gen_chess_dict():

        target_dict = {}
        for i in "RNBQKPrnbqkp":
            target_dict[i] = {}

        squares = []
        for hori in "abcdefgh":
            for vert in "12345678":
                squares.append(hori + vert)

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
            resi = [vert + i[1] for vert in "abcdefgh"["abcdefgh".index(i[0]) :]]
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

    def convert(fen, chess_dict):
        fen = fen.split()
        # a legal fen must have 6 parts
        if len(fen) != 6:
            return False
        else:
            board = {
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
        vert, hori = 8, 0

        # scan the pieces
        for i in pieces:
            if i == "/":
                vert -= 1
                if vert < 1 or hori != 8:
                    return False
                hori = 0

            elif i in "12345678":
                # alter "blank squares" in board
                if hori == 8:
                    return False
                square = "abcdefgh"[hori] + "12345678"[vert - 1]
                hori = hori + int(i)
                if hori > 8:
                    return False
                board["blank"] += chess_dict["blank"][square][str(int(i))]

            elif i in "rbnqkpRBNQKP":
                # alter the packed when meets with a piece
                hori += 1
                if hori > 8:
                    return False
                packed[8 - vert][hori - 1] = i

                # fill pieces and their squares in board
                square = "abcdefgh"[hori - 1] + "12345678"[vert - 1]

                # when meets with a king, fill in the information in board
                if i in "kK":
                    kings[i] += 1
                    board[i] = square

                board["pieces"][square] = i
                if i in "rbnqkp":
                    board["b"].append(square)
                else:
                    board["w"].append(square)
            else:
                return False

        if vert != 1:
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
            board["turn"] = fen[1]

        # fen[2] shows information of castling
        if fen[2] != "-":
            if packed[7][4] == "K":
                if packed[7][7] == "R":
                    board["castle"].append("K")
                if packed[7][0] == "R":
                    board["castle"].append("Q")

            if packed[0][4] == "k":
                if packed[0][7] == "r":
                    board["castle"].append("k")
                if packed[0][0] == "r":
                    board["castle"].append("q")

            if board["castle"]:
                castling = "".join(board["castle"])
            else:
                castling = "-"

            for i in fen[2]:
                if i not in castling:
                    return False

        # fen[3] shows information of passer
        passer = fen[3]
        if passer != "-":
            if passer not in chess_dict["passers"]:
                # passers only appears at certain squares
                return False
            else:
                # passer must has at least one opposite pawn neighbor
                flag = False
                pawn = "P" if board["turn"] == "w" else "p"
                for square in chess_dict["passer_nbr"][passer]:
                    if square in board[board["turn"]]:
                        if board["pieces"][square] == pawn:
                            flag = True
                            break
                if not flag:
                    return False

        return board

    def is_reachable(board, target, side, chess_dict):
        if target in board[side]:
            return False

        for square in board[side]:
            symbol = board["pieces"][square]
            _targets = chess_dict["target_dict"][symbol][square]

            if symbol in "RBQrbq":
                for direc in _targets:
                    for i in direc:
                        if i == target:
                            return True
                        elif i not in board["blank"]:
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

    def is_checked(board, chess_dict):
        result = {"w": False, "b": False}
        result["w"] = Chess.is_reachable(board, board["K"], "b", chess_dict)
        result["b"] = Chess.is_reachable(board, board["k"], "w", chess_dict)
        return result

    def gather_unchecked_moves(board, chess_dict):
        unchecked = []
        oppo_side = "w" if board["turn"] == "b" else "b"

        for square in board[board["turn"]]:
            symbol = board["pieces"][square]
            targets = chess_dict["target_dict"][symbol][square]
            symbol = symbol.upper()

            if symbol in "RBQ":
                # Rock, Biship, Queen
                for direc in targets:
                    for i in direc:
                        if i in board["blank"]:
                            unchecked.append(symbol + square + i)
                        elif i in board[oppo_side]:
                            unchecked.append(symbol + square + "x" + i)
                            break
                        else:
                            break

            elif symbol == "K":
                # King
                for i in targets:
                    if i in board["blank"]:
                        unchecked.append("K" + square + i)
                    elif i in board[oppo_side]:
                        unchecked.append("K" + square + "x" + i)

            elif symbol == "N":
                # Knight
                for i in targets:
                    if i in board["blank"]:
                        unchecked.append("N" + square + i)
                    elif i in board[oppo_side]:
                        unchecked.append("N" + square + "x" + i)

            else:
                # pawns
                for i in targets[0]:
                    if i in board["blank"]:
                        if i[1] in "18":
                            # pawn promotion
                            for asc in "RNBQ":
                                unchecked.append("P" + square + i + "=" + asc)
                        else:
                            unchecked.append("P" + square + i)
                    else:
                        break

                for i in targets[1]:
                    if i in board[oppo_side]:
                        if i[1] in "18":
                            # pawn promotion
                            for asc in "RNBQ":
                                unchecked.append("P" + square + "x" + i + "=" + asc)
                        else:
                            unchecked.append("P" + square + "x" + i)
                    elif i == board["passer"]:
                        unchecked.append("P" + square + "x" + i)

        # castling
        symbols = "KQ" if oppo_side == "b" else "kq"
        infeasible = ""

        for i in symbols:
            if i not in board["castle"]:
                infeasible += i
                continue

            for square in chess_dict["castle"][i][0]:
                if Chess.is_reachable(board, square, oppo_side, chess_dict):
                    infeasible += i
                    break

            for square in chess_dict["castle"][i][1]:
                if square not in board["blank"]:
                    infeasible += i
                    break

        result = []
        if symbols[0] not in infeasible:
            unchecked.append("O-O")
        if symbols[1] not in infeasible:
            unchecked.append("O-O-O")

        return unchecked

    def take_a_move(board, move, chess_dict):
        board = deepcopy(board)
        oppo_side = "w" if board["turn"] == "b" else "b"

        if move in ["O-O", "O-O-O"]:
            # castling kings
            if board["turn"] == "w":
                symbol = "K"
                square, target = chess_dict["castle_move"][symbol][move]
                board[symbol] = target

                for i in "KQ":
                    if i in board["castle"]:
                        board["castle"].remove(i)
            else:
                symbol = "k"
                square, target = chess_dict["castle_move"][symbol][move]
                board["k"] = target

                for i in "kq":
                    if i in board["castle"]:
                        board["castle"].remove(i)

            board["blank"].append(square)
            board["blank"].remove(target)
            board[board["turn"]].append(target)
            board[board["turn"]].remove(square)
            del board["pieces"][square]
            board["pieces"][target] = symbol

            # castling rocks
            if board["turn"] == "w":
                symbol = "R"
            else:
                symbol = "r"

            square, target = chess_dict["castle_move"][symbol][move]

            board["blank"].append(square)
            board["blank"].remove(target)
            board[board["turn"]].append(target)
            board[board["turn"]].remove(square)
            del board["pieces"][square]
            board["pieces"][target] = symbol

        else:
            # normal moves and eat passers
            if "x" in move:
                symbol, square, target = move[0], move[1:3], move[4:6]
            else:
                symbol, square, target = move[0], move[1:3], move[3:5]
                board["blank"].remove(target)

            if board["turn"] == "b":
                symbol = symbol.lower()

            board[board["turn"]].remove(square)
            board[board["turn"]].append(target)
            board["blank"].append(square)
            del board["pieces"][square]

            # alter target square in board
            if "=" in move:
                # pawn promotion
                if board["turn"] == "w":
                    board["pieces"][target] = move[move.index("=") + 1]
                else:
                    board["pieces"][target] = move[move.index("=") + 1].lower()
            else:
                board["pieces"][target] = symbol

            if symbol in "Pp" and target == board["passer"]:
                # eat passers-by
                _target = chess_dict["passer_pawn"][target]
                del board["pieces"][_target]
                board[oppo_side].remove(_target)

            elif "x" in move:
                board[oppo_side].remove(target)

            if symbol in "Kk":
                # king position should be refreashed
                board[symbol] = target

                # castling is not possible after the king has moved
                to_be_moved = "KQ" if symbol == "K" else "kq"
                for i in to_be_moved:
                    if i in board["castle"]:
                        board["castle"].remove(i)

            elif symbol in "Rr":
                # castling is segmentally not possible after the rock has moved
                if symbol == "R" and square == "a1" and "Q" in board["castle"]:
                    board["castle"].remove("Q")
                elif symbol == "R" and square == "h1" and "K" in board["castle"]:
                    board["castle"].remove("K")
                elif symbol == "r" and square == "a8" and "q" in board["castle"]:
                    board["castle"].remove("q")
                elif symbol == "r" and square == "h8" and "k" in board["castle"]:
                    board["castle"].remove("k")

        board["passer"] = "-"

        if move[0] == "P" and move[2] == "2" and move[4] == "4":
            passer = move[1] + "3"
            for square in chess_dict["passer_nbr"][passer]:
                if square in board[oppo_side]:
                    if board["pieces"][square] == "p":
                        board["passer"] = passer

        if move[0] == "p" and move[2] == "7" and move[4] == "5":
            passer = move[1] + "6"
            for square in chess_dict["passer_nbr"][passer]:
                if square in board[oppo_side]:
                    if board["pieces"][square] == passer:
                        board["passer"] = passer

        # alter turn
        board["turn"] = "b" if board["turn"] == "w" else "w"

        # alter half
        if move[0] in "Pp" or "x" in move:
            board["half"] = "0"
        else:
            board["half"] = str(int(board["half"]) + 1)

        # alter full
        if board["turn"] == "w":
            board["full"] = str(int(board["full"]) + 1)

        return board

    def format_moves(board, unchecked):
        formatted = {}
        repe = {}

        pieces = list(board["pieces"].values())
        index = "RNBQK" if board["turn"] == "w" else "rnbqk"
        for i in index:
            if i in pieces:
                pieces.remove(i)

        for hori in "abcdefgh":
            for vert in "12345678":
                repe[hori + vert] = []

        for move in unchecked:
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
                    if "+" in move:
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

    def gather_legal_moves(board, chess_dict):
        unchecked = Chess.gather_unchecked_moves(board, chess_dict)
        legal_moves = []

        for move in unchecked:
            _board = Chess.take_a_move(board, move, chess_dict)
            _is_checked = Chess.is_checked(_board, chess_dict)
            oppo_side = "b" if board["turn"] == "w" else "w"
            if _is_checked[board["turn"]]:
                continue
            elif _is_checked[oppo_side]:
                legal_moves.append(move + "+")
            else:
                legal_moves.append(move)

        return Chess.format_moves(board, legal_moves)

    def gen_fen(board):
        fen = ""
        for vert in "87654321":
            empty = 0
            for hori in "abcdefgh":
                square = hori + vert
                if square in board["blank"]:
                    empty += 1
                else:
                    if empty:
                        fen += str(empty)
                        empty = 0
                    fen += board["pieces"][square]
                if hori == "h":
                    if empty:
                        fen += str(empty)
                    fen += "/"
                    empty = 0
        fen = fen[0:-1]

        if board["castle"]:
            castling = "".join(board["castle"])
        else:
            castling = "-"

        fen += " {} {} {} {} {}".format(
            board["turn"], castling, board["passer"], board["half"], board["full"]
        )
        return fen


from time import sleep
from random import random


def engine(board, chess_dict):
    legal_moves = Chess.gather_legal_moves(board, chess_dict)
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
        return move
    else:
        return choice(list(legal_moves.keys()))


if __name__ == "__main__":
    fen = "r4b1r/1b2k3/p1p1pn1n/5pN1/QP2P1Pp/4P1RP/P2K4/RNB2B2 w - - 1 2"

    chess_dict = Chess.gen_chess_dict()
    board = Chess.convert(fen, chess_dict)
    print(board)
    # legal_moves = gather_legal_moves(board, chess_dict)
    # print(legal_moves)

    # from vfunc import *
    # vfunc(gen_fen,(board,))