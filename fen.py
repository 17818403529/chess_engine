from time import time
import json

ds_path = "C:/Users/17818/Music/chess_engine.py/feasible_moves.json"
with open(ds_path, "r", encoding="UTF-8") as f:
    fea = json.load(f)


def is_fen_legal(fen):
    fen = fen.split()
    if len(fen) != 6:
        return False

    packed = [list("eeeeeeee"), list("eeeeeeee"), list("eeeeeeee"), list("eeeeeeee"), list("eeeeeeee"), list("eeeeeeee"), list("eeeeeeee"), list("eeeeeeee")]
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
    board = {"blank": [], "w": [], "b": [], "pieces": {}, "passer": fen[3], "K": "", "k": ""}

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

    return board


def show_legal_moves(board, turn):
    legal_moves = []
    oppo_side = "w" if turn == "b" else "b"
    for sqr in board[turn]:
        symbol = board["pieces"][sqr]
        _symbol = symbol.upper()
        if symbol in "Pp":
            fea_moves = fea[symbol][sqr]
        else:
            fea_moves = fea[symbol.upper()][sqr]

        if symbol in "RBQrbq":
            for direc in fea_moves:
                for i in direc:
                    if i in board["blank"]:
                        legal_moves.append(_symbol + sqr + i)
                    elif i in board[oppo_side]:
                        legal_moves.append(_symbol + sqr + "x" + i)
                        break
                    else:
                        break

        elif symbol in "Kk":
            for i in fea_moves:
                if i in board["blank"]:
                    legal_moves.append(_symbol + sqr + i)
                elif i in board[oppo_side]:
                    legal_moves.append(_symbol + sqr + "x" + i)

        elif symbol in "Nn":
            for i in fea_moves:
                if i in board["blank"]:
                    legal_moves.append(_symbol + sqr + i)
                elif i in board[oppo_side]:
                    legal_moves.append(_symbol + sqr + "x" + i)

        else:
            for i in fea_moves[0]:
                if i in board["blank"]:
                    if i[1] in "18":
                        for asc in "RNBQ":
                            legal_moves.append(i + "=" + asc)
                    else:
                        legal_moves.append(i)
                else:
                    break

            for i in fea_moves[1]:
                if i in board[oppo_side]:
                    if i[1] in "18":
                        for asc in "RNBQ":
                            legal_moves.append(sqr[0] + "x" + i + "=" + asc)
                    else:
                        legal_moves.append(sqr[0] + "x" + i)
                elif i == board["passer"]:
                    legal_moves.append(sqr[0] + "x" + i)

    return legal_moves


def check(board):
    is_checked = {"w": False, "b": False}
    for sqr in board["pieces"].keys():
        symbol = board["pieces"][sqr]
        if symbol in "RNBQKP":
            if is_checked["b"]:
                continue
            else:
                target, own_side, oppo_side = board["k"], "w", "b"
        else:
            if is_checked["w"]:
                continue
            else:
                target, own_side, oppo_side = board["K"], "b", "w"

        if symbol in "Pp":
            fea_moves = fea[symbol][sqr]
        else:
            fea_moves = fea[symbol.upper()][sqr]

        if symbol in "RBQrbq":
            for direc in fea_moves:
                for i in direc:
                    if i in board[oppo_side]:
                        if i == target:
                            is_checked[oppo_side] = True
                        break
                    elif i in board[own_side]:
                        break

        elif symbol in "KNkn":
            for i in fea_moves:
                if i == target:
                    is_checked[oppo_side] = True
                    break

        else:
            for i in fea_moves[1]:
                if i == target:
                    is_checked[oppo_side] = True
                    break

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


def can_castle(board, own_side):
    result = []
    if own_side == "w":
        castle = "KQ"
        shorit, _long = ["e1", "f1", "g1"], ["e1", "d1", "c1"]
    else:
        shorit, _long = ["e1", "f1", "g1"], ["e1", "d1", "c1"]
        castle = "kq"

    flag = 1
    if castle[0] in board["castle"]:
        for i in shorit:
            if is_sqr_attacked(board, i, own_side):
                flag = 0
        if flag:
            result.append("O-O")

    flag = 1
    if castle[1] in board["castle"]:
        for i in shorit:
            if is_sqr_attacked(board, i, own_side):
                flag = 0
        if flag:
            result.append("O-O-O")
    return result


fen = "8/k7/8/1r1q4/8/K2Q4/8/8 w - - 0 1"
board = conv_fen(fen)
# while True:
#     target = input("type the target:")
#     print(is_reachable(board, target, "b"))
# print(check(board))
# steps = len(show_legal_moves(board, "b"))
# print(steps)
# print(show_legal_moves(board, "w"))

# steps = 1
# test = 10000
# t0 = time()
# for i in range(test):
#     is_reachable(board, "b4", "b")
# past = time() - t0
# print("{}/s".format(int(steps * test / past)))
