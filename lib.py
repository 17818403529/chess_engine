from time import time, sleep
import json
from copy import deepcopy
from random import choice
import os


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
            des = chess_arith(square, vec, steps)
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
            target.append("abcdefgh"[i[1]] + "12345678"[i[0]])
    return target


def biship(square):
    target = []
    for vec in [(1, 1), (-1, -1), (-1, 1), (1, -1)]:
        direc = []
        for steps in range(1, 8):
            des = chess_arith(square, vec, steps)
            if des:
                direc.append(des)
            else:
                break
        if direc != []:
            target.append(direc)
    return target


def queen(square):
    target = []
    for vec in [(1, 1), (-1, -1), (-1, 1), (1, -1), (-1, 0), (1, 0), (0, -1), (0, 1)]:
        direc = []
        for steps in range(1, 8):
            des = chess_arith(square, vec, steps)
            if des:
                direc.append(des)
            else:
                break
        if direc != []:
            target.append(direc)
    return target


def king(square):
    target = []
    for vec in [(1, 1), (-1, -1), (-1, 1), (1, -1), (-1, 0), (1, 0), (0, -1), (0, 1)]:
        _target = chess_arith(square, vec, 1)
        if _target:
            target.append(_target)
    return target


def b_pawn(square):
    target = []
    straight = []
    capture = []

    des = chess_arith(square, (0, -1), 1)
    straight.append(des)

    if square[1] == "7":
        straight.append(chess_arith(square, (0, -1), 2))

    for vec in [(-1, -1), (1, -1)]:
        _target = chess_arith(square, vec, 1)
        if _target:
            capture.append(_target)

    target.append(straight)
    target.append(capture)
    return target


def w_pawn(square):
    target = []
    straight = []
    capture = []

    des = chess_arith(square, (0, 1), 1)
    straight.append(des)

    if square[1] == "2":
        straight.append(chess_arith(square, (0, 1), 2))

    for vec in [(-1, 1), (1, 1)]:
        _target = chess_arith(square, vec, 1)
        if _target:
            capture.append(_target)

    target.append(straight)
    target.append(capture)
    return target


def gen_chess_dict():

    target_dict = {}
    for i in "RNBQKPrnbqkp":
        target_dict[i] = {}

    squares = []
    for hori in "abcdefgh":
        for vert in "12345678":
            squares.append(hori + vert)

    for i in squares:
        target_dict["R"][i] = rook(i)
        target_dict["N"][i] = knight(i)
        target_dict["B"][i] = biship(i)
        target_dict["Q"][i] = queen(i)
        target_dict["K"][i] = king(i)
        target_dict["P"][i] = w_pawn(i)
        target_dict["r"][i] = rook(i)
        target_dict["n"][i] = knight(i)
        target_dict["b"][i] = biship(i)
        target_dict["q"][i] = queen(i)
        target_dict["k"][i] = king(i)
        target_dict["p"][i] = b_pawn(i)

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

    return {
        "target_dict": target_dict,
        "blank": blank,
        "castle": castle,
        "passers": passers,
        "passer_nbr": passer_nbr,
    }


def convert(fen, chess_dict):
    fen = fen.split()
    board = {
        "blank": [],
        "w": [],
        "b": [],
        "pieces": {},
        "turn": fen[1],
        "castle": [],
        "passer": fen[3],
        "K": "",
        "k": "",
    }

    # a legal fen must have 6 parts
    if len(fen) != 6:
        return False

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
            square = "abcdefgh"[hori] + "12345678"[vert - 1]
            board["blank"] += chess_dict["blank"][square][str(int(i))]
            hori = hori + int(i)

        elif i in "rbnqkpRBNQKP":
            # alter the packed when meets with a piece
            hori += 1
            packed[8 - vert][hori - 1] = i
            if i in "kK":
                kings[i] += 1

            # fill pieces and their squares in board
            square = "abcdefgh"[hori - 1] + "12345678"[vert - 1]
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

    if board["castle"] == "":
        castling = "-"
    else:
        castling = "".join(board["castle"])

    if castling != fen[2]:
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
            pawn = "p" if board["turn"] == "w" else "P"
            for square in chess_dict["passer_nbr"]:
                if board["pieces"][square] == pawn:
                    flag = True
                    break
            if not flag:
                return False

    return board


fen = """
rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1
"""
chess_dict = gen_chess_dict()
board = convert(fen, chess_dict)
print(board)

# def show_fea_moves(board):
#     fea_moves = []
#     oppo_side = "w" if board["turn"] == "b" else "b"
#     for sqr in board[board["turn"]]:
#         symbol = board["pieces"][sqr]
#         _symbol = symbol.upper()
#         if symbol in "Pp":
#             _fea_moves = fea[symbol][sqr]
#         else:
#             # print(board[board["turn"]])
#             _fea_moves = fea[symbol.upper()][sqr]

#         if symbol in "RBQrbq":
#             # Rock, Biship, Queen
#             for direc in _fea_moves:
#                 for i in direc:
#                     if i in board["blank"]:
#                         fea_moves.append(_symbol + sqr + i)
#                     elif i in board[oppo_side]:
#                         fea_moves.append(_symbol + sqr + "x" + i)
#                         break
#                     else:
#                         break

#         elif symbol in "Kk":
#             # King
#             for i in _fea_moves:
#                 if i in board["blank"]:
#                     fea_moves.append(_symbol + sqr + i)
#                 elif i in board[oppo_side]:
#                     fea_moves.append(_symbol + sqr + "x" + i)

#         elif symbol in "Nn":
#             # Knight
#             for i in _fea_moves:
#                 if i in board["blank"]:
#                     fea_moves.append(_symbol + sqr + i)
#                 elif i in board[oppo_side]:
#                     fea_moves.append(_symbol + sqr + "x" + i)

#         else:
#             # pawns
#             for i in _fea_moves[0]:
#                 if i in board["blank"]:
#                     if i[1] in "18":
#                         # pawn promotion
#                         for asc in "RNBQ":
#                             fea_moves.append(_symbol + sqr + i + "=" + asc)
#                     else:
#                         fea_moves.append(_symbol + sqr + i)
#                 else:
#                     break

#             for i in _fea_moves[1]:
#                 if i in board[oppo_side]:
#                     if i[1] in "18":
#                         # pawn promotion
#                         for asc in "RNBQ":
#                             fea_moves.append(_symbol + sqr + "x" + i + "=" + asc)
#                     else:
#                         fea_moves.append(_symbol + sqr + "x" + i)
#                 elif i == board["passer"]:
#                     fea_moves.append(_symbol + sqr + "x" + i)

#     fea_moves += can_castle(board, oppo_side)
#     return fea_moves


# def check(board):
#     is_checked = {"w": False, "b": False}
#     is_checked["w"] = is_reachable(board, board["K"], "b")
#     is_checked["b"] = is_reachable(board, board["k"], "w")
#     return is_checked


# def is_reachable(board, target, side):
#     if target in board[side]:
#         return False

#     for sqr in board[side]:
#         symbol = board["pieces"][sqr]

#         if symbol in "Pp":
#             fea_moves = fea[symbol][sqr]
#         else:
#             fea_moves = fea[symbol.upper()][sqr]

#         if symbol in "RBQrbq":
#             for direc in fea_moves:
#                 for i in direc:
#                     if i == target:
#                         return True
#                     elif i not in board["blank"]:
#                         break

#         elif symbol in "KNkn":
#             for i in fea_moves:
#                 if i == target:
#                     return True

#         else:
#             for i in fea_moves[1]:
#                 if i == target:
#                     return True
#     return False


# def can_castle(board, oppo_side):
#     own_side = "b" if oppo_side == "w" else "w"
#     symbol = "KQ" if oppo_side == "b" else "kq"
#     infea = ""

#     for i in symbol:
#         if i not in board["castle"]:
#             infea += i
#             continue

#         for sqr in fea["castle"][i][0]:
#             if is_reachable(board, sqr, oppo_side):
#                 infea += i
#                 break

#         for sqr in fea["castle"][i][1]:
#             if sqr not in board["blank"]:
#                 infea += i
#                 break

#     result = []
#     if symbol[0] not in infea:
#         result.append("O-O")
#     if symbol[1] not in infea:
#         result.append("O-O-O")

#     return result


# def take_a_move(board, move):
#     board = deepcopy(board)
#     oppo_side = "w" if board["turn"] == "b" else "b"

#     if move in ["O-O", "O-O-O"]:
#         # castling kings
#         if board["turn"] == "w":
#             symbol = "K"
#             if move == "O-O":
#                 sqr, target = "e1", "g1"
#             else:
#                 sqr, target = "e1", "c1"

#             for i in "KQ":
#                 if i in board["castle"]:
#                     board["castle"].remove(i)
#         else:
#             symbol = "k"
#             if move == "O-O":
#                 sqr, target = "e8", "g8"
#             else:
#                 sqr, target = "e8", "c8"

#             for i in "kq":
#                 if i in board["castle"]:
#                     board["castle"].remove(i)
#         board[symbol] = target

#         board["blank"].append(sqr)
#         board["blank"].remove(target)
#         board[board["turn"]].append(target)
#         # print(move)
#         board[board["turn"]].remove(sqr)
#         del board["pieces"][sqr]
#         board["pieces"][target] = symbol

#         # castling rocks
#         if board["turn"] == "w":
#             symbol = "R"
#             if move == "O-O":
#                 sqr, target = "h1", "f1"
#             else:
#                 sqr, target = "a1", "d1"
#         else:
#             symbol = "r"
#             if move == "O-O":
#                 sqr, target = "h8", "f8"
#             else:
#                 sqr, target = "a8", "d8"

#         board["blank"].append(sqr)
#         board["blank"].remove(target)
#         board[board["turn"]].append(target)
#         board[board["turn"]].remove(sqr)
#         del board["pieces"][sqr]
#         board["pieces"][target] = symbol

#     else:
#         # normal moves and eat passers
#         if "x" in move:
#             symbol, sqr, target = move[0], move[1:3], move[4:6]
#         else:
#             symbol, sqr, target = move[0], move[1:3], move[3:5]
#             board["blank"].remove(target)

#         board[board["turn"]].remove(sqr)
#         board[board["turn"]].append(target)

#         board["blank"].append(sqr)

#         del board["pieces"][sqr]

#         if "=" in move:
#             # pawn promotion
#             board["pieces"][target] = move[-1]
#         else:
#             if board["turn"] == "w":
#                 board["pieces"][target] = symbol
#             else:
#                 board["pieces"][target] = symbol.lower()

#         if symbol in "Pp" and target == board["passer"]:
#             # eat passers-by
#             if board["turn"] == "w":
#                 passer = target[0] + "5"
#             else:
#                 passer = target[0] + "4"
#             del board["pieces"][passer]
#             board[oppo_side].remove(passer)

#         elif "x" in move:
#             board[oppo_side].remove(target)

#         if symbol == "K":
#             # castling is not possible after the king has moved
#             if board["turn"] == "w":
#                 board["K"] = target
#             else:
#                 board["k"] = target

#             if board["turn"] == "w":
#                 for i in "KQ":
#                     if i in board["castle"]:
#                         board["castle"].remove(i)
#             else:
#                 for i in "kq":
#                     if i in board["castle"]:
#                         board["castle"].remove(i)

#         elif symbol in "Rr":
#             # castling is segmentally not possible after the rock has moved
#             if symbol == "R" and sqr == "a1" and "Q" in board["castle"]:
#                 board["castle"].remove("Q")
#             elif symbol == "R" and sqr == "h1" and "K" in board["castle"]:
#                 board["castle"].remove("K")
#             elif symbol == "r" and sqr == "a8" and "q" in board["castle"]:
#                 board["castle"].remove("q")
#             elif symbol == "r" and sqr == "h8" and "k" in board["castle"]:
#                 board["castle"].remove("k")

#     board["passer"] = "-"

#     if move[0] == "P" and move[2] == "2" and move[4] == "4":
#         board["passer"] = move[1] + "3"

#     if move[0] == "p" and move[2] == "7" and move[4] == "5":
#         board["passer"] = move[1] + "6"

#     board["turn"] = "b" if board["turn"] == "w" else "w"
#     return board


# def format_moves(board, fea_moves):
#     formatted = {}
#     repe = {}

#     test = list(board["pieces"].values())
#     index = "RNBQK" if board["turn"] == "w" else "rnbqk"
#     for i in index:
#         if i in test:
#             test.remove(i)

#     for hori in "abcdefgh":
#         for vert in "12345678":
#             repe[hori + vert] = []

#     for move in fea_moves:
#         if move in ["O-O-O", "O-O"]:
#             formatted[move] = move
#         elif move[0] == "P":
#             if move[3] != "x":
#                 formatted[move] = move[3:]
#             else:
#                 formatted[move] = move[1] + "x" + move[4:]
#         elif move[0] == "K":
#             formatted[move] = "K" + move[3:]

#         else:
#             if move[0] in test:
#                 if "+" in move:
#                     repe[move[-3:-1]].append(move)
#                 else:
#                     repe[move[-2:]].append(move)
#             else:
#                 formatted[move] = move[0] + move[3:]

#     for sqr in repe.keys():
#         length = len(repe[sqr])

#         if length == 1:
#             move = repe[sqr][0]
#             formatted[move] = move[0] + move[3:]

#         elif length > 1:
#             for i in repe[sqr]:
#                 flag = ""

#                 for j in repe[sqr]:
#                     if i != j and i[0] == j[0]:
#                         flag += "0"
#                         if i[1] == j[1]:
#                             flag += "1"

#                 if "0" in flag:
#                     if "1" in flag:
#                         formatted[i] = i
#                     else:
#                         formatted[i] = i[0:2] + i[3:]
#                 else:
#                     formatted[i] = i[0] + i[3:]
#     return formatted


# def show_legal_moves(fen):
#     board = conv_fen(fen)
#     fea_moves = show_fea_moves(board)
#     legal_moves = []

#     for move in fea_moves:
#         _board = take_a_move(board, move)
#         is_checked = check(_board)
#         oppo_side = "b" if board["turn"] == "w" else "w"
#         if is_checked[board["turn"]]:
#             continue
#         elif is_checked[oppo_side]:
#             legal_moves.append(move + "+")
#         else:
#             legal_moves.append(move)

#     abbr = format_moves(board, legal_moves)
#     return abbr


# def gen_fen(board):
#     fen = ""
#     for hori in "87654321":
#         empty = 0
#         for vert in "abcdefgh":
#             sqr = vert + hori
#             if sqr in board["blank"]:
#                 empty += 1
#             else:
#                 if empty:
#                     fen += str(empty)
#                     empty = 0
#                 if sqr in board["b"]:
#                     fen += board["pieces"][sqr].lower()
#                 else:
#                     fen += board["pieces"][sqr]
#             if vert == "h":
#                 if empty:
#                     fen += str(empty)
#                 fen += "/"
#                 empty = 0
#     fen = fen[0:-1]
#     fen += " {} {} {} {} {}".format(
#         board["turn"], "".join(board["castle"]), board["passer"], 0, 1
#     )

#     return fen


# def engine(fen):
#     sleep(0.25)
#     abbr = show_legal_moves(fen)
#     move = choice(list(abbr.values()))
#     return move


# # fen =  "rn3bnr/pp1ppk1p/2b2p2/6pP/1Pp1P3/3P1QP1/P1P4P/RNB1KBNR w KQ g6 0 1"
# # while True:
# #     print(engine(fen))
