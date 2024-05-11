import sys
import os
import json
import time
import sys

import pygame
from chess import *
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from PyQt6.QtCore import *
from PyQt6 import *
import subprocess

current = os.path.dirname(os.path.abspath(__file__))
root = os.path.abspath(os.path.join(current, "../"))
config_path = os.path.join(root, "config.json")
with open(config_path, "r", encoding="utf-8") as f:
    config = json.load(f)

piece_image_dir = os.path.join(root, "resource", "images", "pieces")
sound_dir = os.path.join(root, "resource", "sounds")
manual_bar_image_dir = os.path.join(root, "resource", "images", "manual_bar")

pygame.mixer.init()

if sys.platform == "win32":
    timer = time.perf_counter
else:
    timer = time.time


def convert_color(hexcolor):
    hexcolor = hexcolor.replace("#", "0x")
    hexcolor = int(hexcolor, base=16)
    return QColor((hexcolor >> 16) & 0xFF, (hexcolor >> 8) & 0xFF, hexcolor & 0xFF)


class GameOver(QWidget):
    def __init__(self, window):
        super().__init__()
        self.window = window
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Game Over")
        self.setWindowFlags(
            Qt.WindowType.WindowCloseButtonHint
            | Qt.WindowType.WindowMaximizeButtonHint
            | Qt.WindowType.MSWindowsFixedSizeDialogHint
        )
        layout = QVBoxLayout()

        self.result = QLabel("")
        self.result.setFont(QFont("Sitka Small", 14, QFont.Weight.Bold))
        self.result.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.result)

        self.score = QLabel("")
        self.score.setFont(QFont("Gabriola", 28, QFont.Weight.Bold, True))
        self.score.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.score)
        self.setLayout(layout)

    def append_result(self, packet):
        basic_size = self.window.basic_size
        geometry = self.window.geometry()
        left, top = geometry.x(), geometry.y()
        self.setGeometry(
            left + int(basic_size * 2.33),
            top + basic_size * 3,
            int(basic_size * 4.5),
            int(basic_size * 2.1),
        )
        self.result.setText(packet["result"])
        self.score.setText(packet["score"])
        self.show()


class EngineManagement(QWidget):

    def __init__(self, window):
        super().__init__()
        self.window = window
        self.initUI()

    def initUI(self):
        self.setGeometry(300, 300, 360, 160)
        self.setWindowTitle("Engine Management")

        titleLabel = QLabel("Engine 1")
        authorLabel = QLabel("Engine 2")

        self.engine_1 = QComboBox()
        for i in config["installed"].keys():
            self.engine_1.addItem(i)
        self.engine_1.setCurrentText(config["engine_1"])

        self.engine_2 = QComboBox()
        for i in config["installed"].keys():
            self.engine_2.addItem(i)
        self.engine_2.setCurrentText(config["engine_2"])

        formLayout = QFormLayout()
        formLayout.setSpacing(10)

        button = QPushButton("OK")
        button.clicked.connect(self.confirm)

        formLayout.addRow(titleLabel, self.engine_1)
        formLayout.addRow(authorLabel, self.engine_2)
        formLayout.addRow(button)

        self.setLayout(formLayout)

    def confirm(self):
        config["engine_1"] = self.engine_1.currentText()
        config["engine_2"] = self.engine_2.currentText()
        with open(config_path, "w") as f:
            json.dump(config, f)
        self.close()


class Player(QLabel):
    def __init__(self, tag, window):
        super().__init__(tag, window)
        self.setFont(QFont(config["player_font"], 18))

    def reset(self, tag):
        self.setText(tag)


class Clock(QLabel):
    def __init__(self, window):
        super().__init__("5:00", window)
        self.setFont(QFont(config["clock_font"], 28))
        self.setAutoFillBackground(True)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.timing_color = QPalette()
        self.stop_color = QPalette()

    def set_color(self, timing_color, stop_color):
        self.timing_color.setColor(QPalette.ColorRole.Window, timing_color)
        self.stop_color.setColor(QPalette.ColorRole.Window, stop_color)

    def timing(self):
        self.setPalette(self.timing_color)

    def stop(self):
        self.setPalette(self.stop_color)

    def display(self, seconds):
        if seconds < 0:
            seconds = 0.0
        ts = time.strftime("%M:%S", time.localtime(seconds))
        if seconds >= 30:
            self.setText(ts)
        else:
            self.setText(ts + "." + str(int((seconds - int(seconds)) * 10)))


class Piece(QLabel):
    def __init__(self, iamge, style):
        super().__init__("")
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        if iamge:
            self.setPixmap(iamge)
            self.setScaledContents(True)
        if style == "sketching":
            self.setStyleSheet("padding:7.5%")


class Board(QTableWidget):
    def __init__(self, window):
        super().__init__(8, 8, window)
        self.window = window
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.horizontalHeader().setVisible(False)
        self.verticalHeader().setVisible(False)
        self.setFrameShape(QFrame.Shape.NoFrame)
        self.setShowGrid(False)
        self.initUI()

    def initUI(self):
        # set square color

        white = convert_color(self.window.current_board_style["white"])
        black = convert_color(self.window.current_board_style["black"])

        for file in range(8):
            for rank in range(8):
                # create item and set font
                self.setItem(file, rank, QTableWidgetItem())

                # fill different colors for different squares
                if (rank + file) % 2 == 0:
                    self.item(file, rank).setBackground(white)
                else:
                    self.item(file, rank).setBackground(black)

    def zoom(self):
        for i in range(8):
            # setup square size
            self.setRowHeight(i, self.window.basic_size)
            self.setColumnWidth(i, self.window.basic_size)

    def display(self):
        for square in self.window.ch.rules_dict["squares"]:
            file, rank = self.window.ch.convert_square(square)
            if square not in self.window.chess["blank"]:
                # put piece at a square if it is not blank
                symbol = self.window.chess["pieces"][square]
                piece = Piece(
                    self.window.piece_image[symbol], self.window.current_piece_style
                )
            else:
                piece = Piece(None, "")

            self.setCellWidget(7 - rank, file, piece)

            if not self.window.is_silent:
                self.window.move_sound.play()


class ManualBar(QTableWidget):
    def __init__(self, window):
        super().__init__(1, 5, window)
        self.window = window
        self.initUI()

    def initUI(self):
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.horizontalHeader().setVisible(False)
        self.verticalHeader().setVisible(False)
        self.setFrameStyle(QFrame.Shape.NoFrame)
        self.setShowGrid(False)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        for col in range(5):
            self.setItem(0, col, QTableWidgetItem())
            self.setColumnWidth(col, self.window.basic_size)
            self.item(0, col).setBackground(convert_color(config["manual_bold_color"]))

        hori_margin = int(self.window.basic_size * 0.38)
        vert_margin = int(self.window.basic_size * 0.11)

        for i in range(4):
            angle = ["double-left", "left", "right", "double-right"][i]
            label = QLabel("", self)
            iamge = QPixmap(manual_bar_image_dir + angle + ".svg")
            label.setPixmap(iamge)
            label.setScaledContents(True)
            label.setContentsMargins(hori_margin, vert_margin, hori_margin, vert_margin)
            self.setCellWidget(0, i + 1, label)


class Manual(QTableWidget):
    def __init__(self, window):
        super().__init__(window)
        self.window = window
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.horizontalHeader().setVisible(False)
        self.verticalHeader().setVisible(False)
        self.setColumnCount(3)
        self.setFrameStyle(QFrame.Shape.NoFrame)
        self.setShowGrid(False)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.full_color = convert_color(config["manual_bold_color"])

    def reset(self):
        self.setRowCount(0)

    def zoom(self):
        self.setColumnWidth(0, self.window.basic_size)
        self.setColumnWidth(1, self.window.basic_size * 2)
        self.setColumnWidth(2, self.window.basic_size * 2)
        for i in range(self.rowCount()):
            self.item(i, 1).setFont(
                QFont(
                    config["move_font"],
                    int(config["move_font_size"] * self.window.zoom_ratio),
                )
            )
            self.item(i, 2).setFont(
                QFont(
                    config["move_font"],
                    int(config["move_font_size"] * self.window.zoom_ratio),
                )
            )
            self.item(i, 0).setFont(
                QFont(
                    config["full_font"],
                    int(config["full_font_size"] * self.window.zoom_ratio),
                )
            )

    def append_row(self):
        # insert new row
        self.setRowCount(self.rowCount() + 1)
        self.setRowHeight(self.rowCount() - 1, int(self.window.basic_size * 0.45))
        for j in range(3):
            newItme = QTableWidgetItem()

            # set font
            font = QFont(
                config["move_font"],
                int(config["move_font_size"] * self.window.zoom_ratio),
            )
            newItme.setFont(font)

            # set background color
            self.setItem(self.rowCount() - 1, j, newItme)
            if not self.window.is_manual_bar_activated:
                self.scrollToBottom()

    def append_move(self, move, turn, full):
        if turn == "b":
            self.append_row()
            self.item(self.rowCount() - 1, 0).setText(str(full))
            self.item(self.rowCount() - 1, 0).setBackground(self.full_color)
            self.item(self.rowCount() - 1, 0).setTextAlignment(
                Qt.AlignmentFlag.AlignCenter
            )
            self.item(self.rowCount() - 1, 1).setText(move)
        else:
            try:
                self.item(self.rowCount() - 1, 2).setText(move)
            except AttributeError:
                self.append_row()
                self.item(self.rowCount() - 1, 0).setText(str(full))
                self.item(self.rowCount() - 1, 0).setBackground(self.full_color)
                self.item(self.rowCount() - 1, 0).setTextAlignment(
                    Qt.AlignmentFlag.AlignCenter
                )
                self.item(self.rowCount() - 1, 2).setText(move)

    def append_result(self, packet):
        self.append_row()
        self.item(self.rowCount() - 1, 1).setText(packet["score"])


class ClockThread(QThread):

    signal = pyqtSignal(str)

    def __init__(self, clock):
        super().__init__()
        self.clock = clock

    def run(self):
        oppo = "b" if self.clock["turn"] == "w" else "w"
        while True:
            start_time = timer()
            ts = self.clock[self.clock["turn"]]
            if ts < 30:
                time.sleep(0.1)
            else:
                time.sleep(ts - int(ts))
            used_time = timer() - start_time
            self.clock[self.clock["turn"]] -= used_time

            if self.clock[self.clock["turn"]] < 0:
                self.clock[self.clock["turn"]] = 0
                self.signal.emit(json.dumps(self.clock))
                if oppo == "b":
                    game_over = {
                        "event": "game_over",
                        "result": "Overtime, black wins.",
                        "score": "0 - 1",
                    }
                else:
                    game_over = {
                        "event": "game_over",
                        "result": "Overtime, white wins.",
                        "score": "1 - 0",
                    }
                self.signal.emit(json.dumps(game_over))
            else:
                self.signal.emit(json.dumps(self.clock))


class GameThread(QThread):

    signal = pyqtSignal(str)

    def __init__(self, game_signal, fen):
        super().__init__()
        self.ch = Chess()
        self.move_history = {}
        self.game_signal = game_signal
        self.packet = {
            "event": "game",
            "move": "",
            "chess": self.ch.convert(fen),
        }
        self.load_engine()

    def load_engine(self):

        self.engine_1 = subprocess.Popen(
            [config["installed"][config["engine_1"]]["cmd"]],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

        self.engine_1.stdin.write("uci\n")
        self.engine_1.stdin.flush()
        while True:
            resp = self.engine_1.stdout.readline()
            if resp == "uciok\n":
                break

        self.engine_1.stdin.write("isready\n")
        self.engine_1.stdin.flush()
        while True:
            resp = self.engine_1.stdout.readline()
            if resp == "readyok\n":
                break

        self.engine_2 = subprocess.Popen(
            [config["installed"][config["engine_2"]]["cmd"]],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

        self.engine_2.stdin.write("uci\n")
        self.engine_2.stdin.flush()
        while True:
            resp = self.engine_2.stdout.readline()
            if resp == "uciok\n":
                break

        self.engine_2.stdin.write("isready\n")
        self.engine_2.stdin.flush()
        while True:
            resp = self.engine_2.stdout.readline()
            if resp == "readyok\n":
                break

    def run(self):

        if self.packet["chess"]:
            self.signal.emit(json.dumps(self.packet))

        status = self.ch.is_game_over(self.packet["chess"], "", self.move_history)
        if status:
            self.signal.emit(json.dumps(status))
        else:
            while True:
                # get into the game loop
                move, chess = engine(self.packet["chess"])
                self.packet["move"] = move
                self.packet["chess"] = chess
                self.signal.emit(json.dumps(self.packet))

                self.move_history[move] = self.ch.gen_fen(chess).split()[0]
                status = self.ch.is_game_over(chess, move, self.move_history)
                if status:
                    self.signal.emit(json.dumps(status))
                    break


class Hera(QMainWindow):

    # signals
    game_signal = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):

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

        # widget appearance
        self.setWindowTitle("Hera")
        self.setAcceptDrops(True)

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
        self.load_piece_images()
        self.move_sound = pygame.mixer.Sound(os.path.join(sound_dir, "move.wav"))

        # add widgets
        self.board = Board(self)
        self.black_player = Player("StockFish 8", self)
        self.manual = Manual(self)
        self.manual_bar = ManualBar(self)
        self.black_clock = Clock(self)
        self.white_player = Player("Spike 1.4", self)
        self.white_clock = Clock(self)
        self.game_over = GameOver(self)
        self.engine_management = EngineManagement(self)

        # setup color
        self.window_color = QPalette()
        self.window_color.setColor(
            QPalette.ColorRole.Window, convert_color(config["window_color"])
        )
        self.setPalette(self.window_color)

        self.black_clock.set_color(
            convert_color(self.current_board_style["clock"]),
            convert_color(config["window_color"]),
        )
        self.white_clock.set_color(
            convert_color(self.current_board_style["clock"]),
            convert_color(config["window_color"]),
        )

        # game and thread
        self.ch = Chess()
        self.chess = None
        self.clock = None
        self.game_thread = None
        self.ClockThread = None
        self.move_history = []
        self.is_first_move_taken = None
        self.last_move_ts = None
        self.is_manual_bar_activated = False
        self.move_to_display = 0
        # draw widgets
        self.draw_menu()
        self.draw()

    def cal_basic_size(self, is_initial=True):
        if is_initial:
            screen = QGuiApplication.primaryScreen().geometry()
            width = screen.width()
            self.basic_size = width // 25
            self.std_size = width // 25
        else:
            width = self.geometry().width()
            height = self.geometry().height()
            self.basic_size = min(
                (height - self.spacing["top"] - self.spacing["shaft"] * 2) // 8,
                width // 14,
            )
        self.zoom_ratio = self.basic_size / self.std_size
        self.spacing["hori"] = self.basic_size // 3

    def load_piece_images(self):
        # load the picture of each piece from disk

        for symbol in "rnbqkp":
            img_path = os.path.join(
                piece_image_dir, self.current_piece_style, "b{}.svg".format(symbol)
            )
            self.piece_image[symbol] = QPixmap(img_path)

        for symbol in "RNBQKP":
            img_path = os.path.join(
                piece_image_dir, self.current_piece_style, "w{}.svg".format(symbol)
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

        # append "Options" menu
        OptionsMenu = menuBar.addMenu("Options")

        # "Engine" submenu
        engineMenu = OptionsMenu.addMenu("Engine")
        manageAct = QAction(QIcon(""), "manage", self)
        manageAct.triggered.connect(self.menu_manage_engine)
        engineMenu.addAction(manageAct)

        # "board style" submenu
        boardStyleMenu = OptionsMenu.addMenu("Board Style")

        for style in self.board_styles.keys():
            styleAct = QAction(QIcon(""), style, self)
            styleAct.triggered.connect(
                lambda: self.menu_alter_current_board_style(self.sender().text())
            )
            boardStyleMenu.addAction(styleAct)

        # "piece style" submenu
        pieceStyleMenu = OptionsMenu.addMenu("Pieces Style")

        for style in self.piece_styles:
            styleAct = QAction(QIcon(""), style, self)
            styleAct.triggered.connect(
                lambda: self.menu_alter_current_piece_style(self.sender().text())
            )
            pieceStyleMenu.addAction(styleAct)

        # "sound" submenu
        soundMenu = OptionsMenu.addMenu("Sound")

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

    def menu_manage_engine(self):
        self.engine_management.show()

    def menu_alter_current_piece_style(self, style):
        self.current_piece_style = style
        self.load_piece_images()
        self.board.display()

    def menu_alter_current_board_style(self, style):
        self.current_board_style = self.board_styles[style]
        self.black_clock.set_color(
            convert_color(self.current_board_style["clock"]),
            convert_color(config["window_color"]),
        )
        self.white_clock.set_color(
            convert_color(self.current_board_style["clock"]),
            convert_color(config["window_color"]),
        )

        self.board.initUI()

    def menu_create_game(self, mode):
        self.manual.reset()
        if mode == "standard":
            fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
            ok = True
        elif mode == "from FEN...":
            fen, ok = QInputDialog.getText(self, "FEN", "Input fen:")

        if ok and fen:
            # close a running game if it exists
            if self.game_thread:
                self.game_thread.terminate()
            if self.clock_thread:
                self.clock_thread.terminate()

            # initialize game resources
            self.game_thread = GameThread(self.game_signal, fen)
            self.game_thread.signal.connect(self.extract_packet)
            self.is_first_move_taken = False
            self.clock = {"event": "clock", "w": 15, "b": 15, "step": 1, "turn": "w"}
            self.display_clock()
            self.white_player.reset(config["installed"][config["engine_1"]]["tag"])
            self.black_player.reset(config["installed"][config["engine_2"]]["tag"])
            self.game_thread.start()

    def menu_keep_silent(self):
        if self.is_silent:
            self.is_silent = False
        else:
            self.is_silent = True

    def draw(self):

        self.board.setGeometry(
            self.spacing["hori"],
            self.spacing["top"],
            self.basic_size * 8,
            self.basic_size * 8,
        )

        self.board.zoom()

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
            self.basic_size * 5,
            self.basic_size,
        )

        self.white_player.setGeometry(
            self.spacing["hori"] * 2 + self.basic_size * 8,
            self.spacing["top"] + self.basic_size * 6,
            self.basic_size * 5,
            self.basic_size,
        )
        self.white_clock.setGeometry(
            self.spacing["hori"] * 2 + self.basic_size * 8,
            self.spacing["top"] + self.basic_size * 7,
            self.basic_size * 2,
            self.basic_size,
        )

        self.manual_bar.setGeometry(
            self.spacing["hori"] * 2 + self.basic_size * 8,
            self.spacing["top"] + int(self.basic_size * 2),
            self.basic_size * 5,
            int(self.basic_size * 0.5),
        )

        self.manual.setGeometry(
            self.spacing["hori"] * 2 + self.basic_size * 8,
            self.spacing["top"] + int(self.basic_size * 2.5),
            self.basic_size * 5,
            int(self.basic_size * 3.5),
        )

        self.manual.zoom()

    def extract_packet(self, signal):

        packet = json.loads(signal)

        if packet["event"] == "game":
            move, chess = packet["move"], packet["chess"]
            self.chess = chess
            self.move_history.append([move, chess])

            if not self.is_manual_bar_activated:
                self.board.display()
                self.move_to_display = len(self.move_history) - 1

            if move:

                if self.is_first_move_taken:
                    used_time = timer() - self.last_move_ts
                    self.last_move_ts = timer()
                    self.clock[self.clock["turn"]] -= used_time
                else:
                    self.is_first_move_taken = True
                    self.last_move_ts = timer()

                ts = timer()
                self.clock["turn"] = chess["turn"]
                if self.clock_thread:
                    self.clock_thread.terminate()
                self.clock_thread = ClockThread(self.clock)
                self.clock_thread.signal.connect(self.extract_packet)
                self.clock_thread.start()

                # refresh manual area
                turn, full = chess["turn"], int(chess["full"])
                self.manual.append_move(move, turn, full)

        elif packet["event"] == "clock":
            self.last_move_ts = timer()
            self.clock = packet
            self.display_clock()

        elif packet["event"] == "game_over":
            if self.clock_thread:
                self.clock_thread.terminate()
            self.game_thread.terminate()
            self.game_over.append_result(packet)
            self.manual.append_result(packet)

    def display_clock(self):
        w_clock, b_clock, turn = self.clock["w"], self.clock["b"], self.clock["turn"]
        self.white_clock.display(w_clock)
        self.black_clock.display(b_clock)

        if turn == "w":
            self.white_clock.timing()
            self.black_clock.stop()
        elif turn == "b":
            self.black_clock.timing()
            self.white_clock.stop()

    def resizeEvent(self, *args, **kwargs):
        self.cal_basic_size(is_initial=False)
        self.draw()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    hera = Hera()
    hera.show()
    sys.exit(app.exec())
