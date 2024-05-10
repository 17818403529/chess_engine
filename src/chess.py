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


class Chess:
    def __init__(self):
        self.gen_rules_dict()

    def convert_square(self, square):
        return "abcdefgh".index(square[0]), "12345678".index(square[1])

    def gen_rules_dict(self):

        self.rules_dict = {}

        # gen Unconfined
        squares = []
        for file in "abcdefgh":
            for rank in "12345678":
                squares.append(file + rank)
        self.rules_dict["squares"] = squares

        unconfined = {}
        for i in "RNBQKPrnbqkp":
            unconfined[i] = {}

        for i in squares:
            unconfined["R"][i] = Piece.rook(i)
            unconfined["N"][i] = Piece.knight(i)
            unconfined["B"][i] = Piece.biship(i)
            unconfined["Q"][i] = Piece.queen(i)
            unconfined["K"][i] = Piece.king(i)
            unconfined["r"][i] = Piece.rook(i)
            unconfined["n"][i] = Piece.knight(i)
            unconfined["b"][i] = Piece.biship(i)
            unconfined["q"][i] = Piece.queen(i)
            unconfined["k"][i] = Piece.king(i)
            if i[1] not in "18":
                unconfined["P"][i] = Piece.w_pawn(i)
                unconfined["p"][i] = Piece.b_pawn(i)

        self.rules_dict["unconfined"] = unconfined

        # gen Blank
        blank = {}
        for i in squares:
            blank[i] = {}
            resi = [rank + i[1] for rank in "abcdefgh"["abcdefgh".index(i[0]) :]]
            for j in range(len(resi)):
                blank[i][str(j + 1)] = resi[: j + 1]
        self.rules_dict["blank"] = blank

        castle_squares = {
            "w": {
                "O-O": [["e1", "f1", "g1"], ["f1", "g1"]],
                "O-O-O": [["e1", "d1", "c1"], ["b1", "d1", "c1"]],
            },
            "b": {
                "O-O": [["e8", "f8", "g8"], ["f8", "g8"]],
                "O-O-O": [["e8", "d8", "c8"], ["b8", "d8", "c8"]],
            },
        }
        self.rules_dict["castle_squares"] = castle_squares

        # gen Castle Rights
        castle_rights = {
            "K": {
                "K": "-",
                "Q": "-",
                "k": "k",
                "q": "q",
                "KQ": "-",
                "Kk": "k",
                "Kq": "q",
                "Qk": "k",
                "Qq": "q",
                "kq": "kq",
                "Kkq": "kq",
                "Qkq": "kq",
                "KQk": "k",
                "KQq": "q",
                "KQkq": "kq",
                "-": "-",
            },
            "k": {
                "K": "K",
                "Q": "Q",
                "k": "-",
                "q": "-",
                "KQ": "KQ",
                "Kk": "K",
                "Kq": "K",
                "Qk": "Q",
                "Qq": "Q",
                "kq": "-",
                "Kkq": "K",
                "Qkq": "Q",
                "KQk": "KQ",
                "KQq": "KQ",
                "KQkq": "KQ",
                "-": "-",
            },
            "R": {
                "a1": {
                    "K": "K",
                    "Q": "-",
                    "k": "k",
                    "q": "q",
                    "KQ": "K",
                    "Kk": "Kk",
                    "Kq": "Kq",
                    "Qk": "k",
                    "Qq": "q",
                    "kq": "kq",
                    "Kkq": "Kkq",
                    "Qkq": "kq",
                    "KQk": "Kk",
                    "KQq": "Kq",
                    "KQkq": "Kkq",
                    "-": "-",
                },
                "h1": {
                    "K": "-",
                    "Q": "Q",
                    "k": "k",
                    "q": "q",
                    "KQ": "Q",
                    "Kk": "k",
                    "Kq": "q",
                    "Qk": "Qk",
                    "Qq": "Qq",
                    "kq": "kq",
                    "Kkq": "kq",
                    "Qkq": "Qkq",
                    "KQk": "Qk",
                    "KQq": "Qq",
                    "KQkq": "Qkq",
                    "-": "-",
                },
            },
            "r": {
                "a8": {
                    "K": "K",
                    "Q": "Q",
                    "k": "k",
                    "q": "-",
                    "KQ": "KQ",
                    "Kk": "Kk",
                    "Kq": "K",
                    "Qk": "Qk",
                    "Qq": "Q",
                    "kq": "k",
                    "Kkq": "Kk",
                    "Qkq": "Qk",
                    "KQk": "KQk",
                    "KQq": "KQ",
                    "KQkq": "KQk",
                    "-": "-",
                },
                "h8": {
                    "K": "K",
                    "Q": "Q",
                    "k": "-",
                    "q": "q",
                    "KQ": "KQ",
                    "Kk": "K",
                    "Kq": "Kq",
                    "Qk": "Q",
                    "Qq": "Qq",
                    "kq": "kq",
                    "Kkq": "Kq",
                    "Qkq": "Qq",
                    "KQk": "KQ",
                    "KQq": "KQq",
                    "KQkq": "KQq",
                    "-": "-",
                },
            },
        }
        self.rules_dict["castle_rights"] = castle_rights

        castle_move = {
            "w": {
                "symbol": "KR",
                "O-O": {"king": ["e1", "g1"], "rock": ["h1", "f1"]},
                "O-O-O": {"king": ["e1", "c1"], "rock": ["a1", "d1"]},
            },
            "b": {
                "symbol": "kr",
                "O-O": {"king": ["e8", "g8"], "rock": ["h8", "f8"]},
                "O-O-O": {"king": ["e8", "c8"], "rock": ["a8", "d8"]},
            },
        }
        self.rules_dict["castle_move"] = castle_move

        castle_map = {
            "K": {"w": ["O-O"], "b": []},
            "Q": {"w": ["O-O-O"], "b": []},
            "k": {"w": [], "b": ["O-O"]},
            "q": {"w": [], "b": ["O-O-O"]},
            "KQ": {"w": ["O-O-O", "O-O"], "b": []},
            "Kk": {"w": ["O-O"], "b": ["O-O"]},
            "Kq": {"w": ["O-O"], "b": ["O-O-O"]},
            "Qk": {"w": ["O-O-O"], "b": ["O-O"]},
            "Qq": {"w": ["O-O-O"], "b": ["O-O-O"]},
            "kq": {"w": [], "b": ["O-O-O", "O-O"]},
            "Kkq": {"w": ["O-O"], "b": ["O-O-O", "O-O"]},
            "Qkq": {"w": ["O-O-O"], "b": ["O-O-O", "O-O"]},
            "KQk": {"w": ["O-O-O", "O-O"], "b": ["O-O"]},
            "KQq": {"w": ["O-O-O", "O-O"], "b": ["O-O-O"]},
            "KQkq": {"w": ["O-O-O", "O-O"], "b": ["O-O-O", "O-O"]},
            "-": {"w": [], "b": []},
        }
        self.rules_dict["castle_map"] = castle_map

        passer = {
            "b": ["a3", "b3", "c3", "d3", "e3", "f3", "g3", "h3"],
            "w": ["a6", "b6", "c6", "d6", "e6", "f6", "g6", "h6"],
        }
        self.rules_dict["passer"] = passer

        passer_move = [
            "Pa2a4",
            "Pb2b4",
            "Pc2c4",
            "Pd2d4",
            "Pe2e4",
            "Pf2f4",
            "Pg2g4",
            "Ph2h4",
            "Pa7a5",
            "Pb7b5",
            "Pc7c5",
            "Pd7d5",
            "Pe7e5",
            "Pf7f5",
            "Pg7g5",
            "Ph7h5",
        ]
        self.rules_dict["passer_move"] = passer_move

        en_passant_targets = {
            "Pa2a4": "a3",
            "Pb2b4": "b3",
            "Pc2c4": "c3",
            "Pd2d4": "d3",
            "Pe2e4": "e3",
            "Pf2f4": "f3",
            "Pg2g4": "g3",
            "Ph2h4": "h3",
            "Pa7a5": "a6",
            "Pb7b5": "b6",
            "Pc7c5": "c6",
            "Pd7d5": "d6",
            "Pe7e5": "e6",
            "Pf7f5": "f6",
            "Pg7g5": "g6",
            "Ph7h5": "h6",
        }
        self.rules_dict["en_passant_targets"] = en_passant_targets

        possible_en = {
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
        self.rules_dict["possible_en"] = possible_en

        passer_square = {
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
        self.rules_dict["passer_square"] = passer_square

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
                "castle": "",
                "passer": fen[3],
                "half": int(fen[4]),
                "full": int(fen[5]),
                "K": "",
                "k": "",
            }

        # fen[0] is Piece Placement
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
                chess["blank"] += self.rules_dict["blank"][square][str(int(i))]

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

        for i in "Pp":
            # pawns can not in the "line 1" or the "line 8"
            if i in packed[0] or i in packed[7]:
                return False

        # fen[1] shows Active Color
        if fen[1] not in "wb":
            return False
        else:
            chess["turn"] = fen[1]

        # fen[2] shows Castling Rights

        castle = ["-"]
        if packed[7][4] == "K":
            if packed[7][7] == "R":
                castle.append("K")
            if packed[7][0] == "R":
                castle.append("Q")

        if packed[0][4] == "k":
            if packed[0][7] == "r":
                castle.append("k")
            if packed[0][0] == "r":
                castle.append("q")

        for i in fen[2]:
            if i not in castle:
                return False

        chess["castle"] = fen[2]

        # fen[3] shows Possible En Passant Targets
        passer = fen[3]
        if passer != "-":
            if passer not in self.rules_dict["passer"][fen[1]]:
                # passers only appears at certain squares
                return False
            else:
                # passer must have at least one opposite pawn neighbor
                flag = False
                pawn = "P" if fen[1] == "w" else "p"
                for square in self.rules_dict["possible_en"][passer]:
                    if square in chess[fen[1]]:
                        if chess["pieces"][square] == pawn:
                            flag = True
                            break
                if not flag:
                    return False

        return chess

    def is_square_attacked(self, chess, square, side):
        if square in chess[side]:
            return False

        for _square in chess[side]:
            symbol = chess["pieces"][_square]
            unconfined = self.rules_dict["unconfined"][symbol][_square]

            if symbol in "RBQrbq":
                for direc in unconfined:
                    for i in direc:
                        if i == square:
                            return True
                        elif i not in chess["blank"]:
                            break

            elif symbol in "KNkn":
                for i in unconfined:
                    if i == square:
                        return True

            else:
                for i in unconfined[1]:
                    if i == square:
                        return True
        return False

    def is_checking(self, chess):
        result = {}
        result["b"] = self.is_square_attacked(chess, chess["K"], "b")
        result["w"] = self.is_square_attacked(chess, chess["k"], "w")
        return result

    castle_squares = {
        "w": {
            "O-O": [["e1", "f1", "g1"], ["f1", "g1"]],
            "O-O-O": [["c1", "d1", "e1"], ["b1", "c1", "d1"]],
        },
        "b": {
            "O-O": [["e8", "f8", "g8"], ["f8", "g8"]],
            "O-O-O": [["c8", "d8", "e8"], ["b8", "c8", "d8"]],
        },
    }

    def gather_castlings(self, chess):
        # gather all possible castlings
        castlings = []
        oppo = "w" if chess["turn"] == "b" else "b"
        unconfined = self.rules_dict["castle_map"][chess["castle"]][chess["turn"]]
        for move in unconfined:
            flag = True
            king_path, region = self.rules_dict["castle_squares"][chess["turn"]][move]
            for square in region:
                if square not in chess["blank"]:
                    flag = False
                    break
            if flag:
                for square in king_path:
                    if self.is_square_attacked(chess, square, oppo):
                        flag = False
                        break
            if flag:
                castlings.append(move)
        return castlings

    def gather_unconfined(self, chess):
        unconfined = []
        oppo = "w" if chess["turn"] == "b" else "b"

        for square in chess[chess["turn"]]:
            symbol = chess["pieces"][square]
            targets = self.rules_dict["unconfined"][symbol][square]
            symbol = symbol.upper()

            if symbol in "RBQ":
                # Rock, Biship, Queen
                for direc in targets:
                    for i in direc:
                        if i in chess["blank"]:
                            unconfined.append(symbol + square + i)
                        elif i in chess[oppo]:
                            unconfined.append(symbol + square + "x" + i)
                            break
                        else:
                            break

            elif symbol in "KN":
                # King and Knight
                for i in targets:
                    if i in chess["blank"]:
                        unconfined.append(symbol + square + i)
                    elif i in chess[oppo]:
                        unconfined.append(symbol + square + "x" + i)

            else:
                # pawns
                for i in targets[0]:
                    if i in chess["blank"]:
                        if i[1] in "18":
                            # pawn promotion
                            for asc in "RNBQ":
                                unconfined.append("P" + square + i + "=" + asc)
                        else:
                            unconfined.append("P" + square + i)
                    else:
                        break

                for i in targets[1]:
                    if i in chess[oppo]:
                        if i[1] in "18":
                            # pawn promotion
                            for asc in "RNBQ":
                                unconfined.append("P" + square + "x" + i + "=" + asc)
                        else:
                            unconfined.append("P" + square + "x" + i)
                    elif i == chess["passer"]:
                        unconfined.append("P" + square + "x" + i)

        return unconfined

    def move_action(self, chess, symbol, square, not_taken, target):
        # symbol from square moves to target, taken or not taken
        chess[chess["turn"]].remove(square)
        chess["blank"].append(square)
        chess[chess["turn"]].append(target)

        del chess["pieces"][square]
        chess["pieces"][target] = symbol

        if symbol in "Pp" and target == chess["passer"]:
            chess["blank"].remove(target)
        else:
            if not_taken:
                chess["blank"].remove(target)
            else:
                oppo = "w" if chess["turn"] == "b" else "b"
                chess[oppo].remove(target)

    def take_a_move(self, chess, move):
        chess = deepcopy(chess)
        player = chess["turn"]
        oppo = "w" if player == "b" else "b"

        if move in ["O-O", "O-O-O"]:
            # king move
            symbol = self.rules_dict["castle_move"][player]["symbol"][0]
            chess[symbol] = target
            square, target = self.rules_dict["castle_move"][player][move]
            self.move_action(chess, symbol, square, False, target)

            # rock move
            symbol = self.rules_dict["castle_move"][player]["symbol"][1]
            square, target = self.rules_dict["castle_move"][player][move]
            self.move_action(chess, symbol, square, False, target)

            # alter castling possibility
            chess["castle"] = self.rules_dict["castle_move"][player]["poss"][
                chess["castle"]
            ]

        else:
            if "x" in move:
                symbol, square, not_taken, target = move[0], move[1:3], False, move[4:6]
            else:
                symbol, square, not_taken, target = move[0], move[1:3], True, move[3:5]

            if "=" in move:
                symbol = move[-1]

            if player == "b":
                symbol = symbol.lower()

            self.move_action(chess, symbol, square, not_taken, target)

            if symbol in "Pp" and target == chess["passer"]:
                # eat passers-by
                passer = self.rules_dict["passer_square"][chess["passer"]]
                del chess["pieces"][passer]
                chess[oppo].remove(passer)
                chess["blank"].append(passer)

            if symbol in "Kk":
                # king position should be refreashed
                chess[symbol] = target
                chess["castle"] = self.rules_dict["castle_rights"][symbol][
                    chess["castle"]
                ]

            if symbol in "Rr":
                # castling is segmentally not possible after the rock has moved
                if square in self.rules_dict["castle_rights"][symbol].keys():
                    chess["castle"] = self.rules_dict["castle_rights"][symbol][square][
                        chess["castle"]
                    ]

            chess["passer"] = "-"
            if move in self.rules_dict["passer_move"]:
                passer = self.rules_dict["en_passant_targets"][move]
                for square in self.rules_dict["possible_en"][passer]:
                    if square in chess[oppo]:
                        if chess["pieces"][square] in "Pp":
                            chess["passer"] = passer

        # alter turn
        chess["turn"] = "b" if chess["turn"] == "w" else "w"

        # alter half
        if move[0] in "Pp" or "x" in move:
            chess["half"] = "0"
        else:
            chess["half"] = str(int(chess["half"]) + 1)

        # alter full
        if player == "b":
            chess["full"] = str(int(chess["full"]) + 1)

        return chess

    def simplify_moves(self, chess, unconfined):
        simplified = {}
        repe = {}

        pieces = list(chess["pieces"].values())
        index = "RNBQK" if chess["turn"] == "w" else "rnbqk"

        for i in index:
            if i in pieces:
                pieces.remove(i)

        for file in "abcdefgh":
            for rank in "12345678":
                repe[file + rank] = []

        for move in unconfined:
            symbol = move[0] if chess["turn"] == "w" else move[0].lower()
            if move in ["O-O-O", "O-O"]:
                simplified[move] = unconfined[move]
            elif symbol in "Pp":
                if move[3] != "x":
                    simplified[move[3:]] = unconfined[move]
                else:
                    simplified[move[1] + "x" + move[4:]] = unconfined[move]
            elif symbol in "Kk":
                # there is only one king
                simplified["K" + move[3:]] = unconfined[move]

            else:
                if symbol in pieces:
                    if "+" in move:
                        repe[move[-3:-1]].append(move)
                    else:
                        repe[move[-2:]].append(move)
                else:
                    simplified[move[0] + move[3:]] = unconfined[move]

        for square in repe.keys():
            length = len(repe[square])

            if length == 1:
                move = repe[square][0]
                simplified[move[0] + move[3:]] = unconfined[move]

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
                            simplified[i] = unconfined[i]
                        else:
                            simplified[i[0:2] + i[3:]] = unconfined[i]
                    else:
                        simplified[i[0] + i[3:]] = unconfined[i]
        return simplified

    def gather_confined(self, chess):
        unconfined = self.gather_unconfined(chess)
        confined = {}

        for move in unconfined:
            _chess = self.take_a_move(chess, move)
            checking = self.is_checking(_chess)
            oppo = "b" if chess["turn"] == "w" else "w"
            if checking[oppo]:
                continue
            elif checking[chess["turn"]]:
                confined[move + "+"] = _chess
            else:
                confined[move] = _chess

        return self.simplify_moves(chess, confined)

    def gather_legal_moves(self, chess):
        confined = self.gather_confined(chess)
        legal_moves = {}
        for move in confined.keys():
            if "+" in move:
                if not self.gather_confined(confined[move]):
                    legal_moves[move[0:-1] + "#"] = confined[move]
                else:
                    legal_moves[move] = confined[move]
            else:
                legal_moves[move] = confined[move]
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

        fen += " {} {} {} {} {}".format(
            chess["turn"],
            chess["castle"],
            chess["passer"],
            chess["half"],
            chess["full"],
        )
        return fen

    def is_game_over(self, chess, move, move_history):

        if not chess:
            return {
                "event": "game_over",
                "result": "Illegal FEN.",
                "score": "",
            }

        # insufficient force
        if len(chess["blank"]) == 62:
            return {
                "event": "game_over",
                "result": "Draw, understrength.",
                "score": "1/2  -  1/2",
            }

        if len(chess["blank"]) == 61:
            for i in chess["pieces"].values():
                if i in "BbNn":
                    return {
                        "event": "game_over",
                        "result": "Draw, understrength.",
                        "score": "1/2  -  1/2",
                    }

        if "#" in move:
            if chess["turn"] == "w":
                return {
                    "event": "game_over",
                    "result": "Checkmate, black wins.",
                    "score": "0 - 1",
                }
            else:
                return {
                    "event": "game_over",
                    "result": "Checkmate, white wins.",
                    "score": "1 - 0",
                }

        if chess["half"] == 100:
            return {
                "event": "game_over",
                "result": "Draw, 50 moves.",
                "score": "1/2  -  1/2",
            }

        # rep3 draw
        placement = list(move_history.values())
        placement.reverse()
        repeated = 0
        for i in placement:
            if i == placement[0]:
                repeated += 1
                if repeated == 4:
                    return {
                        "event": "game_over",
                        "result": "Draw, rep3.",
                        "score": "1/2  -  1/2",
                    }

        player = chess["turn"]
        oppo = "b" if player == "w" else "w"
        checking = self.is_checking(chess)

        if checking[player]:
            return {
                "event": "game_over",
                "result": "Illegal FEN.",
                "score": "",
            }

        if not checking[oppo] and self.gather_legal_moves(chess) == {}:
            return {
                "event": "game_over",
                "result": "Stalemate.",
                "score": "1/2  -  1/2",
            }

        return False


from time import sleep
from random import random, randint


def engine(chess):
    sleep(randint(1, 2) + random())
    ch = Chess()
    legal_moves = ch.gather_legal_moves(chess)
    castling = []
    capture = []
    check = []
    king = []
    others = []
    move = ""
    for i in list(legal_moves.keys()):
        if "#" in i:
            return i, legal_moves[i]
        elif i in ["O-O-O", "O-O"]:
            castling.append(i)
        elif "x" in i:
            capture.append(i)
        elif "+" in i:
            check.append(i)
        elif "K" in i:
            king.append(i)
        else:
            others.append(i)

    if castling:
        move = choice(castling)
        return move, legal_moves[move]
    elif capture:
        if random() > 0.3:
            move = choice(capture)
            return move, legal_moves[move]
    elif check:
        if random() > 0.2:
            move = choice(check)
            return move, legal_moves[move]
    elif others:
        if random() > 0.5:
            move = choice(others)
            return move, legal_moves[move]
    elif king:
        if random() > 0.9:
            move = choice(king)
            return move, legal_moves[move]

    move = choice(list(legal_moves.keys()))
    return move, legal_moves[i]


if __name__ == "__main__":
    from vfunc import *

    fen = "7k/8/8/3PpP2/8/8/8/2K5 w - e6 0 1"
    ch = Chess()
    chess = ch.convert(fen)
    vfunc("speed", ch.convert, fen)
