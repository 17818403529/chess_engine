import sys
import os
import json
from random import choice
import time

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


class Player(QLabel):
    def __init__(self, symbol):
        super().__init__(symbol)
        self.setFont(QFont("Roman times", 18, QFont.Bold))


class Clock(QLabel):
    def __init__(self, symbol):
        super().__init__(symbol)
        self.setFont(QFont("Consolas", 28, QFont.Bold))
        self.setAutoFillBackground(True)


class Piece(QLabel):
    def __init__(self, iamge, size):
        super().__init__("")
        self.setAlignment(Qt.AlignCenter)
        if iamge:
            self.setPixmap(iamge.scaled(size, size))

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            drag = QDrag(self)
            mimeData = QMimeData()

            pixmap = QPixmap(self.size())
            self.render(pixmap)
            drag.setPixmap(pixmap)

            drag.setMimeData(mimeData)
            drag.exec_(Qt.MoveAction)


class ClockThread(QThread):
    signal = pyqtSignal(str)

    def __init__(self, total, added, game_signal):
        super().__init__()
        self.game_signal = game_signal
        self.game_signal.connect(self.change_hands)
        self.clock = {"w": total, "b": total, "turn": "w"}
        self.turn = self.clock["turn"]
        self.added = added

    def change_hands(self, game_signal):
        clock = json.loads(game_signal)
        self.clock = clock
        self.clock[self.turn] += self.added
        self.turn = clock["turn"]

    def run(self):
        while True:
            start_time = time.time()
            sleep(0.001)
            end_time = time.time()
            used_time = end_time - start_time
            if self.clock[self.turn] - int(self.clock[self.turn]) < used_time:
                self.clock[self.turn] -= used_time
                self.signal.emit(json.dumps(self.clock))
            else:
                self.clock[self.turn] -= used_time


class PlayerThread(QThread):

    signal = pyqtSignal(str)

    def __init__(self, player_signal, fen):
        super().__init__()
        self.oppo = "w" if self.side == "b" else "b"
        self.player_signal = player_signal
        self.player_signal.connect(self.activate)
        self.fen = fen
        self.chess_dict = Chess.gen_chess_dict()
        self.chess = Chess.convert(self.fen, self.chess_dict)


    def activate(self):
        move, self.chess = engine(self.chess, self.chess_dict)
        self.signal.emit(move)

    def run(self):
        while True:
            sleep(1000)


class Hera(QMainWindow):

    # signals
    clock_signal = pyqtSignal(str)
    white_player_signal = pyqtSignal(str)
    black_player_signal = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        # basic appearance setup
        self.setWindowTitle("Hera")
        self.setGeometry((1920 - 920) // 7 * 2, (1080 - 720) // 3, 920, 720)
        self.setAcceptDrops(True)
        self.board = QTableWidget(8, 8, self)
        self.manual = QTableWidget(1, 3, self)
        self.black_player = Player("Miss Ace")
        self.black_clock = Clock("04:35")
        self.white_player = Player("Souna")
        self.white_clock = Clock("07:22")
        self.board.setParent(self)
        self.manual.setParent(self)
        self.black_player.setParent(self)
        self.black_clock.setParent(self)
        self.white_player.setParent(self)
        self.white_clock.setParent(self)

        self.timing_color = QPalette()
        self.timing_color.setColor(QPalette.Window, QColor(143, 188, 139))
        self.stop_color = QPalette()
        self.stop_color.setColor(QPalette.Window, QColor(250, 235, 215))

        # load config
        self.piece_image_dir = config["piece_image_dir"]
        self.sound_dir = config["sound_dir"]
        self.board_style = config["board_style"]
        self.square_size = config["square_size"]
        self.piece_styles = config["piece_styles"]
        self.current_piece_style = config["current_piece_style"]

        # system variables
        self.piece_image = {}
        self.piece_size = None
        self.is_silent = True
        self.game_thread = None

        # load resource file
        self.load_piece_image()
        self.move_sound = pygame.mixer.Sound(self.sound_dir + "move.wav")

        # append components
        self.draw_menu()
        self.draw_board(80)
        self.draw_manual(80)
        self.draw_info(80)

        # game
        self.chess_dict = Chess.gen_chess_dict()
        self.chess = None
        self.white_player_thread = None
        self.black_player_thread = None
        self.clock_thread = None

    def display_clock(self, signal):
        data = json.loads(signal)
        if data["turn"] == "w":
            self.white_clock.setPalette(self.timing_color)
            self.black_clock.setPalette(self.stop_color)
            w_clock = time.strftime("%M:%S", time.localtime(data["w"]))
            self.white_clock.setText(w_clock)
            data["turn"] = "b"
        else:
            self.black_clock.setPalette(self.timing_color)
            self.white_clock.setPalette(self.stop_color)
            b_clock = time.strftime("%M:%S", time.localtime(data["b"]))
            self.black_clock.setText(b_clock)
            data["turn"] = "w"
        self.clock_signal.emit(json.dumps(data))

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

    def draw_menu(self):
        menuBar = self.menuBar()

        # append "File" menu
        fileMenu = menuBar.addMenu("Files")

        openAct = QAction(QIcon(""), "Open...", self)
        openAct.setShortcut("Ctrl+F")
        openAct = QAction(QIcon(""), "Open...", self)
        fileMenu.addAction(openAct)

        # append "Game" menu
        gameMenu = menuBar.addMenu("Game")

        # append "New Game" submenu
        newGameMenu = gameMenu.addMenu("New Game")

        standardAct = QAction(QIcon(""), "standard", self)
        standardAct.triggered.connect(lambda: self.start_new_game("standard"))
        newGameMenu.addAction(standardAct)

        fromPositionAct = QAction(QIcon(""), "from position", self)
        fromPositionAct.triggered.connect(lambda: self.new_game("from position"))
        newGameMenu.addAction(fromPositionAct)

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


    def start_new_game(self, mode):
        if mode == "standard":
            fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
        self.chess = Chess.convert(fen, self.chess_dict)
        self.white_player_thread = PlayerThread(
            "w", 150, 0, self.white_player_signal, fen
        )
        self.white_player_signal.signal.connect(self.display_move)
        self.black_player_thread = PlayerThread(
            "b", 150, 0, self.black_player_signal, fen
        )
        self.black_player_thread.signal.connect(self.display_move)
        self.clock_thread = ClockThread(150, 0, self.clock_signal)
        self.clock_thread.signal.connect(self.display_clock)
        self.clock_thread.start()

    def keep_silent(self):
        if self.is_silent:
            self.is_silent = False
        else:
            self.is_silent = True

    def draw_info(self, basic_width):
        self.black_player.setGeometry(10, 32, basic_width * 2, basic_width)
        self.black_clock.setGeometry(
            10 + basic_width * 6, 32, basic_width * 2, basic_width
        )
        self.white_player.setGeometry(
            10, 32 + basic_width * 9, basic_width * 2, basic_width
        )
        self.white_clock.setGeometry(
            10 + basic_width * 6, 32 + basic_width * 9, basic_width * 2, basic_width
        )

        self.black_player.setFont(
            QFont("Roman times", 18 * basic_width // 80, QFont.Bold)
        )
        self.black_clock.setFont(
            QFont("Roman times", 28 * basic_width // 80, QFont.Bold)
        )
        self.white_player.setFont(
            QFont("Roman times", 18 * basic_width // 80, QFont.Bold)
        )
        self.white_clock.setFont(
            QFont("Roman times", 28 * basic_width // 80, QFont.Bold)
        )

    def draw_board(self, basic_width):

        square_size = basic_width
        self.board.setGeometry(10, 32 + basic_width, square_size * 8, square_size * 8)

        for i in range(8):
            # setup square size
            self.board.setRowHeight(i, square_size)
            self.board.setColumnWidth(i, square_size)

        self.board.horizontalHeader().setVisible(False)
        self.board.verticalHeader().setVisible(False)
        self.board.setFrameShape(QFrame.NoFrame)
        self.board.setShowGrid(False)

        # set square color
        light, bold = (
            self.board_style["light"],
            self.board_style["bold"],
        )

        style = {
            "light": QColor(light[0], light[1], light[2]),
            "bold": QColor(bold[0], bold[1], bold[2]),
        }

        for file in range(8):
            for rank in range(8):
                # create item and set font
                self.board.setItem(file, rank, QTableWidgetItem())
                self.board.item(file, rank).setFont(
                    QFont("consolas", basic_width // 7, QFont.Bold)
                )

                # fill different colors for different squares
                if (rank + file) % 2 == 1:
                    b_color = style["light"]
                    f_color = style["bold"]
                else:
                    b_color = style["bold"]
                    f_color = style["light"]
                self.board.item(file, rank).setBackground(b_color)
                self.board.item(file, rank).setForeground(f_color)

                # fill in the row and column numbers
                if file == 7:
                    self.board.item(file, rank).setTextAlignment(
                        Qt.AlignRight | Qt.AlignBottom
                    )
                    self.board.item(file, rank).setText("abcdefgh"[rank])
                if rank == 0:
                    self.board.item(file, rank).setTextAlignment(
                        Qt.AlignLeft | Qt.AlignTop
                    )
                    self.board.item(file, rank).setText("87654321"[file])
        # the a1 square
        self.board.item(7, 0).setText("1")

    def draw_manual(self, basic_width):

        self.manual.setGeometry(
            basic_width * 8 + 20,
            basic_width + 32,
            int(basic_width * 2.6),
            basic_width * 8,
        )

        # setup the base appearance and scaling behavior
        self.manual.setFrameShape(QFrame.NoFrame)
        self.manual.setShowGrid(False)
        self.manual.horizontalHeader().setVisible(False)
        self.manual.verticalHeader().setVisible(False)
        self.manual.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # setup the column width
        self.manual.setColumnWidth(0, int(basic_width * 0.58))
        self.manual.setColumnWidth(1, basic_width)
        self.manual.setColumnWidth(2, basic_width)

    def display_move(self, signal):

        # refresh board after one certain move in games
        game = json.loads(signal)
        move, chess, status = game["move"], game["chess"], game["status"]
        if chess["turn"] == "w":
            self.white_player_signal.emit(move)
        else:
            self.black_player_signal.emit(move)

        if status:
            QMessageBox.information(self, "Error", status)
            return False

        # refresh board
        for rank in range(8):
            for file in range(8):
                square = "abcdefgh"[file] + "87654321"[rank]
                if square not in chess["blank"]:
                    # put piece at a square if it is not blank
                    symbol = chess["pieces"][square]
                    piece = Piece(self.piece_image[symbol], self.piece_size)
                else:
                    piece = Piece(None, self.piece_size)

                self.board.setCellWidget(rank, file, piece)

        # refresh manual area
        turn, full = chess["turn"], int(chess["full"])
        current_row = self.manual.rowCount()

        if turn == "b":
            # append a new chess row
            self.manual.insertRow(current_row)
            current_row = self.manual.rowCount()
            for j in range(3):
                self.manual.setItem(current_row - 1, j, QTableWidgetItem())

            # append move
            self.manual.item(current_row - 1, 0).setText(str(full))
            self.manual.item(current_row - 1, 1).setText(move)
        else:
            # append move
            self.manual.item(current_row - 1, 2).setText(move)

        if not self.is_silent:
            self.move_sound.play()

    def resizeEvent(self, *args, **kwargs):
        window_width = self.geometry().width()
        window_height = self.geometry().height()

        basic_width = min(((window_width - 30) // 11), ((window_height - 32) // 10))

        self.draw_board(basic_width)
        self.draw_manual(basic_width)
        self.draw_info(basic_width)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    hera = Hera()
    hera.show()
    sys.exit(app.exec())
