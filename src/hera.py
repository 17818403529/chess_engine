import sys
import os
import json
from random import choice, randint, random
import time

import pygame
from chess import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5 import *

config_path = os.path.dirname(os.path.abspath(__file__)) + "\\config.json"
with open(config_path, "r", encoding="utf-8") as f:
    config = json.load(f)
pygame.mixer.init()


class GameOver(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setGeometry(300, 200, 350, 150)
        layout = QVBoxLayout()
        self.setWindowFlags(
            Qt.WindowCloseButtonHint
            | Qt.WindowMaximizeButtonHint
            | Qt.MSWindowsFixedSizeDialogHint
        )
        self.setWindowTitle("GAME OVER")
        self.result = QLabel("")
        font = QFont("Sitka Small", 14)
        font.setBold(True)
        self.result.setFont(font)
        self.result.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        layout.addWidget(self.result)
        self.score = QLabel("")
        font = QFont("Gabriola", 28)
        font.setItalic(True)
        font.setBold(True)
        self.score.setFont(font)
        self.score.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        layout.addWidget(self.score)
        self.setLayout(layout)

    def append_result(self, status):
        self.result.setText(status[0])
        self.score.setText(status[1])
        self.show()


class Player(QLabel):
    def __init__(self, symbol, window):
        super().__init__(symbol, window)
        self.setFont(QFont(config["player_font"], 18))


class Clock(QLabel):
    def __init__(self, window):
        super().__init__("5:00", window)
        self.setFont(QFont(config["clock_font"], 28))
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


class Manual(QTableWidget):
    def __init__(self, window):
        super().__init__(window)
        self.window = window
        self.setColumnCount(3)
        self.setFrameShape(QFrame.NoFrame)
        self.setShowGrid(False)
        self.horizontalHeader().setVisible(False)
        self.verticalHeader().setVisible(False)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.light = self.window.convert_color(config["window_color"])
        self.bold = self.window.convert_color(config["manual_bold_color"])

    def reset(self):
        self.setRowCount(0)

    def append_row(self):
        # insert new row
        self.setRowCount(self.rowCount() + 1)
        self.setRowHeight(self.rowCount() - 1, int(self.window.basic_size * 0.6))
        for j in range(3):
            newItme = QTableWidgetItem()

            # set font
            font = QFont(
                config["manual_font"],
                int(config["manual_font_size"] * self.window.zoom_ratio),
            )
            newItme.setFont(font)

            # set background color
            self.setItem(self.rowCount() - 1, j, newItme)
            if self.rowCount() % 2 == 1:
                self.item(self.rowCount() - 1, j).setBackground(self.light)
            else:
                self.item(self.rowCount() - 1, j).setBackground(self.bold)

    def append_move(self, move, turn, full):
        if turn == "b":
            self.append_row()
            self.item(self.rowCount() - 1, 0).setText(str(full))
            self.item(self.rowCount() - 1, 1).setText(move)
        else:
            self.item(self.rowCount() - 1, 2).setText(move)

    def append_result(self, status):
        self.append_row()
        self.item(self.rowCount() - 1, 1).setText(status[1])


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
        self.ch = Chess()
        self.move_history = {}
        self.game_signal = game_signal
        chess = self.ch.convert(fen)
        status = self.ch.is_game_unplayable(chess)
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
            self.move_history[move] = self.ch.gen_fen(chess).split()[0]
            status = self.ch.judge(chess, move, self.move_history)
            self.game["move"] = move
            self.game["chess"] = chess
            self.game["status"] = status
            self.signal.emit(json.dumps(self.game))
            if status:
                # game over
                break
            # time.sleep(randint(1, 3) + random())
            time.sleep(0.1)


class Hera(QMainWindow):

    # signals
    clock_signal = pyqtSignal(str)
    game_signal = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):

        # add widgets
        self.board = QTableWidget(8, 8, self)
        self.manual = Manual(self)
        self.black_player = Player("StockFish 8", self)
        self.white_player = Player("Spike 1.4", self)
        self.black_clock = Clock(self)
        self.white_clock = Clock(self)
        self.game_over = GameOver()

        # widget appearance
        self.setWindowTitle("Hera")
        self.setAcceptDrops(True)
        self.board.horizontalHeader().setVisible(False)
        self.board.verticalHeader().setVisible(False)
        self.board.setFrameShape(QFrame.NoFrame)
        self.board.setShowGrid(False)

        # setup Geometry
        self.std_size = None
        self.basic_size = None
        self.zoom_ratio = None
        self.spacing = {"top": 32, "shaft": 5}
        self.cal_basic_size()
        window_height, window_width = (
            self.basic_size * 8 + self.spacing["top"] + self.spacing["shaft"] * 2,
            self.basic_size * 14,
        )
        self.setGeometry(
            self.basic_size * 4, self.basic_size * 2, window_width, window_height
        )

        # load Config and Resource Files
        self.piece_size = None
        self.is_silent = True
        self.game_thread = None
        self.clock_thread = None
        self.board_styles = config["board_styles"]
        self.current_board_style = config["board_styles"][config["current_board_style"]]
        self.piece_image = {}
        self.piece_styles = config["piece_styles"]
        self.current_piece_style = config["current_piece_style"]
        self.piece_image_dir = config["piece_image_dir"]
        self.load_piece_image()
        self.sound_dir = config["sound_dir"]
        self.move_sound = pygame.mixer.Sound(self.sound_dir + "move.wav")

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

        # game and thread
        self.chess = None
        self.game_thread = None
        self.clock_thread = None
        self.history = {}

        # draw widgets
        self.draw_menu()
        self.draw_board()
        self.draw_side()

    def convert_color(self, rgb):
        return QColor(rgb[0], rgb[1], rgb[2])

    def cal_basic_size(self, is_initial=True):
        if is_initial:
            desktop = QApplication.desktop()
            screenRect = desktop.screenGeometry()
            width = screenRect.width()
            self.basic_size = screenRect.width() // 25
            self.std_size = screenRect.width() // 25
        else:
            width = self.geometry().width()
            height = self.geometry().height()
            self.basic_size = min(
                (height - self.spacing["top"] - self.spacing["shaft"] * 2) // 8,
                width // 14,
            )
        self.zoom_ratio = self.basic_size / self.std_size
        self.spacing["hori"] = self.basic_size // 3

    def load_piece_image(self):
        # load the picture of each piece from disk
        suffix = self.piece_styles[self.current_piece_style][0]
        self.piece_size = self.piece_styles[self.current_piece_style][1]
        self.piece_size = int(self.piece_size * self.zoom_ratio)

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
        standardAct.triggered.connect(lambda: self.menu_create_game("standard"))
        newGameMenu.addAction(standardAct)

        fromFenAct = QAction(QIcon(""), "from FEN...", self)
        fromFenAct.triggered.connect(lambda: self.menu_create_game("from FEN..."))
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
                lambda: self.menu_alter_current_board_style(self.sender().text())
            )
            boardStyleMenu.addAction(styleAct)

        # "piece style" submenu
        pieceStyleMenu = configMenu.addMenu("Pieces Style")

        for style in self.piece_styles.keys():
            styleAct = QAction(QIcon(""), style, self)
            styleAct.triggered.connect(
                lambda: self.menu_alter_current_piece_style(self.sender().text())
            )
            pieceStyleMenu.addAction(styleAct)

        # "sound" submenu
        soundMenu = configMenu.addMenu("Sound")

        adjustVolumeAct = QAction(QIcon(""), "Adjust Volume", self)
        soundMenu.addAction(adjustVolumeAct)

        keepSilentAct = QAction(QIcon(""), "Keep Silent", self)
        keepSilentAct.triggered.connect(self.menu_keep_silent)
        soundMenu.addAction(keepSilentAct)

        # the "Help Menu"
        helpMenu = menuBar.addMenu("Help")

        helpAct = QAction(QIcon(""), "Help", self)
        helpAct.setShortcut("Ctrl+H")
        helpMenu.addAction(helpAct)

        aboutAct = QAction(QIcon(""), "About", self)
        helpMenu.addAction(aboutAct)

    def menu_alter_current_piece_style(self, style):
        self.current_piece_style = style
        self.load_piece_image()

    def menu_alter_current_board_style(self, style):
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

    def menu_create_game(self, mode):
        self.manual.reset()
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

    def menu_keep_silent(self):
        if self.is_silent:
            self.is_silent = False
        else:
            self.is_silent = True

    def draw_side(self):

        self.black_player.setFont(
            QFont(
                config["player_font"], int(config["player_font_size"] * self.zoom_ratio)
            )
        )
        self.black_clock.setFont(
            QFont(
                config["clock_font"], int(config["clock_font_size"] * self.zoom_ratio)
            )
        )
        self.white_player.setFont(
            QFont(
                config["player_font"], int(config["player_font_size"] * self.zoom_ratio)
            )
        )
        self.white_clock.setFont(
            QFont(
                config["clock_font"], int(config["clock_font_size"] * self.zoom_ratio)
            )
        )

        self.black_clock.setGeometry(
            self.spacing["hori"] * 2 + self.basic_size * 8,
            self.spacing["top"],
            self.basic_size * 2,
            self.basic_size,
        )
        self.black_player.setGeometry(
            self.spacing["hori"] * 2 + self.basic_size * 8,
            self.spacing["top"] + self.basic_size,
            self.basic_size * 2,
            self.basic_size,
        )

        self.white_player.setGeometry(
            self.spacing["hori"] * 2 + self.basic_size * 8,
            self.spacing["top"] + self.basic_size * 6,
            self.basic_size * 2,
            self.basic_size,
        )
        self.white_clock.setGeometry(
            self.spacing["hori"] * 2 + self.basic_size * 8,
            self.spacing["top"] + self.basic_size * 7,
            self.basic_size * 2,
            self.basic_size,
        )

        self.manual.setGeometry(
            self.spacing["hori"] * 2 + self.basic_size * 8,
            self.spacing["top"] + self.basic_size * 2,
            self.basic_size * 5,
            self.basic_size * 4,
        )

        self.manual.setColumnWidth(0, self.basic_size)
        self.manual.setColumnWidth(1, self.basic_size * 2)
        self.manual.setColumnWidth(2, self.basic_size * 2)

    def draw_board(self):

        self.board.setGeometry(
            self.spacing["hori"],
            self.spacing["top"],
            self.basic_size * 8,
            self.basic_size * 8,
        )

        for i in range(8):
            # setup square size
            self.board.setRowHeight(i, self.basic_size)
            self.board.setColumnWidth(i, self.basic_size)

        # set square color

        light = self.convert_color(self.current_board_style["white"])
        bold = self.convert_color(self.current_board_style["black"])

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
                self.manual.append_move(move, turn, full)

            if status:
                self.clock_signal.emit("-")
                self.game_over.append_result(status)
                self.manual.append_result(status)
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
        self.cal_basic_size(is_initial=False)
        self.piece_size = int(
            self.piece_styles[self.current_piece_style][1] * self.zoom_ratio
        )
        self.draw_board()
        self.draw_side()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    hera = Hera()
    hera.show()
    sys.exit(app.exec())
