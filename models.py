from time import time, sleep
import json
from copy import deepcopy
from random import choice
import os


def cal_pos(pos, vec, steps):
    col = "abcdefgh".index(pos[0]) + steps * vec[0]
    row = "12345678".index(pos[1]) + steps * vec[1]
    if col in range(0, 8) and row in range(0, 8):
        return "abcdefgh"[col] + "12345678"[row]
    else:
        return None


def rook(pos):
    fea = []
    for vec in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
        _fea = []
        for steps in range(1, 8):
            des = cal_pos(pos, vec, steps)
            if des:
                _fea.append(des)
            else:
                break
        if _fea != []:
            fea.append(_fea)
    return fea


def biship(pos):
    fea = []
    for vec in [(1, 1), (-1, -1), (-1, 1), (1, -1)]:
        _fea = []
        for steps in range(1, 8):
            des = cal_pos(pos, vec, steps)
            if des:
                _fea.append(des)
            else:
                break
        if _fea != []:
            fea.append(_fea)
    return fea


def queen(pos):
    fea = []
    for vec in [(1, 1), (-1, -1), (-1, 1), (1, -1), (-1, 0), (1, 0), (0, -1), (0, 1)]:
        _fea = []
        for steps in range(1, 8):
            des = cal_pos(pos, vec, steps)
            if des:
                _fea.append(des)
            else:
                break
        if _fea != []:
            fea.append(_fea)
    return fea


def king(pos):
    fea = []
    for vec in [(1, 1), (-1, -1), (-1, 1), (1, -1), (-1, 0), (1, 0), (0, -1), (0, 1)]:
        des = cal_pos(pos, vec, 1)
        if des:
            fea.append(des)
    return fea


def knight(pos):
    fea = []
    col, row = "abcdefgh".index(pos[0]), "12345678".index(pos[1])
    for des in [
        (row + 2, col + 1),
        (row + 2, col - 1),
        (row - 2, col + 1),
        (row - 2, col - 1),
        (row + 1, col + 2),
        (row + 1, col - 2),
        (row - 1, col + 2),
        (row - 1, col - 2),
    ]:
        if des[0] in range(0, 8) and des[1] in range(0, 8):
            fea.append("abcdefgh"[des[1]] + "12345678"[des[0]])
    return fea


def b_pawn(pos):
    fea = []
    straight = []
    capture = []

    des = cal_pos(pos, (0, -1), 1)
    straight.append(des)

    if pos[1] == "7":
        des = cal_pos(pos, (0, -1), 2)
        straight.append(des)

    for vec in [(-1, -1), (1, -1)]:
        des = cal_pos(pos, vec, 1)
        if des:
            capture.append(des)

    fea.append(straight)
    fea.append(capture)
    return fea


def w_pawn(pos):
    fea = []
    straight = []
    capture = []

    des = cal_pos(pos, (0, 1), 1)
    straight.append(des)

    if pos[1] == "2":
        des = cal_pos(pos, (0, 1), 2)
        straight.append(des)

    for vec in [(-1, 1), (1, 1)]:
        des = cal_pos(pos, vec, 1)
        if des:
            capture.append(des)

    fea.append(straight)
    fea.append(capture)
    return fea


fea = {"R": {}, "B": {}, "N": {}, "K": {}, "Q": {}, "p": {}, "P": {}}

for row in "12345678":
    for col in "abcdefgh":
        pos = col + row
        fea["R"][pos] = rook(pos)
        fea["B"][pos] = biship(pos)
        fea["Q"][pos] = queen(pos)
        fea["K"][pos] = king(pos)
        fea["N"][pos] = knight(pos)

for row in "234567":
    for col in "abcdefgh":
        pos = col + row
        fea["p"][pos] = b_pawn(pos)
        fea["P"][pos] = w_pawn(pos)

fea["blank"] = {}
for row in "12345678":
    for col in "abcdefgh":
        pos = col + row
        fea["blank"][pos] = {}
        resi = []
        for i in range("abcdefgh".index(col), 8):
            resi.append("abcdefgh"[i] + row)
        for i in range(len(resi)):
            fea["blank"][pos][str(i + 1)] = resi[: i + 1]

fea["castle"] = {
    "K": [["e1", "f1", "g1"], ["f1", "g1"]],
    "Q": [["e1", "d1", "c1"], ["b1", "d1", "c1"]],
    "k": [["e8", "f8", "g8"], ["f8", "g8"]],
    "q": [["e8", "d8", "c8"], ["b8", "d8", "c8"]],
}


def is_fen_legal(fen):
    fen = fen.split()
    if len(fen) != 6:
        return False

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
    row = ""
    kings = {"k": 0, "K": 0}
    hori, vert = 8, 0

    for i in fen[0]:
        if i == "/":
            hori -= 1
            if hori < 1 or vert != 8:
                return False
            vert = 0
            row = ""
        elif i in "12345678":
            vert = vert + int(i)
        elif i in "rbnqkpRBNQKP":
            vert += 1
            packed[8 - hori][vert - 1] = i
            if i in "kK":
                kings[i] += 1
        else:
            return False

    if hori != 1:
        return False
    if not ((kings["K"] == 1) and (kings["k"] == 1)):
        return False
    for p in "Pp":
        if p in packed[0] or p in packed[7]:
            return False

    if fen[1] not in "wb":
        return False

    castling = ""
    if packed[7][4] == "K":
        if packed[7][7] == "R":
            castling += "K"
        if packed[7][0] == "R":
            castling += "Q"

    if packed[0][4] == "k":
        if packed[0][7] == "r":
            castling += "k"
        if packed[0][0] == "r":
            castling += "q"

    if castling == "":
        castling = "-"
    if castling != fen[2]:
        return False

    passer = fen[3]
    if passer != "-":
        nbr = ""
        vert, hori = "abcdefgh".index(passer[0]), "12345678".index(passer[1])

        if fen[1] == "w":
            if passer[1] != "6" or packed[3][vert] != "p":
                return False
            else:
                if (vert - 1) in range(0, 8):
                    nbr += packed[3][vert - 1]
                if (vert + 1) in range(0, 8):
                    nbr += packed[3][vert + 1]
            if "P" not in nbr:
                return False

        if fen[1] == "b":
            if passer[1] != "3" and packed[6][vert] != "P":
                return False
            else:
                if (vert - 1) in range(0, 8):
                    nbr += packed[4][vert - 1]
                if (vert + 1) in range(0, 8):
                    nbr += packed[4][vert + 1]
            if "p" not in nbr:
                return False

    return packed


def conv_fen(fen):
    fen = fen.split()
    hori, vert = 7, 0
    board = {
        "blank": [],
        "w": [],
        "b": [],
        "pieces": {},
        "castle": [],
        "passer": fen[3],
        "K": "",
        "k": "",
        "turn": fen[1],
    }

    for i in fen[0]:
        if i == "/":
            hori -= 1
            vert = 0
        elif i in "12345678":
            sqr = "abcdefgh"[vert] + "12345678"[hori]
            board["blank"] += fea["blank"][sqr][i]
            vert += int(i)

        elif i in "rbnqkp":
            sqr = "abcdefgh"[vert] + "12345678"[hori]
            board["b"].append(sqr)
            board["pieces"][sqr] = i
            vert += 1
        else:
            sqr = "abcdefgh"[vert] + "12345678"[hori]
            board["w"].append(sqr)
            board["pieces"][sqr] = i
            vert += 1

        if i in "Kk":
            board[i] = sqr

    if fen[2] != "-":
        for i in fen[2]:
            board["castle"].append(i)

    return board


def show_fea_moves(board):
    fea_moves = []
    oppo_side = "w" if board["turn"] == "b" else "b"
    for sqr in board[board["turn"]]:
        symbol = board["pieces"][sqr]
        _symbol = symbol.upper()
        if symbol in "Pp":
            _fea_moves = fea[symbol][sqr]
        else:
            print(board[board["turn"]])
            _fea_moves = fea[symbol.upper()][sqr]

        if symbol in "RBQrbq":
            # Rock, Biship, Queen
            for direc in _fea_moves:
                for i in direc:
                    if i in board["blank"]:
                        fea_moves.append(_symbol + sqr + i)
                    elif i in board[oppo_side]:
                        fea_moves.append(_symbol + sqr + "x" + i)
                        break
                    else:
                        break

        elif symbol in "Kk":
            # King
            for i in _fea_moves:
                if i in board["blank"]:
                    fea_moves.append(_symbol + sqr + i)
                elif i in board[oppo_side]:
                    fea_moves.append(_symbol + sqr + "x" + i)

        elif symbol in "Nn":
            # Knight
            for i in _fea_moves:
                if i in board["blank"]:
                    fea_moves.append(_symbol + sqr + i)
                elif i in board[oppo_side]:
                    fea_moves.append(_symbol + sqr + "x" + i)

        else:
            # pawns
            for i in _fea_moves[0]:
                if i in board["blank"]:
                    if i[1] in "18":
                        # pawn promotion
                        for asc in "RNBQ":
                            fea_moves.append(_symbol + sqr + i + "=" + asc)
                    else:
                        fea_moves.append(_symbol + sqr + i)
                else:
                    break

            for i in _fea_moves[1]:
                if i in board[oppo_side]:
                    if i[1] in "18":
                        # pawn promotion
                        for asc in "RNBQ":
                            fea_moves.append(_symbol + sqr + "x" + i + "=" + asc)
                    else:
                        fea_moves.append(_symbol + sqr + "x" + i)
                elif i == board["passer"]:
                    fea_moves.append(_symbol + sqr + "x" + i)

    fea_moves += can_castle(board, oppo_side)
    return fea_moves


def check(board):
    is_checked = {"w": False, "b": False}
    is_checked["w"] = is_reachable(board, board["K"], "b")
    is_checked["b"] = is_reachable(board, board["k"], "w")
    return is_checked


def is_reachable(board, target, side):
    if target in board[side]:
        return False

    for sqr in board[side]:
        symbol = board["pieces"][sqr]

        if symbol in "Pp":
            fea_moves = fea[symbol][sqr]
        else:
            fea_moves = fea[symbol.upper()][sqr]

        if symbol in "RBQrbq":
            for direc in fea_moves:
                for i in direc:
                    if i == target:
                        return True
                    elif i not in board["blank"]:
                        break

        elif symbol in "KNkn":
            for i in fea_moves:
                if i == target:
                    return True

        else:
            for i in fea_moves[1]:
                if i == target:
                    return True
    return False


def can_castle(board, oppo_side):
    own_side = "b" if oppo_side == "w" else "w"
    symbol = "KQ" if oppo_side == "b" else "kq"
    infea = ""

    for i in symbol:
        if i not in board["castle"]:
            infea += i
            continue

        for sqr in fea["castle"][i][0]:
            if is_reachable(board, sqr, oppo_side):
                infea += i
                break

        for sqr in fea["castle"][i][1]:
            if sqr not in board["blank"]:
                infea += i
                break

    result = []
    if symbol[0] not in infea:
        result.append("O-O")
    if symbol[1] not in infea:
        result.append("O-O-O")

    return result


def take_a_move(board, move):
    board = deepcopy(board)
    oppo_side = "w" if board["turn"] == "b" else "b"

    if move in ["O-O", "O-O-O"]:
        # castling kings
        if board["turn"] == "w":
            symbol = "K"
            if move == "O-O":
                sqr, target = "e1", "g1"
            else:
                sqr, target = "e1", "c1"

            for i in "KQ":
                if i in board["castle"]:
                    board["castle"].remove(i)
        else:
            symbol = "k"
            if move == "O-O":
                sqr, target = "e8", "g8"
            else:
                sqr, target = "e8", "c8"

            for i in "kq":
                if i in board["castle"]:
                    board["castle"].remove(i)
        board[symbol] = target

        board["blank"].append(sqr)
        board["blank"].remove(target)
        board[board["turn"]].append(target)
        print(move)
        board[board["turn"]].remove(sqr)
        del board["pieces"][sqr]
        board["pieces"][target] = symbol

        # castling rocks
        if board["turn"] == "w":
            symbol = "R"
            if move == "O-O":
                sqr, target = "h1", "f1"
            else:
                sqr, target = "a1", "d1"
        else:
            symbol = "r"
            if move == "O-O":
                sqr, target = "h8", "f8"
            else:
                sqr, target = "a8", "d8"

        board["blank"].append(sqr)
        board["blank"].remove(target)
        board[board["turn"]].append(target)
        board[board["turn"]].remove(sqr)
        del board["pieces"][sqr]
        board["pieces"][target] = symbol

    else:
        # normal moves and eat passers
        if "x" in move:
            symbol, sqr, target = move[0], move[1:3], move[4:6]
        else:
            symbol, sqr, target = move[0], move[1:3], move[3:5]
            board["blank"].remove(target)

        board[board["turn"]].remove(sqr)
        board[board["turn"]].append(target)

        board["blank"].append(sqr)

        del board["pieces"][sqr]

        if "=" in move:
            # pawn promotion
            board["pieces"][target] = move[-1]
        else:
            if board["turn"] == "w":
                board["pieces"][target] = symbol
            else:
                board["pieces"][target] = symbol.lower()

        if symbol in "Pp" and target == board["passer"]:
            # eat passers-by
            if board["turn"] == "w":
                passer = target[0] + "5"
            else:
                passer = target[0] + "4"
            del board["pieces"][passer]
            board[oppo_side].remove(passer)

        elif "x" in move:
            board[oppo_side].remove(target)

        if symbol == "K":
            # castling is not possible after the king has moved
            if board["turn"] == "w":
                board["K"] = target
            else:
                board["k"] = target

            if board["turn"] == "w":
                for i in "KQ":
                    if i in board["castle"]:
                        board["castle"].remove(i)
            else:
                for i in "kq":
                    if i in board["castle"]:
                        board["castle"].remove(i)

        elif symbol in "Rr":
            # castling is segmentally not possible after the rock has moved
            if symbol == "R" and sqr == "a1" and "Q" in board["castle"]:
                board["castle"].remove("Q")
            elif symbol == "R" and sqr == "h1" and "K" in board["castle"]:
                board["castle"].remove("K")
            elif symbol == "r" and sqr == "a8" and "q" in board["castle"]:
                board["castle"].remove("q")
            elif symbol == "r" and sqr == "h8" and "k" in board["castle"]:
                board["castle"].remove("k")

    board["passer"] = "-"

    if move[0] == "P" and move[2] == "2" and move[4] == "4":
        board["passer"] = move[1] + "3"

    if move[0] == "p" and move[2] == "7" and move[4] == "5":
        board["passer"] = move[1] + "6"

    board["turn"] = "b" if board["turn"] == "w" else "w"
    return board


def format_moves(board, fea_moves):
    formatted = {}
    repe = {}

    test = list(board["pieces"].values())
    index = "RNBQK" if board["turn"] == "w" else "rnbqk"
    for i in index:
        if i in test:
            test.remove(i)

    for hori in "abcdefgh":
        for vert in "12345678":
            repe[hori + vert] = []

    for move in fea_moves:
        if move in ["O-O-O", "O-O"]:
            formatted[move] = move
        elif move[0] == "P":
            if move[3] != "x":
                formatted[move] = move[3:]
            else:
                formatted[move] = move[1] + "x" + move[4:]
        elif move[0] == "K":
            formatted[move] = "K" + move[3:]

        else:
            if move[0] in test:
                if "+" in move:
                    repe[move[-3:-1]].append(move)
                else:
                    repe[move[-2:]].append(move)
            else:
                formatted[move] = move[0] + move[3:]

    for sqr in repe.keys():
        length = len(repe[sqr])

        if length == 1:
            move = repe[sqr][0]
            formatted[move] = move[0] + move[3:]

        elif length > 1:
            for i in repe[sqr]:
                flag = ""

                for j in repe[sqr]:
                    if i != j and i[0] == j[0]:
                        flag += "0"
                        if i[1] == j[1]:
                            flag += "1"

                if "0" in flag:
                    if "1" in flag:
                        formatted[i] = i
                    else:
                        formatted[i] = i[0:2] + i[3:]
                else:
                    formatted[i] = i[0] + i[3:]
    return formatted


def show_legal_moves(fen):
    board = conv_fen(fen)
    fea_moves = show_fea_moves(board)
    legal_moves = []

    for move in fea_moves:
        _board = take_a_move(board, move)
        is_checked = check(_board)
        oppo_side = "b" if board["turn"] == "w" else "w"
        if is_checked[board["turn"]]:
            continue
        elif is_checked[oppo_side]:
            legal_moves.append(move + "+")
        else:
            legal_moves.append(move)

    abbr = format_moves(board, legal_moves)
    return abbr


def gen_fen(board):
    fen = ""
    for hori in "87654321":
        empty = 0
        for vert in "abcdefgh":
            sqr = vert + hori
            if sqr in board["blank"]:
                empty += 1
            else:
                if empty:
                    fen += str(empty)
                    empty = 0
                if sqr in board["b"]:
                    fen += board["pieces"][sqr].lower()
                else:
                    fen += board["pieces"][sqr]
            if vert == "h":
                if empty:
                    fen += str(empty)
                fen += "/"
                empty = 0
    fen = fen[0:-1]
    fen += " {} {} {} {} {}".format(
        board["turn"], "".join(board["castle"]), board["passer"], 0, 1
    )

    return fen


def engine(fen):
    sleep(0.25)
    abbr = show_legal_moves(fen)
    move = choice(list(abbr.values()))
    return move

# fen =  "rn3bnr/pp1ppk1p/2b2p2/6pP/1Pp1P3/3P1QP1/P1P4P/RNB1KBNR w KQ g6 0 1"
# while True:
#     print(engine(fen))
