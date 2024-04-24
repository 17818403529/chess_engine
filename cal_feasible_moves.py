import json

ds_path = "C:/Users/17818/Music/chess_engine.py/feasible_moves.json"

fea = {"R": {}, "B": {}, "N": {}, "K": {}, "Q": {}, "p": {}, "P": {}, "blank": {}}


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
    for des in [(row + 2, col + 1), (row + 2, col - 1), (row - 2, col + 1), (row - 2, col - 1), (row + 1, col + 2), (row + 1, col - 2), (row - 1, col + 2), (row - 1, col - 2)]:
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


for row in "12345678":
    for col in "abcdefgh":
        pos = col + row
        fea["blank"][pos] = {}
        resi = []
        for i in range(col, 8):
            resi.append("abcdefgh"[i] + "12345678"[row])
        for i in range(len(resi)):
            fea["blank"][pos][str(i + 1)] = resi[: i + 1]


with open(ds_path, "w", encoding="UTF-8") as f:
    json.dump(fea, f, indent=4, ensure_ascii=False)
# with open(ds_path, "r", encoding="UTF-8") as f:
#     fea = json.load(f)
