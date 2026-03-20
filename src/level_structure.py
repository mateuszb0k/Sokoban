
"""
ARRAY FOR PLAYER POSITION X,Y
TWO BOOLEAN 2D ARRAYS FOR WALL AND TARGET POSITIONS
INITIAL BOX ARRAY ALSO IMPLEMENTED AS A STACK [[x0,y0],....[xn,yn]]
"""
class LevelStructure():
    def __init__(self,level_w,level_h):
        self.player_x = 0
        self.player_y = 0
        self.box_position = []
        self.wall_array = []
        self.target_array = []
        self.width = level_w
        self.height = level_h
    def parse(self,level,level_w,level_h):
        self.wall_array = []
        for y in range(level_h):
            wall_row = [False] * level_w
            target_row = [False]* level_w
            for x in range(level_w):
                if level[y][x] == '#':
                    wall_row[x]=(True)
                if level[y][x] == '@':
                    self.player_x = x
                    self.player_y = y
                if level[y][x] == '$':
                    self.box_position.append((x,y))
                if level[y][x] == '.':
                    target_row[x]=(True)
                if level[y][x] == '*':
                    target_row[x]=(True)
                    self.box_position.append((x,y))
                if level[y][x] == '+':
                    target_row[x]=(True)
                    self.player_x = x
                    self.player_y = y
            self.wall_array.append(wall_row)
            self.target_array.append(target_row)
class GameState():
    def __init__(self,level: LevelStructure):
        self.box_position = level.box_position.copy()
        self.player_x = level.player_x
        self.player_y = level.player_y


