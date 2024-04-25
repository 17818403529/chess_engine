from fen import *


def test_is_fen_legal():
    fen = input("paste the FEN:")
    if not is_fen_legal(fen):
        print(False)
    else:
        print(True)


def test_can_castle():
    fen = input("paste the FEN:")
    if is_fen_legal(fen):
        board = conv_fen(fen)
        print("white: {}, black: {}".format(can_castle(board, "b"), can_castle(board, "w")))
    else:
        print("illegal FEN")


while True:
    test_can_castle()
