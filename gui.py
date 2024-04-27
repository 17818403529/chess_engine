import sys
import os
import json
from vfunc import *
import time

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5 import *

from chess_engine.lib import *

pieces_path = os.getcwd() + "\\pieces\\"
fen = """
rn3bnr/pp1ppk1p/2b2p2/6pP/1Pp1P3/3P1QP1/P1P4P/RNB1KBNR w KQ g6 0 1
"""


class Chess(QThread):
    def __init__(self, signal):
        super().__init__()
        self.move_list = []
        self.signal = signal
        self.init_fen = fen

    def run(self):
        fen = self.init_fen
        while True:
            board = convert(fen)
            legal_moves = show_legal_moves(fen)
            move = engine(fen)
            if move in legal_moves.values():
                for key in legal_moves.keys():
                    if legal_moves[key] == move:
                        _move = key
                        break
            else:
                return False

            board = take_a_move(board, _move)
            fen = gen_fen(board)
            self.signal.emit(json.dumps(board))


class VBoard(QWidget):

    signal = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.title = "VBoard"
        self.board_style = {
            "light": QColor(206, 206, 206),
            "bold": QColor(242, 242, 242),
        }
        self.square_size = 81
        self.piece_size = 58
        self.piece_style = "sketching"
        self.piece_image_dir = os.getcwd() + "\\pieces\\{}\\".format(self.piece_style)

        self.load_piece_imgs()
        self.signal.connect(self.refresh_board)
        self.init_window()

    def load_piece_imgs(self):
        self.piece_imgs = {}
        for symbol in "rnbqkp":
            img_path = self.piece_image_dir + "b{}.png".format(symbol)
            self.piece_imgs[symbol] = QPixmap(img_path)

        for symbol in "RNBQKP":
            img_path = self.piece_image_dir + "w{}.png".format(symbol)
            self.piece_imgs[symbol] = QPixmap(img_path)

    def init_window(self):
        self.setWindowTitle(self.title)
        self.setGeometry(480, 200, 800, 720)

        self.draw_board()
        self.show()
        self.chess_thread = Chess(self.signal)
        self.chess_thread.start()

    def draw_board(self):

        # set the size and placement, whether to show grid
        self.board = QTableWidget(8, 8, self)
        self.board.setGeometry(5, 5, 680, 690)
        self.board.setFrameShape(QFrame.Box)
        self.board.setShowGrid(True)

        # set the header(the coordinate) font to bold
        font = self.board.horizontalHeader().font()
        font.setBold(True)
        self.board.horizontalHeader().setFont(font)
        font = self.board.verticalHeader().font()
        font.setBold(True)
        self.board.verticalHeader().setFont(font)

        for i in range(8):
            # set the square size
            self.board.setRowHeight(i, self.square_size)
            self.board.setColumnWidth(i, self.square_size)

            # draw the header
            cell_text = QTableWidgetItem("abcdefgh"[i])
            self.board.setHorizontalHeaderItem(i, cell_text)
            cell_text = QTableWidgetItem("87654321"[i])
            self.board.setVerticalHeaderItem(i, cell_text)

        # fill different colors for different squares
        for vert in range(8):
            for hori in range(8):
                self.board.setItem(hori, vert, QTableWidgetItem())
                if (vert + hori) % 2 == 1:
                    color = self.board_style["light"]
                else:
                    color = self.board_style["bold"]
                self.board.item(hori, vert).setBackground(color)

    def refresh_board(self, signal):
        # refresh board after one certain move
        board = json.loads(signal)

        for hori in range(8):
            for vert in range(8):
                sqr = "abcdefgh"[hori] + "87654321"[vert]
                label = QLabel("")

                if sqr not in board["blank"]:
                    # put piece at a square if it is not blank
                    symbol = board["pieces"][sqr]
                    side = "w" if symbol in "RNBQKP" else "b"
                    symbol = symbol.lower() if side == "b" else symbol
                    # load the chess image file

                    img_path = self.piece_image_dir + "{}.png".format(side + symbol)
                    label.setPixmap(self.piece_imgs[symbol].scaled(self.piece_size, self.piece_size))

                label.setAlignment(Qt.AlignCenter)
                self.board.setCellWidget(vert, hori, label)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = VBoard()
    sys.exit(app.exec())
