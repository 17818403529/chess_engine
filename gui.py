import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5 import *
import os
from time import sleep
from random import choice
from models import *
import json

pieces_path = "C:\\Users\\17818\\Music\\chess_engine\\pieces\\"


class EngineThread(QThread):

    def __init__(self, signal):
        super().__init__()
        self.signal = signal

    def run(self):
        fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
        board = conv_fen(fen)

        while True:
            nodes = gen_nodes(board)
            legal_moves = list(nodes.keys())
            if legal_moves == []:
                print("#")
                break
            else:
                move = choice(legal_moves)
            board = nodes[move]
            print(board["turn"], move)
            sleep(0.3)
            self.signal.emit(json.dumps(board))


class MyWin(QWidget):

    signal = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.title = "VChess"
        self.top = 480
        self.left = 200
        self.width = 720
        self.height = 600
        self.InitWindow()

    def move(self, signal):

        board = json.loads(signal)

        for sqr in board["blank"]:
            hori, vert = "abcdefgh".index(sqr[0]), "87654321".index(sqr[1])
            label = QLabel("")
            label.setAlignment(Qt.AlignCenter)
            self.table.setCellWidget(vert, hori, label)

        for sqr in board["pieces"].keys():
            hori, vert = "abcdefgh".index(sqr[0]), "87654321".index(sqr[1])
            symbol = board["pieces"][sqr]
            side = "w" if symbol in "RNBQKP" else "b"
            symbol = symbol.lower() if side == "b" else symbol
            img_path = pieces_path + "{}\\{}.png".format(side, symbol)
            label = QLabel("")
            label.setAlignment(Qt.AlignCenter)
            label.setPixmap(QPixmap(img_path).scaled(40, 40))
            self.table.setCellWidget(vert, hori, label)

    def InitWindow(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.top, self.left, self.width, self.height)
        self.creatingTables()
        self.vBoxLayout = QVBoxLayout()
        self.vBoxLayout.addWidget(self.table)
        self.setLayout(self.vBoxLayout)

        self.show()

        self.engine_thread = EngineThread(self.signal)
        self.engine_thread.start()
        self.signal.connect(self.move)

    def creatingTables(self):

        self.table = QTableWidget(8, 8, self)
        self.table.setShowGrid(True)
        for i in range(8):
            self.table.setRowHeight(i, 64)
            self.table.setColumnWidth(i, 64)

        for i in range(8):
            cell_text = QTableWidgetItem("ABCDEFGH"[i])
            self.table.setHorizontalHeaderItem(i, cell_text)
            cell_text = QTableWidgetItem("87654321"[i])
            self.table.setVerticalHeaderItem(i, cell_text)

        for vert in range(8):
            for hori in range(8):
                if vert % 2 == 0:
                    if hori % 2 == 1:
                        cell_bc = QColor(242, 242, 242)
                    else:
                        cell_bc = QColor(206, 206, 206)
                else:
                    if hori % 2 == 1:
                        cell_bc = QColor(206, 206, 206)
                    else:
                        cell_bc = QColor(242, 242, 242)
                self.table.setItem(hori, vert, QTableWidgetItem())
                self.table.item(hori, vert).setBackground(cell_bc)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MyWin()
    sys.exit(app.exec())
