from time import time
import json

ds_path = "C:/Users/17818/Music/chess_engine.py/feasible_moves.json"
with open(ds_path, "r", encoding="UTF-8") as f:
    fea = json.load(f)


def if_fen_legal(fen):
    fen = fen.split()
    if len(fen) != 6:
        return False

    packed_fen = [list("eeeeeeee"), list("eeeeeeee"), list("eeeeeeee"), list("eeeeeeee"), list("eeeeeeee"), list("eeeeeeee"), list("eeeeeeee"), list("eeeeeeee")]
    line = ""
    kings = {"k": 0, "K": 0}
    row, col = 8, 0

    for i in fen[0]:
        if i == "/":
            row -= 1
            if row < 1 or col != 8:
                return False
            col = 0
            line = ""
        elif i in "12345678":
            col = col + int(i)
        elif i in "rbnqkpRBNQKP":
            col += 1
            packed_fen[8 - row][col - 1] = i
            if i in "kK":
                kings[i] += 1
        else:
            return False
    if row != 1:
        return False
    if not ((kings["K"] == 1) and (kings["k"] == 1)):
        return False

    if fen[1] not in "wb":
        return False

    castling = ""
    if packed_fen[7][4] == "K":
        if packed_fen[7][7] == "R":
            castling += "K"
        if packed_fen[7][0] == "R":
            castling += "Q"

    if packed_fen[0][4] == "k":
        if packed_fen[0][7] == "r":
            castling += "k"
        if packed_fen[0][0] == "r":
            castling += "q"

    if castling == "":
        castling = "-"
    if castling != fen[2]:
        return False

    passer = fen[3]
    if passer != "-":
        nbr = ""
        col, row = "abcdefgh".index(passer[0]), "12345678".index(passer[1])

        if fen[1] == "w":
            if passer[1] != "6" or packed_fen[3][col] != "p":
                return False
            else:
                if (col - 1) in range(0, 8):
                    nbr += packed_fen[3][col - 1]
                if (col + 1) in range(0, 8):
                    nbr += packed_fen[3][col + 1]
            if "P" not in nbr:
                return False

        if fen[1] == "b":
            if passer[1] != "3" and packed_fen[6][col] != "P":
                return False
            else:
                if (col - 1) in range(0, 8):
                    nbr += packed_fen[4][col - 1]
                if (col + 1) in range(0, 8):
                    nbr += packed_fen[4][col + 1]
            if "p" not in nbr:
                return False

    return packed_fen


def conv_fen(fen):
    fen = fen.split()
    row, col = 7, 0
    board = {"blank": [], "w": [], "b": [], "pieces": {}}

    for i in fen[0]:
        if i == "/":
            row -= 1
            col = 0
        elif i in "12345678":
            pos = "abcdefgh"[col] + "12345678"[row]
            board["blank"] += fea["blank"][pos][i]
            col += int(i)

        elif i in "rbnqkp":
            pos = "abcdefgh"[col] + "12345678"[row]
            board["w"].append(pos)
            board["pieces"][pos] = i
        elif i in "RBNQKP":
            pos = "abcdefgh"[col] + "12345678"[row]
            board["b"].append(pos)
            board["pieces"][pos] = i
        else:
            pos = "abcdefgh"[col] + "12345678"[row]
            board["blank"].append(pos)
    return board


def show_legal_moves(board, turn):
    legal_moves = []
    op = "w" if turn == "b" else "b"
    for pos in board[turn]:
        symbol = board["pieces"][pos]
        _symbol = symbol.upper()
        if symbol in "Pp":
            fea_moves = fea[symbol][pos]
        else:
            fea_moves = fea[symbol.upper()][pos]

        if symbol in "RBKQrbkq":
            for direc in fea_moves:
                for i in direc:
                    if i in board["blank"]:
                        legal_moves.append(_symbol + pos + i)
                    elif i in board[op]:
                        legal_moves.append(_symbol + pos + "x" + i)
                        break
                    else:
                        break
        elif symbol in "Nn":
            for i in fea_moves:
                if i in board["blank"]:
                    legal_moves.append(_symbol + pos + i)
                elif i in board[op]:
                    legal_moves.append(_symbol + pos + "x" + i)
                    break
                else:
                    break
        else:
            for i in fea_moves[0]:
                if i in board["blank"]:
                    legal_moves.append(_symbol + pos + i)
                else:
                    break

            for i in fea_moves[1]:
                if i in board[op]:
                    legal_moves.append(_symbol + pos + "x" + i)
    return legal_moves


fen = "rnb1k1r1/pp1pp2p/5ppn/2p4b/2q1PP2/NP1B1Q2/P1PP2PP/1RB1K1NR w Kq - 0 1"
board = conv_fen(fen)
# print(board)
print(len(show_legal_moves(board, "w")))

test = 10000
a = 0
t0 = time()
for i in range(test):
    # conv_fen(fen)
    # a = a + 1
    show_legal_moves(board, "w")
past = time() - t0
print("{}/s".format(int(test / past)))
