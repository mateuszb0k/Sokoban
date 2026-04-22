import copy
from level_structure import LevelStructure, GameState,LevelGenerator
from renderer import View
from solver import GameSolver
from config_manager import ConfigManager
import random
'''
Game Class handling the logic 
'''
class Game:
    def __init__(self,level_w,level_h,board):
        ##init a map
        self.level = LevelStructure(level_w,level_h)
        self.level.parse(board,level_w,level_h)
        self.moves_count = 0
        self.pushes_count = 0
        self.game_state = GameState(self.level)
        self.bot = EnemyAI(self)
        self.view = View()
        self.undo_stack = []
        self.redo_stack = []
    def move(self,dx,dy,player_id = "local"):
        x,y = self.game_state.players[player_id]
        new_x,new_y = x+dx,y+dy
        old_boxes = self.game_state.box_position.copy()
        old_moves = self.moves_count
        old_pushes = self.pushes_count
        if self.level.wall_array[new_y][new_x]:
            return
        ##if box
        elif (new_x,new_y) in self.game_state.box_position:##smaller game state class
            box_x,box_y = new_x+dx,new_y+dy
            if self.level.wall_array[box_y][box_x]:
                return
            elif (box_x,box_y) in self.game_state.box_position:
                return
            else:
                self.game_state.box_position.append((box_x,box_y))
                # self.undo_stack.append((box_x,box_y))
                self.game_state.box_position.remove((new_x,new_y))
                self.pushes_count += 1
        players_copy = self.game_state.players.copy()
        current_state = (players_copy,old_boxes,old_pushes,old_moves)
        self.undo_stack.append(current_state)
        self.game_state.players[player_id] = [new_x,new_y]
        self.moves_count += 1
        self.bot.make_move()
        self.redo_stack = []
    def undo(self):
        if self.undo_stack:
            popped = self.undo_stack.pop()
            players_copy = self.game_state.players.copy()
            current_state = (players_copy, self.game_state.box_position.copy(),self.pushes_count,self.moves_count)
            self.redo_stack.append(current_state)
            self.game_state.players = popped[0]
            self.game_state.box_position = popped[1]
            self.pushes_count = popped[2]
            self.moves_count = popped[3]
        else:
            return
    def redo(self):
        if self.redo_stack:
            popped = self.redo_stack.pop()
            players_copy = self.game_state.players.copy()
            current_state = (players_copy, self.game_state.box_position.copy(),self.pushes_count,self.moves_count)
            self.undo_stack.append(current_state)
            self.game_state.players = popped[0]
            self.game_state.box_position = popped[1]
            self.pushes_count = popped[2]
            self.moves_count = popped[3]
        else:
            return
    def check_win(self):
        for x,y in self.game_state.box_position:
           if not self.level.target_array[y][x]:
               return False
        return True
    def reset(self):
        self.game_state = GameState(self.level)
        self.undo_stack = []
        self.redo_stack = []
        self.moves_count = 0
        self.pushes_count = 0
    def check_deadlock(self):
        for x,y in self.game_state.box_position:
            if not self.level.target_array[y][x]:
                wall_up = self.level.wall_array[y-1][x]
                wall_down = self.level.wall_array[y+1][x]
                wall_left = self.level.wall_array[y][x-1]
                wall_right = self.level.wall_array[y][x+1]
                if wall_up and wall_left:
                    return True
                if wall_up and wall_right:
                    return True
                if wall_down and wall_left:
                    return True
                if wall_down and wall_right:
                    return True
        return False
class EnemyAI():
    def __init__(self,game:Game):
        self.config = ConfigManager()
        self.game = game
        self.solver = GameSolver(self.game.level,self.game.game_state)
        self.id = "bot"
        self.x,self.y = self.find_spawn_point()
        self.game.game_state.players[self.id] = (self.x,self.y)
        self.max_pushes = self.config.max_pushes
        self.range = self.config.range
        self.current_pushes = 0
    def find_spawn_point(self):
        for y in range(self.game.level.height):
            for x in range(self.game.level.width):
                if not self.game.level.wall_array[y][x] and not self.game.level.target_array[y][x] and (x,y) not in self.game.game_state.box_position and (x,y) not in self.game.game_state.players.values():
                    return x,y
        return -1,-1
    def get_distance(self,x,y):
        player_x,player_y = self.game.game_state.players['local']
        return abs(player_x-x)+abs(player_y-y)
    def get_valid_moves(self):
        directions = [(0, 1), (0, -1), (-1, 0), (1, 0)]
        valid_moves = []
        for dir in directions:
            new_x,new_y = self.x+dir[0],self.y+dir[1]
            if not self.game.level.wall_array[new_y][new_x] and (new_x,new_y) not in self.game.game_state.players.values():
                if (new_x,new_y) not in self.game.game_state.box_position:
                    valid_moves.append((new_x,new_y,'MOVE'))
                else:
                    if self.current_pushes<self.max_pushes:
                        b_x,b_y = new_x+dir[0],new_y+dir[1]
                        if not self.game.level.wall_array[b_y][b_x] and (b_x,b_y) not in self.game.game_state.box_position and (b_x,b_y) not in self.game.game_state.players.values():
                            box_pos_copy = self.game.game_state.box_position.copy()
                            box_pos_copy.remove((new_x,new_y))
                            box_pos_copy.append((b_x,b_y))
                            if self.solver.check_freeze_deadlock(bx=b_x,by=b_y,current_boxes=box_pos_copy):
                                continue
                            else:
                                if self.game.level.target_array[b_y+dir[1]][b_x+dir[0]]:
                                    continue
                                else:
                                    valid_moves.append((new_x,new_y,'PUSH'))
                    else:
                        continue
        return valid_moves
    def make_move(self):
        distance = self.get_distance(self.x,self.y)
        valid_moves = self.get_valid_moves()
        move = None
        #bot normal moves
        state = 'PATROL'
        if distance<=self.range:
            state = 'FLEE'
        #bot sabotages
        elif distance>self.range and self.current_pushes<self.max_pushes:
            state = 'SABOTEUR'
        else:
            state = 'PATROL'
        if valid_moves:
            if state == 'PATROL':
                move = random.choice(valid_moves)
            elif state == 'SABOTEUR':
                move = random.choice(valid_moves)
                for m in valid_moves:
                    if m[-1] == 'PUSH':
                        move = m
                        break
            elif state == 'FLEE':
                max_d = -1
                best_move= None
                for m in valid_moves:
                    dist = self.get_distance(m[0],m[1])
                    if dist>max_d:
                        max_d = dist
                        best_move = m
                    # if m[-1] == 'PUSH':
                    #     best_move=m
                move = best_move
            if move[-1] == 'PUSH':
                dx,dy = move[0]-self.x,move[1]-self.y
                self.game.game_state.box_position.remove((move[0],move[1]))
                self.game.game_state.box_position.append((move[0]+dx,move[1]+dy))
                self.current_pushes += 1
            self.x = move[0]
            self.y = move[1]
            self.game.game_state.players[self.id] = (self.x,self.y)







if __name__ == "__main__":
    test_map = LevelGenerator(10,7,3)
    game = Game(level_w=len(test_map.level[0]), level_h=len(test_map.level),board=test_map.level)

    hint_cnt=0
    while True:
        game.view.draw_board(game.level,game.game_state)
        for row in game.view.board:
            print(row)
        move = input().lower()
        if move == 'q':
            break
        elif move == 'w':
            game.move(dx=0,dy=-1)
        elif move == 's':
            game.move(dx=0,dy=1)
        elif move == 'a':
            game.move(dx=-1,dy=0)
        elif move == 'd':
            game.move(dx=1,dy=0)
        elif move == 'z':
            game.undo()
        elif move == 'x':
            game.redo()
        elif move == 'r':
            game.reset()
        elif move == 'h': #hint
            solution = GameSolver(game.level, game.game_state).solve()
            print(f"Hint: {solution[0]}" if solution else "There are no solutions")

        is_game_over = game.check_win()
        is_deadlock = game.check_deadlock()
        if is_deadlock:
            print("Game over deadlock press r to reset")
        if is_game_over:
            print("GAME OVER")
            break
