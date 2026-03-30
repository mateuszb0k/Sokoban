import copy
from level_structure import LevelStructure, GameState,LevelGenerator
from renderer import View
from solver import GameSolver
class Game:
    def __init__(self,level_w,level_h,board):
        ##init a map
        self.level = LevelStructure(level_w,level_h)
        self.level.parse(board,level_w,level_h)
        self.moves_count = 0
        self.pushes_count = 0
        self.game_state = GameState(self.level)
        self.view = View()
        self.undo_stack = []
        self.redo_stack = []
    def move(self,dx,dy):
        x,y = self.game_state.player_x,self.game_state.player_y
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
        current_state = (x,y,old_boxes,old_pushes,old_moves)
        self.undo_stack.append(current_state)
        self.game_state.player_x = new_x
        self.game_state.player_y = new_y
        self.moves_count += 1
        self.redo_stack = []
    def undo(self):
        if self.undo_stack:
            popped = self.undo_stack.pop()
            current_state = (self.game_state.player_x, self.game_state.player_y, self.game_state.box_position.copy(),self.pushes_count,self.moves_count)
            self.redo_stack.append(current_state)
            self.game_state.player_x = popped[0]
            self.game_state.player_y = popped[1]
            self.game_state.box_position = popped[2]
            self.pushes_count = popped[3]
            self.moves_count = popped[4]
        else:
            return
    def redo(self):
        if self.redo_stack:
            popped = self.redo_stack.pop()
            current_state = (self.game_state.player_x, self.game_state.player_y, self.game_state.box_position.copy(),self.pushes_count,self.moves_count)
            self.undo_stack.append(current_state)
            self.game_state.player_x = popped[0]
            self.game_state.player_y = popped[1]
            self.game_state.box_position = popped[2]
            self.pushes_count = popped[3]
            self.moves_count = popped[4]
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
