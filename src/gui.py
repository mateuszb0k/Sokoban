from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget,
    QLabel,QMessageBox,QFileDialog,
    QVBoxLayout, QPushButton, QHBoxLayout, QGraphicsView, QGraphicsScene,QGraphicsPixmapItem,QGraphicsRectItem,QGraphicsTextItem
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap, QBrush, QColor,QFont
from engine import Game
import sys
from level_structure import LevelGenerator, GameState, LevelStructure
from solver import GameSolver
from config_manager import ConfigManager
from factory import EntityFactory
from network import Network
import random
import threading
'''
Simple PyQt visualisation
'''
class MainWindow(QMainWindow):
    def __init__(self,game_state:Game):
        super().__init__()
        self.config = ConfigManager()
        self.tile_size = self.config.tile_size
        self.textures = {
            'wall' : QPixmap('../assets/wall.png').scaled(self.tile_size, self.tile_size),
            'floor' : QPixmap('../assets/floor_tile.png').scaled(self.tile_size, self.tile_size),
            'box' : QPixmap('../assets/box.png').scaled(self.tile_size, self.tile_size),
            'player0' : QPixmap('../assets/player_model.png').scaled(self.tile_size, self.tile_size),
            'player1' : QPixmap('../assets/player_model_1.png').scaled(self.tile_size, self.tile_size),
            'player2' : QPixmap('../assets/player_model_2.png').scaled(self.tile_size, self.tile_size),
            'player3' : QPixmap('../assets/player_model_3.png').scaled(self.tile_size, self.tile_size),
            'bot' : QPixmap('../assets/bot_model.png').scaled(self.tile_size, self.tile_size),
            'target' : QPixmap('../assets/target.png').scaled(self.tile_size, self.tile_size),
            'box_on_target' : QPixmap('../assets/box_on_target.png').scaled(self.tile_size, self.tile_size)
        }
        self.font =QFont('Futura',self.tile_size//3)
        self.player_id = f"Player{random.randint(0,100)}"
        self.factory = EntityFactory(self.textures,self.tile_size)
        self.game = game_state
        self.network = Network()
        self.network.signal.connect(self.handle_network_update)
        self.network.start()
        self.setWindowTitle("Sokoban")
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout  = QHBoxLayout()
        self.scene = QGraphicsScene()
        self.graphics = QGraphicsView()
        self.graphics.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.graphics.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.graphics.setScene(self.scene)
        layout.addWidget(self.graphics)
        layout1 = QVBoxLayout()

        self.steps = QLabel("Steps: 0")
        self.box_pushes = QLabel("Pushes: 0")
        # self.undo_button = QPushButton("Undo")
        self.load_file = QPushButton("Load File")
        self.load_file.clicked.connect(self.choose_file)
        # self.redo_button = QPushButton("Redo")
        # self.reset_button = QPushButton("Reset")
        # self.hint_button = QPushButton("Hint")
        layout1.addWidget(self.steps)
        layout1.addWidget(self.box_pushes)
        # layout1.addWidget(self.undo_button)
        # layout1.addWidget(self.redo_button)
        # layout1.addWidget(self.reset_button)
        # layout1.addWidget(self.hint_button)
        layout1.addWidget(self.load_file)
        layout1.addStretch()
        layout.addLayout(layout1)
        central_widget.setLayout(layout)

        self.block_to_highlight = None

        self.updateUI()
    def handle_network_update(self,data):
        player_id = data.get('player_id','remote')
        self.game.game_state.players[player_id] = (data.get('x',0),data.get('y',0))
        self.game.game_state.box_position = [tuple(position) for position in data.get('box_position',self.game.level.box_position)]
        self.updateUI()

    def updateUI(self):
        self.scene.clear()
        steps = self.game.moves_count
        pushes = self.game.pushes_count
        self.steps.setText(f"Steps: {steps}")
        self.box_pushes.setText(f"Box Pushes: {pushes}")
        for y in range(self.game.level.height):
            for x in range(self.game.level.width):
                self.scene.addItem(self.factory.create_sprite('floor',x,y))
                if self.game.level.target_array[y][x]:
                    self.scene.addItem(self.factory.create_sprite('target',x,y))
                if self.game.level.wall_array[y][x]:
                    self.scene.addItem(self.factory.create_sprite('wall',x,y))
                for id,player in enumerate(self.game.game_state.players.items()):
                    name,position = player
                    if x==position[0] and y==position[1]:
                        if name!="bot":
                            self.scene.addItem(self.factory.create_sprite(f'player{id}',x,y))
                        else:
                            self.scene.addItem(self.factory.create_sprite(f'bot',x,y))
                        if id ==0:
                            text = QGraphicsTextItem("You")
                        else:
                            text = QGraphicsTextItem(name)
                        text.setFont(self.font)
                        text.setDefaultTextColor(QColor(255,255,255))
                        text.setPos(x*self.tile_size,y*self.tile_size-self.tile_size//3-5)
                        self.scene.addItem(text)
                if (x,y) in self.game.game_state.box_position:
                    self.scene.addItem(self.factory.create_sprite('box',x,y))
                    if self.game.level.target_array[y][x]:
                        self.scene.addItem(self.factory.create_sprite('box_on_target',x,y))
                if (x, y) == self.block_to_highlight:
                    item = QGraphicsRectItem(0, 0, self.tile_size, self.tile_size)
                    brush = QBrush(QColor(0, 255, 0, 120))
                    item.setBrush(brush)
                    item.setPos(x * self.tile_size, y * self.tile_size)
                    self.scene.addItem(item)

    def keyPressEvent(self, event):
        move = event.key()
        self.block_to_highlight = None
        if move == Qt.Key.Key_W:
            self.game.move(dx=0, dy=-1)
        elif move == Qt.Key.Key_S:
            self.game.move(dx=0, dy=1)
        elif move == Qt.Key.Key_A:
            self.game.move(dx=-1, dy=0)
        elif move == Qt.Key.Key_D:
            self.game.move(dx=1, dy=0)
        elif move == Qt.Key.Key_Z:
            self.handle_undo()
        elif move == Qt.Key.Key_X:
            self.handle_redo()
        elif move == Qt.Key.Key_R:
            self.game.reset()
        elif move == Qt.Key.Key_C:
            self.handle_hot_reload()
        elif move == Qt.Key.Key_H:  # hint only for the first player
            solution = GameSolver(self.game.level, self.game.game_state).solve()
            x,y = self.game.game_state.players["local"]
            if solution:
                if solution[0] =='w':
                    self.block_to_highlight = (x, y-1)
                elif solution[0] =='s':
                    self.block_to_highlight = (x, y+1)
                elif solution[0] =='a':
                    self.block_to_highlight = (x-1, y)
                elif solution[0] =='d':
                    self.block_to_highlight = (x+1, y)
            else:
                self.block_to_highlight = None
        if self.game.check_win():
            QMessageBox.information(self, "You Won!", "You Won!")
            self.updateUI()
            l = LevelGenerator(self.game.level.width, self.game.level.height,len(self.game.level.box_position))
            self.game = Game(self.game.level.width, self.game.level.height,l.level)
            self.game.reset()
            self.block_to_highlight = None
            self.updateUI()



        elif self.game.check_deadlock():
            QMessageBox.information(self, "Deadlock", "Deadlock, Undo your last move or reset")

        payload = {
            "player_id": self.player_id,
            "x": self.game.game_state.players["local"][0],
            "y": self.game.game_state.players["local"][1],
            "box_position": self.game.game_state.box_position
        }
        self.network.send_data(payload)
        self.updateUI()
    def handle_undo(self):
        self.game.undo()
        self.updateUI()
    def handle_redo(self):
        self.game.redo()
        self.updateUI()
    def choose_file(self):
        dir,_ = QFileDialog.getOpenFileName(caption = "Choose a file")
        list = []
        if dir:
            with open(dir, 'r') as f:
                for line in f:
                    line = line.rstrip('\n')
                    list.append(line)
            h = len(list)
            w = len(list[0])
            self.game = Game(w,h,list)
            self.block_to_highlight = None
            self.updateUI()
        else:
            return
    def handle_hot_reload(self):
        self.config.load_config()
        self.tile_size = self.config.tile_size
        self.textures = {
            'wall' : QPixmap('../assets/wall.png').scaled(self.tile_size, self.tile_size),
            'floor' : QPixmap('../assets/floor_tile.png').scaled(self.tile_size, self.tile_size),
            'box' : QPixmap('../assets/box.png').scaled(self.tile_size, self.tile_size),
            'player' : QPixmap('../assets/player_model.png').scaled(self.tile_size, self.tile_size),
            'target' : QPixmap('../assets/target.png').scaled(self.tile_size, self.tile_size),
            'box_on_target' : QPixmap('../assets/box_on_target.png').scaled(self.tile_size, self.tile_size)
        }
        self.factory = EntityFactory(self.textures,self.tile_size)
        self.updateUI()
if __name__ == "__main__":
    app = QApplication(sys.argv)
    config = ConfigManager()
    x,y,b=config.width,config.height,config.boxes
    board = LevelGenerator(x,y,b)
    game = Game(x,y,board.level)
    # level = []
    # with open('../lvl.txt', 'r') as f:
    #     for line in f:
    #         line = line.rstrip('\n')
    #         level.append(line)
    # h = len(level)
    # w = len(level[0])
    # game = Game(w, h, level)
    window = MainWindow(game)
    window.show()
    sys.exit(app.exec())