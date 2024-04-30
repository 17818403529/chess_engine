import sys
import os
import json
from random import choice
from time import sleep

import pygame
from models import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5 import *

config_path = os.path.dirname(os.path.abspath(__file__)) + "\\config.json"
with open(config_path, "r", encoding="utf-8") as f:
    config = json.load(f)
pygame.mixer.init()


class Piece(QLabel):
    def model(self, image, size):
        self.setPixmap(image.scaled(size, size))

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            drag = QDrag(self)
            mimeData = QMimeData()

            pixmap = QPixmap(self.size())
            self.render(pixmap)
            drag.setPixmap(pixmap)

            drag.setMimeData(mimeData)
            drag.exec_(Qt.MoveAction)


class Game(QThread):
    def __init__(self, signal, fen):
        super().__init__()
        self.pgn = {}
        self.signal = signal
        self.chess_dict = Chess.gen_chess_dict()
        self.fen = fen

    def judge(self, move, board):

        # move = engine(board, self.chess_dict)
        # if move in legal_moves.keys():
        #     board = Chess.take_a_move(board, legal_moves[move], self.chess_dict)
        #     self.current_fen = Chess.gen_fen(board).split()[0]
        #     self.pgn[move] = self.current_fen
        # else:
        #     return False

        if "#" in move:
            # checkmate
            return True

        legal_moves = Chess.gather_legal_moves(board, self.chess_dict)
        if legal_moves == {}:
            # stalemate
            return True

        # 50 moves draw
        if board["half"] == "100":
            return True

        # 3 rep draw
        pgn = list(self.pgn.values())
        pgn.reverse()
        repe = 0
        for i in pgn:
            if i == self.current_fen:
                repe += 1
        if repe == 4:
            return True

        # insufficient particle force
        if len(board["blank"]) == 62:
            return True

        if len(board["blank"]) == 61:
            for i in board["pieces"].values():
                if i in "BbNn":
                    return True
        return False

    def run(self):
        board = Chess.convert(self.fen, self.chess_dict)
        while True:
            move = engine(board, self.chess_dict)
            result = self.judge(move, board)
            self.signal.emit(json.dumps(result))
            if result["status"]:
                break
            board = result["board"]


class Hera(QMainWindow):

    # signals
    game_signal = pyqtSignal(str)
    white_signal = pyqtSignal(str)
    black_signal = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        # basic appearance setup
        self.centralWidget = QWidget()
        self.layout = QGridLayout()
        self.chessboard = QTableWidget(8, 8, self)
        self.manual_area = QTableWidget(1, 3, self)
        self.load_piece_image()
        self.move_sound = pygame.mixer.Sound(self.sound_dir + "move.wav")

        # load config
        self.piece_image_dir = config["piece_image_dir"]
        self.sound_dir = config["sound_dir"]
        self.chessboard_style = config["chessboard_style"]
        self.square_size = config["square_size"]
        self.piece_styles = config["piece_styles"]
        self.current_piece_style = config["current_piece_style"]

        # system variables
        self.piece_image = {}
        self.piece_size = None
        self.is_silent = True
        self.game_thread = None
        self.game_signal.connect(self.update_game_status)

        # append components
        self.compose()
        self.append_menu()
        self.append_chessboard()
        self.append_manual_area()

    def load_piece_image(self):
        # load the picture of each piece from disk
        suffix = self.piece_styles[self.current_piece_style][0]
        self.piece_size = self.piece_styles[self.current_piece_style][1]

        for symbol in "rnbqkp":
            img_path = self.piece_image_dir + "{}\\b{}.{}".format(
                self.current_piece_style, symbol, suffix
            )
            self.piece_image[symbol] = QPixmap(img_path)

        for symbol in "RNBQKP":
            img_path = self.piece_image_dir + "{}\\w{}.{}".format(
                self.current_piece_style, symbol, suffix
            )
            self.piece_image[symbol] = QPixmap(img_path)

    def compose(self):
        self.setAcceptDrops(True)
        self.setWindowTitle("VBord")
        self.setCentralWidget(self.centralWidget)
        self.setGeometry(480, 200, 1000, 720)
        self.layout.setSpacing(10)
        self.layout.addWidget(self.chessboard, 0, 0, 1, 1)
        self.layout.addWidget(self.manual_area, 0, 1, 1, 1)
        self.centralWidget.setLayout(self.layout)

    def append_menu(self):
        menuBar = self.menuBar()

        # append "File" menu
        fileMenu = menuBar.addMenu("Files")

        openAct = QAction(QIcon(""), "Open...", self)
        openAct.setShortcut("Ctrl+F")
        openAct = QAction(QIcon(""), "Open...", self)
        fileMenu.addAction(openAct)

        # the "Game Menu"
        gameMenu = menuBar.addMenu("Game")

        newGameAct = QAction(QIcon(""), "new game", self)
        gameMenu.addAction(newGameAct)
        newGameAct.triggered.connect(self.new_game)

        # append "Config" menu
        configMenu = menuBar.addMenu("Configs")

        # "piece style" submenu
        pieceStyleMenu = configMenu.addMenu("Pieces Style")

        for style in self.piece_styles.keys():
            styleAct = QAction(QIcon(""), style, self)
            styleAct.triggered.connect(
                lambda: self.alter_current_piece_style(self.sender().text())
            )
            pieceStyleMenu.addAction(styleAct)

        # "sound" submenu
        soundMenu = configMenu.addMenu("Sound")

        adjustVolumeAct = QAction(QIcon(""), "Adjust Volume", self)
        soundMenu.addAction(adjustVolumeAct)

        keepSilentAct = QAction(QIcon(""), "Keep Silent", self)
        keepSilentAct.triggered.connect(self.keep_silent)
        soundMenu.addAction(keepSilentAct)

        # the "Help Menu"
        helpMenu = menuBar.addMenu("Help")

        helpAct = QAction(QIcon(""), "Help", self)
        helpAct.setShortcut("Ctrl+H")
        helpMenu.addAction(helpAct)

        aboutAct = QAction(QIcon(""), "About", self)
        helpMenu.addAction(aboutAct)

    def alter_current_piece_style(self, style):
        self.current_piece_style = style
        self.load_piece_image()

    def new_game(self):
        if self.game_thread:
            self.game_thread.terminate()
            self.game_thread.wait()

        self.game_thread = Game(
            self.game_signal, "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
        )
        self.game_thread.start()

    def keep_silent(self):
        if self.is_silent:
            self.is_silent = False
        else:
            self.is_silent = True

    def append_chessboard(self):

        # set the base appearance and scaling behavior
        self.chessboard.setMinimumSize(660, 660)

        for i in range(8):
            # setup square size
            self.chessboard.setRowHeight(i, self.square_size)
            self.chessboard.setColumnWidth(i, self.square_size)

        self.chessboard.horizontalHeader().setVisible(False)
        self.chessboard.verticalHeader().setVisible(False)
        self.chessboard.setFrameShape(QFrame.NoFrame)
        self.chessboard.setShowGrid(False)
        self.chessboard.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # set square color
        light, bold = (
            self.chessboard_style["light"],
            self.chessboard_style["bold"],
        )

        style = {
            "light": QColor(light[0], light[1], light[2]),
            "bold": QColor(bold[0], bold[1], bold[2]),
        }

        for hori in range(8):
            for vert in range(8):
                # create item and set font
                self.chessboard.setItem(hori, vert, QTableWidgetItem())
                self.chessboard.item(hori, vert).setFont(
                    QFont("consolas", 10, QFont.Bold)
                )

                # fill different colors for different squares
                if (vert + hori) % 2 == 1:
                    b_color = style["light"]
                    f_color = style["bold"]
                else:
                    b_color = style["bold"]
                    f_color = style["light"]
                self.chessboard.item(hori, vert).setBackground(b_color)
                self.chessboard.item(hori, vert).setForeground(f_color)

                # fill in the row and column numbers
                if hori == 7:
                    self.chessboard.item(hori, vert).setTextAlignment(
                        Qt.AlignRight | Qt.AlignBottom
                    )
                    self.chessboard.item(hori, vert).setText("abcdefgh"[vert])
                if vert == 0:
                    self.chessboard.item(hori, vert).setTextAlignment(
                        Qt.AlignLeft | Qt.AlignTop
                    )
                    self.chessboard.item(hori, vert).setText("87654321"[hori])

        # special square "a1"
        self.chessboard.setItem(7, 0, QTableWidgetItem())
        self.chessboard.item(7, 0).setTextAlignment(Qt.AlignRight | Qt.AlignBottom)
        self.chessboard.item(7, 0).setText("a")

    def append_manual_area(self):

        # setup the base appearance and scaling behavior
        self.manual_area.setMaximumSize(240, 660)
        self.manual_area.setFrameShape(QFrame.NoFrame)
        self.manual_area.setShowGrid(False)
        self.manual_area.horizontalHeader().setVisible(False)
        self.manual_area.verticalHeader().setVisible(False)
        self.manual_area.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # setup the column width
        self.manual_area.setColumnWidth(0, 45)
        self.manual_area.setColumnWidth(1, 60)
        self.manual_area.setColumnWidth(1, 60)

    def update_game_status(self, game_signal):
        # refresh chessboard after one certain move in games
        data = json.loads(game_signal)
        board, move = data["board"], data["move"]
        turn, full = board["turn"], int(board["full"])
        current_row = self.manual_area.rowCount()

        if turn == "b":
            self.manual_area.insertRow(current_row)
            current_row = self.manual_area.rowCount()
            for j in range(3):
                self.manual_area.setItem(current_row - 1, j, QTableWidgetItem())

            self.manual_area.item(current_row - 1, 0).setText(str(full))
            self.manual_area.item(current_row - 1, 1).setText(move)
        else:
            self.manual_area.item(current_row - 1, 2).setText(move)

        for hori in range(8):
            for vert in range(8):
                piece = Piece("")
                square = "abcdefgh"[hori] + "87654321"[vert]

                if square not in board["blank"]:
                    # put piece at a square if it is not blank
                    symbol = board["pieces"][square]
                    try:
                        piece.model(self.pieces[symbol], self.piece_size)
                    except:
                        print(symbol, board["pieces"])

                piece.setAlignment(Qt.AlignCenter)
                self.chessboard.setCellWidget(vert, hori, piece)

        if not self.is_silent:
            self.move_sound.play()

    def dragEnterEvent(self, event):
        event.accept()

    def dropEvent(self, event):
        pos = event.pos()
        square = self.chessboard.itemAt(pos)
        hori, vert = square.row(), square.column()
        print(hori, vert)
        piece = event.source()
        self.chessboard.setCellWidget(hori, vert, piece)
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    hera = Hera()
    hera.show()
    sys.exit(app.exec())
