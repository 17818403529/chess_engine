import sys
import os
import json

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5 import *
import pygame

from models import *


class Game(QThread):
    def __init__(self, signal):
        super().__init__()
        self.move_list = []
        self.signal = signal
        self.init_fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
        self.chess_dict = Chess.gen_chess_dict()

    def run(self):
        fen = self.init_fen
        while True:
            board = Chess.convert(fen, self.chess_dict)
            legal_moves = Chess.gather_legal_moves(board, self.chess_dict)
            move = engine(fen, self.chess_dict)
            if move in legal_moves.values():
                for key in legal_moves.keys():
                    if legal_moves[key] == move:
                        _move = key
                        break
            else:
                return False

            board = Chess.take_a_move(board, _move, self.chess_dict)
            fen = Chess.gen_fen(board)
            print(_move, fen)
            self.signal.emit(json.dumps(board))


class VBoard(QMainWindow):

    signal = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.title = "VBoard"

        self.load_config()
        self.load_pieces()
        self.load_sound()

        self.signal.connect(self.render_board)
        self.init_window()

    def load_config(self):
        config_path = os.path.dirname(os.path.abspath(__file__)) + "\\config.json"
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)

        # board square color
        light, bold = config["board_style"]["light"], config["board_style"]["bold"]
        self.board_style = {
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

    def init_window(self):
        self.setWindowTitle(self.title)
        self.setGeometry(480, 200, 800, 720)

        self.draw_menu()
        self.draw_board()
        self.show()
        self.chess_thread = Game(self.signal)
        self.chess_thread.start()

    def draw_menu(self):
        menuBar = self.menuBar()

        fileMenu = menuBar.addMenu("Files")
        gameMenu = menuBar.addMenu("Games")
        configMenu = menuBar.addMenu("Configs")

        # the "Pieces Style Menu"
        pieceStyleMenu = configMenu.addMenu("Pieces Style")
        for style in self.piece_styles.keys():
            styleAct = QAction(QIcon(""), style, self)
            pieceStyleMenu.addAction(styleAct)
            styleAct.triggered.connect(
                lambda: self.alter_current_piece_style(self.sender().text())
            )

        openAct = QAction(QIcon(""), "Open...", self)
        openAct.setShortcut("Ctrl+F")
        openAct = QAction(QIcon(""), "Open...", self)
        fileMenu.addAction(openAct)

    def alter_current_piece_style(self, style):
        self.current_piece_style = style
        self.load_pieces()

    def draw_board(self):

        # set the size and placement, whether to show grid
        self.board = QTableWidget(8, 8, self)
        self.board.setGeometry(5, 35, 680, 690)
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

    def render_board(self, signal):
        # refresh board after one certain move
        board = json.loads(signal)

        for hori in range(8):
            for vert in range(8):
                label = QLabel("")
                square = "abcdefgh"[hori] + "87654321"[vert]
                if square not in board["blank"]:
                    # put piece at a square if it is not blank
                    symbol = board["pieces"][square]
                    label.setPixmap(
                        self.pieces[symbol].scaled(self.piece_size, self.piece_size)
                    )
                label.setAlignment(Qt.AlignCenter)
                self.board.setCellWidget(vert, hori, label)
        # self.move_sound.play()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = VBoard()
    sys.exit(app.exec())
