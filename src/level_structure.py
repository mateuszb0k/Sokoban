import random
import numpy as np
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
        self.target_positions = []
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
                    self.target_positions.append((x,y))
                if level[y][x] == '*':
                    target_row[x]=(True)
                    self.box_position.append((x,y))
                    self.target_positions.append((x,y))
                if level[y][x] == '+':
                    target_row[x]=(True)
                    self.target_positions.append((x,y))
                    self.player_x = x
                    self.player_y = y
            self.wall_array.append(wall_row)
            self.target_array.append(target_row)
    def lvl_from_txt(self,txt):
        board = []
        with open(txt,'r') as f:
            lines = f.readlines()
            for line in lines:
                line = line.rstrip('\n')
                board.append(line)
        x = len(board[0])
        y = len(board)
        level  = LevelStructure(x,y)
        level.parse(board,x,y)
        return level




class GameState():
    def __init__(self,level: LevelStructure):
        self.box_position = level.box_position.copy()
        self.player_x = level.player_x
        self.player_y = level.player_y
class LevelGenerator():
    def __init__(self,dim_x,dim_y,boxes):
        self.level = []
        for y in range(dim_y):
            self.level.append([' ']*dim_x)
        for y in range(dim_y):
            for x in range(dim_x):
                if y ==0 or y ==dim_y-1:
                    self.level[y][x] = '#'
                if x ==0 or x ==dim_x-1:
                    self.level[y][x] = '#'
        num_walls = min(dim_x,dim_y)-min(dim_x,dim_y)//10#arbitrary
        random_walls=0
        while random_walls<num_walls:
            x=random.randint(0,dim_x-1)
            y=random.randint(0,dim_y-1)
            if self.level[y][x]==' ':
                self.level[y][x] = '#'
                random_walls += 1

        p_x = random.randint(1,dim_x-2)
        p_y = random.randint(1,dim_y-2)
        placed =0
        targets =[]
        boxes_arr = []
        while placed<boxes:
            x,y = random.randint(1,dim_x-2),random.randint(1,dim_y-2)
            if (x,y) not in targets and (x,y) != (p_x,p_y) and self.level[y][x]!='#':
                targets.append((x,y))
                boxes_arr.append((x,y))
                placed+=1
        for _ in range(50000):
            directions = [(0,1),(0,-1),(-1,0),(1,0)]
            vector=random.choice(directions)
            n_px = p_x+vector[0]
            n_py = p_y + vector[1]
            if self.level[n_py][n_px] == '#' or (n_px,n_py) in boxes_arr:
                continue
            else:
                box_x = p_x-vector[0]
                box_y = p_y-vector[1]
                if (box_x,box_y) in boxes_arr and (p_x,p_y) not in boxes_arr:
                    if random.choice([True,False]):
                        boxes_arr.remove((box_x, box_y))
                        boxes_arr.append((p_x,p_y))
                        p_x = n_px
                        p_y = n_py
                else:
                    p_x = n_px
                    p_y = n_py
        for tx,ty in targets:
            self.level[ty][tx] = '.'
        for bx,by in boxes_arr:
            if self.level[by][bx] == '.':
                self.level[by][bx] = '*'
            else:
                self.level[by][bx] = '$'
        self.level[p_y][p_x] = '@' if self.level[p_y][p_x]!='.' else '+'

        print(self.level)



