import sys
import os
import json
from random import choice
from time import sleep

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5 import *
import pygame

from models import *


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

    def is_game_ended(self, board):

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
            legal_moves = Chess.gather_legal_moves(board, self.chess_dict)
            if len(list(legal_moves.keys())) == 0:
                print("mate")
            move = engine(board, self.chess_dict)
            if move in legal_moves.keys():
                board = Chess.take_a_move(board, legal_moves[move], self.chess_dict)
                self.current_fen = Chess.gen_fen(board).split()[0]
                self.pgn[move] = self.current_fen
            else:
                return False
            self.signal.emit(json.dumps({"board": board, "move": move}))
            if self.is_game_ended(board):
                break
            sleep(1)


class VBord(QMainWindow):

    signal = pyqtSignal(str)

    def __init__(self):
        super().__init__()

        # basic setup
        self.setAcceptDrops(True)
        self.setWindowTitle("VBord")
        self.centralWidget = QWidget()
        self.setCentralWidget(self.centralWidget)
        # self.setGeometry(480, 200, 1000, 720)
        self.layout = QGridLayout()
        self.layout.setSpacing(10)

        # system
        self.is_silent = True
        self.game_thread = None

        # load resource files
        self.load_config()
        self.load_pieces()
        self.load_sound()

        # render all assembly units
        self.render_menu()
        self.render_chessboard()
        self.render_manual_zone()
        self.compose()

        # connect signals
        self.signal.connect(self.game)

    def compose(self):
        self.layout.addWidget(self.chessboard, 0, 0, 1, 1)
        self.layout.addWidget(self.manual_zone, 0, 1, 1, 1)
        self.centralWidget.setLayout(self.layout)

    def render_manual_zone(self):
        self.manual_zone = QTableWidget(1, 3, self)
        self.manual_zone.setMaximumSize(240, 660)
        self.manual_zone.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.manual_zone.setFrameShape(QFrame.NoFrame)
        self.manual_zone.setShowGrid(False)

        # hide the header
        self.manual_zone.horizontalHeader().setVisible(False)
        self.manual_zone.verticalHeader().setVisible(False)

        self.manual_zone.setColumnWidth(0, 45)
        self.manual_zone.setColumnWidth(1, 60)
        self.manual_zone.setColumnWidth(1, 60)

    def load_config(self):
        config_path = os.path.dirname(os.path.abspath(__file__)) + "\\config.json"
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)

        # chessboard square color
        light, bold = (
            config["chessboard_style"]["light"],
            config["chessboard_style"]["bold"],
        )
        self.chessboard_style = {
            "light": QColor(light[0], light[1], light[2]),
            "bold": QColor(bold[0], bold[1], bold[2]),
        }

        # square size
        self.square_size = config["square_size"]

        # piece style
        self.current_piece_style = config["current_piece_style"]

        # resource file directory
        self.pieces_dir = config["pieces_dir"]
        self.sound_dir = config["sound_dir"]

        # pieces styles
        self.piece_styles = config["piece_styles"]

    def load_pieces(self):
        # load the picture of each piece from disk
        self.pieces = {}
        suffix = self.piece_styles[self.current_piece_style][0]
        self.piece_size = self.piece_styles[self.current_piece_style][1]

        for symbol in "rnbqkp":
            img_path = self.pieces_dir + "{}\\b{}.{}".format(
                self.current_piece_style, symbol, suffix
            )
            self.pieces[symbol] = QPixmap(img_path)

        for symbol in "RNBQKP":
            img_path = self.pieces_dir + "{}\\w{}.{}".format(
                self.current_piece_style, symbol, suffix
            )
            self.pieces[symbol] = QPixmap(img_path)

    def load_sound(self):
        pygame.mixer.init()
        self.move_sound = pygame.mixer.Sound(self.sound_dir + "move.wav")

    def new_game(self):
        if self.game_thread:
            self.game_thread.terminate()
            self.game_thread.wait()

        self.game_thread = Game(
            self.signal, "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
        )
        self.game_thread.start()

    def render_menu(self):
        menuBar = self.menuBar()

        fileMenu = menuBar.addMenu("Files")
        gameMenu = menuBar.addMenu("Game")
        configMenu = menuBar.addMenu("Configs")

        # the "Game Menu"
        newGameAct = QAction(QIcon(""), "new game", self)
        gameMenu.addAction(newGameAct)
        newGameAct.triggered.connect(self.new_game)

        # the "Pieces Style Menu"
        pieceStyleMenu = configMenu.addMenu("Pieces Style")
        for style in self.piece_styles.keys():
            styleAct = QAction(QIcon(""), style, self)
            pieceStyleMenu.addAction(styleAct)
            styleAct.triggered.connect(
                lambda: self.alter_current_piece_style(self.sender().text())
            )

        # the "Sound Menu"
        soundMenu = configMenu.addMenu("Sound")
        adjustVolumeAct = QAction(QIcon(""), "Adjust Volume", self)
        soundMenu.addAction(adjustVolumeAct)

        keepSilentAct = QAction(QIcon(""), "Keep Silent", self)
        soundMenu.addAction(keepSilentAct)
        keepSilentAct.triggered.connect(self.keep_silent)

        # the "File Menu"
        openAct = QAction(QIcon(""), "Open...", self)
        openAct.setShortcut("Ctrl+F")
        openAct = QAction(QIcon(""), "Open...", self)
        fileMenu.addAction(openAct)
        
        # the "Help Menu"
        helpMenu = menuBar.addMenu("Help")
        helpAct = QAction(QIcon(""), "Help", self)
        helpAct.setShortcut("Ctrl+H")
        aboutAct = QAction(QIcon(""), "About", self)
        helpMenu.addAction(helpAct)
        helpMenu.addAction(aboutAct)


    def keep_silent(self):
        if self.is_silent:
            self.is_silent = False
        else:
            self.is_silent = True

    def alter_current_piece_style(self, style):
        self.current_piece_style = style
        self.load_pieces()

    def render_chessboard(self):

        # set the size and placement, whether to show grid
        self.chessboard = QTableWidget(8, 8, self)
        self.chessboard.setMinimumSize(660, 660)
        self.chessboard.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.chessboard.setFrameShape(QFrame.NoFrame)
        self.chessboard.setShowGrid(False)

        # hide the header
        self.chessboard.horizontalHeader().setVisible(False)
        self.chessboard.verticalHeader().setVisible(False)

        # automatically adjust column width and row height
        self.chessboard.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.chessboard.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)

        for i in range(8):
            # set the square size
            self.chessboard.setRowHeight(i, self.square_size)
            self.chessboard.setColumnWidth(i, self.square_size)

        for hori in range(8):
            for vert in range(8):
                # create item and set font
                self.chessboard.setItem(hori, vert, QTableWidgetItem())
                self.chessboard.item(hori, vert).setFont(
                    QFont("consolas", 10, QFont.Bold)
                )

                # fill different colors for different squares
                if (vert + hori) % 2 == 1:
                    b_color = self.chessboard_style["light"]
                    f_color = self.chessboard_style["bold"]
                else:
                    b_color = self.chessboard_style["bold"]
                    f_color = self.chessboard_style["light"]
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

    def game(self, signal):
        # refresh chessboard after one certain move
        data = json.loads(signal)
        board, move = data["board"], data["move"]
        turn, bout = board["turn"], int(board["full"])
        current_row = self.manual_zone.rowCount()

        if turn == "b":
            self.manual_zone.insertRow(current_row)
            current_row = self.manual_zone.rowCount()
            for j in range(3):
                self.manual_zone.setItem(current_row - 1, j, QTableWidgetItem())

            self.manual_zone.item(current_row - 1, 0).setText(str(bout))
            self.manual_zone.item(current_row - 1, 1).setText(move)
        else:
            self.manual_zone.item(current_row - 1, 2).setText(move)

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
        pos = event.pos()
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
    window = VBord()
    window.show()
    sys.exit(app.exec())
