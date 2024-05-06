import sys
import os
import json
from random import choice, randint, random
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


class GameOver(QWidget):
    def __init__(self, score, result):
        super().__init__()
        result = QLabel(result)
        result.setAlignment(Qt.AlignCenter)
        result.setFont(QFont("Roman times", 18, QFont.Bold))
        score = QLabel(score)
        score.setAlignment(Qt.AlignCenter)
        score.setFont(QFont("Roman times", 18, QFont.Bold))
        button = QPushButton("OK")
        button.clicked.connect(self.close)
        button.setFont(QFont("Roman times", 18, QFont.Bold))
        layout = QVBoxLayout()
        layout.addWidget(result)
        layout.addWidget(score)
        layout.addWidget(button)
        self.setLayout(layout)
        self.setWindowFlags(Qt.FramelessWindowHint)


class Player(QLabel):
    def __init__(self, symbol):
        super().__init__(symbol)
        self.setFont(QFont(config["player_font"], 18, QFont.Bold))


class Clock(QLabel):
    def __init__(self):
        super().__init__("5:00")
        self.setFont(QFont(config["clock_font"], 28, QFont.Bold))
        self.setAutoFillBackground(True)
        self.setAlignment(Qt.AlignCenter)
        self.timing_color = QPalette()
        self.stop_color = QPalette()

    def set_color(self, timing_color, stop_color):
        self.timing_color.setColor(QPalette.Window, timing_color)
        self.stop_color.setColor(QPalette.Window, stop_color)

    def timing(self):
        self.setPalette(self.timing_color)

    def stop(self):
        self.setPalette(self.stop_color)

    def display(self, seconds):
        self.setText(time.strftime("%M:%S", time.localtime(seconds)))


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

    def __init__(self, clock_signal, time_limit, time_step):
        super().__init__()
        self.turn = None
        self.clock_signal = clock_signal
        self.clock_signal.connect(self.swap)
        self.clock = {"event": "clock", "w": time_limit, "b": time_limit, "turn": None}
        self.time_step = time_step

    def swap(self, clock_signal):
        self.turn = clock_signal
        self.clock["turn"] = clock_signal

    def run(self):
        self.signal.emit(json.dumps(self.clock))
        while True:
            start_time = time.time()
            time.sleep(0.001)
            used_time = time.time() - start_time
            if self.turn:
                if self.turn == "-":
                    break
                ts = self.clock[self.turn]
                self.clock[self.turn] -= used_time
                if int(ts) - int(self.clock[self.turn]) == 1:
                    self.signal.emit(json.dumps(self.clock))


class GameThread(QThread):

    signal = pyqtSignal(str)

    def __init__(self, game_signal, fen):
        super().__init__()
        self.cl = ChessLib()
        self.move_history = {}
        self.game_signal = game_signal
        chess = self.cl.convert(fen)
        status = self.cl.is_game_unplayable(chess)
        self.game = {
            "event": "game",
            "move": "",
            "chess": chess,
            "status": status,
        }

    def run(self):
        self.signal.emit(json.dumps(self.game))
        while True:
            move, chess = engine(self.game["chess"])
            status = self.cl.judge(chess, move, self.move_history)
            self.move_history[move] = self.cl.gen_fen(chess)
            self.game["move"] = move
            self.game["chess"] = chess
            self.game["status"] = status
            self.signal.emit(json.dumps(self.game))
            if status:
                # game over
                break
            time.sleep(randint(1, 3) + random())


class Hera(QMainWindow):

    # signals
    clock_signal = pyqtSignal(str)
    game_signal = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        # basic appearance setup
        self.setWindowTitle("Hera")
        self.setAcceptDrops(True)
        self.board = QTableWidget(8, 8, self)
        self.manual = QTableWidget(1, 3, self)
        self.black_player = Player("Black")
        self.black_clock = Clock()
        self.white_player = Player("White")
        self.white_clock = Clock()
        self.board.setParent(self)
        self.manual.setParent(self)
        self.black_player.setParent(self)
        self.black_clock.setParent(self)
        self.white_player.setParent(self)
        self.white_clock.setParent(self)

        # load config
        self.piece_image_dir = config["piece_image_dir"]
        self.sound_dir = config["sound_dir"]
        self.piece_styles = config["piece_styles"]
        self.board_styles = config["board_styles"]
        self.current_piece_style = config["current_piece_style"]
        self.current_board_style = config["board_styles"][config["current_board_style"]]

        # setup color
        self.window_color = QPalette()
        self.window_color.setColor(
            QPalette.Window, self.convert_color(config["window_color"])
        )
        self.setPalette(self.window_color)

        self.black_clock.set_color(
            self.convert_color(self.current_board_style["clock"]),
            self.convert_color(config["window_color"]),
        )
        self.white_clock.set_color(
            self.convert_color(self.current_board_style["clock"]),
            self.convert_color(config["window_color"]),
        )

        # system variables
        self.piece_image = {}
        self.piece_size = None
        self.is_silent = True
        self.game_thread = None

        # game
        self.chess = None
        self.game_thread = None
        self.clock_thread = None

        # layout correlation
        self.basic_size = None
        self.spacing = {"top": 40, "shaft": 5}
        self.cal_basic_size()
        window_height, window_width = (
            self.basic_size * 10 + self.spacing["top"] + self.spacing["shaft"] * 3,
            self.basic_size * 14,
        )
        self.setGeometry(
            self.basic_size * 4, self.basic_size * 2, window_width, window_height
        )

        # load resource file
        self.load_piece_image()
        self.move_sound = pygame.mixer.Sound(self.sound_dir + "move.wav")

        # append components
        self.draw_menu()
        self.draw_board()
        self.draw_manual()
        self.draw_clock()

    def convert_color(self, rgb):
        return QColor(rgb[0], rgb[1], rgb[2])

    def cal_basic_size(self):
        desktop = QApplication.desktop()
        screenRect = desktop.screenGeometry()
        self.basic_size = screenRect.width() // 25
        self.std_size = screenRect.width() // 25
        self.spacing["hori"] = self.basic_size // 3

    def load_piece_image(self):
        # load the picture of each piece from disk
        suffix = self.piece_styles[self.current_piece_style][0]
        self.piece_size = self.piece_styles[self.current_piece_style][1]
        self.piece_size = self.piece_size * self.basic_size // self.std_size

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
        standardAct.triggered.connect(lambda: self.create_game("standard"))
        newGameMenu.addAction(standardAct)

        fromFenAct = QAction(QIcon(""), "from FEN...", self)
        fromFenAct.triggered.connect(lambda: self.create_game("from FEN..."))
        newGameMenu.addAction(fromFenAct)

        fromPositionAct = QAction(QIcon(""), "from position", self)
        fromPositionAct.triggered.connect(lambda: self.new_game("from position"))
        newGameMenu.addAction(fromPositionAct)

        # append "Config" menu
        configMenu = menuBar.addMenu("Configs")

        # "board style" submenu
        boardStyleMenu = configMenu.addMenu("Board Style")

        for style in self.board_styles.keys():
            styleAct = QAction(QIcon(""), style, self)
            styleAct.triggered.connect(
                lambda: self.alter_current_board_style(self.sender().text())
            )
            boardStyleMenu.addAction(styleAct)

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

    def alter_current_board_style(self, style):
        self.current_board_style = self.board_styles[style]
        self.black_clock.set_color(
            self.convert_color(self.current_board_style["clock"]),
            self.convert_color(config["window_color"]),
        )
        self.white_clock.set_color(
            self.convert_color(self.current_board_style["clock"]),
            self.convert_color(config["window_color"]),
        )

        self.draw_board()

    def create_game(self, mode):
        self.manual.clearContents()
        if mode == "standard":
            fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
            ok = True
        elif mode == "from FEN...":
            fen, ok = QInputDialog.getText(self, "FEN", "Input fen:")

        if ok and fen:
            if self.game_thread:
                self.game_thread.terminate()
            if self.clock_thread:
                self.clock_thread.terminate()
            self.game_thread = GameThread(self.game_signal, fen)
            self.game_thread.signal.connect(self.display_game)
            self.game_thread.start()
            self.clock_thread = ClockThread(self.clock_signal, 150, 1)
            self.clock_thread.signal.connect(self.display_game)
            self.clock_thread.start()

    def keep_silent(self):
        if self.is_silent:
            self.is_silent = False
        else:
            self.is_silent = True

    def draw_clock(self):
        self.black_player.setGeometry(
            self.spacing["hori"],
            self.spacing["top"],
            self.basic_size * 2,
            self.basic_size,
        )
        self.black_clock.setGeometry(
            self.spacing["hori"] + self.basic_size * 6,
            self.spacing["top"],
            self.basic_size * 2,
            self.basic_size,
        )
        self.white_player.setGeometry(
            self.spacing["hori"],
            self.spacing["top"] + self.basic_size * 9 + self.spacing["shaft"] * 2,
            self.basic_size * 2,
            self.basic_size,
        )
        self.white_clock.setGeometry(
            self.spacing["hori"] + self.basic_size * 6,
            self.spacing["top"] + self.basic_size * 9 + self.spacing["shaft"] * 2,
            self.basic_size * 2,
            self.basic_size,
        )

        self.black_player.setFont(
            QFont(
                config["player_font"], 18 * self.basic_size // self.std_size, QFont.Bold
            )
        )
        self.black_clock.setFont(
            QFont(
                config["player_font"], 28 * self.basic_size // self.std_size, QFont.Bold
            )
        )
        self.white_player.setFont(
            QFont(
                config["player_font"], 18 * self.basic_size // self.std_size, QFont.Bold
            )
        )
        self.white_clock.setFont(
            QFont(
                config["player_font"], 28 * self.basic_size // self.std_size, QFont.Bold
            )
        )

    def draw_board(self):

        self.board.setGeometry(
            self.spacing["hori"],
            self.spacing["top"] + self.basic_size + self.spacing["shaft"],
            self.basic_size * 8,
            self.basic_size * 8,
        )

        for i in range(8):
            # setup square size
            self.board.setRowHeight(i, self.basic_size)
            self.board.setColumnWidth(i, self.basic_size)

        self.board.horizontalHeader().setVisible(False)
        self.board.verticalHeader().setVisible(False)
        self.board.setFrameShape(QFrame.NoFrame)
        self.board.setShowGrid(False)

        # set square color

        light = self.convert_color(self.current_board_style["light"])
        bold = self.convert_color(self.current_board_style["bold"])

        for file in range(8):
            for rank in range(8):
                # create item and set font
                self.board.setItem(file, rank, QTableWidgetItem())
                self.board.item(file, rank).setFont(
                    QFont("consolas", self.basic_size // 7, QFont.Bold)
                )

                # fill different colors for different squares
                if (rank + file) % 2 == 1:
                    self.board.item(file, rank).setBackground(light)
                else:
                    self.board.item(file, rank).setBackground(bold)

    def draw_manual(self):

        self.manual.setGeometry(
            self.basic_size * 8 + self.spacing["hori"] * 2,
            self.spacing["top"],
            self.basic_size * 7,
            self.basic_size * 10,
        )

        # setup the base appearance and scaling behavior
        self.manual.setFrameShape(QFrame.NoFrame)
        self.manual.setShowGrid(False)
        self.manual.horizontalHeader().setVisible(False)
        self.manual.verticalHeader().setVisible(False)
        self.manual.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # setup the column width
        self.manual.setColumnWidth(0, self.basic_size)
        self.manual.setColumnWidth(1, self.basic_size * 2)
        self.manual.setColumnWidth(2, self.basic_size * 2)

    def display_game(self, signal):
        # refresh board after one certain move in games
        data = json.loads(signal)
        if data["event"] == "game":
            move, chess, status = data["move"], data["chess"], data["status"]
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

            if not self.is_silent:
                self.move_sound.play()

            if move:
                self.clock_signal.emit(chess["turn"])
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

            if status:
                self.clock_signal.emit("-")
                self.msg = GameOver(status)
                self.msg.show()
        else:
            w_clock, b_clock, turn = data["w"], data["b"], data["turn"]
            self.white_clock.display(w_clock)
            self.black_clock.display(b_clock)

            if data["turn"] == "w":
                self.white_clock.timing()
                self.black_clock.stop()
            elif data["turn"] == "b":
                self.black_clock.timing()
                self.white_clock.stop()

    def resizeEvent(self, *args, **kwargs):
        window_width = self.geometry().width()
        window_height = self.geometry().height()
        self.basic_size = min(
            (window_height - self.spacing["top"] - self.spacing["shaft"] * 3) // 10,
            window_width // 14,
        )
        self.spacing["hori"] = self.basic_size // 3
        self.piece_size = self.piece_styles[self.current_piece_style][1]
        self.piece_size = self.piece_size * self.basic_size // self.std_size
        self.draw_board()
        self.draw_manual()
        self.draw_clock()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    hera = Hera()
    hera.show()
    sys.exit(app.exec())
