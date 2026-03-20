from level_structure import LevelStructure, GameState
from renderer import View
class Game:
    def __init__(self,level_w,level_h,board):
        ##init a map
        self.level = LevelStructure(level_w,level_h)
        self.level.parse(board,level_w,level_h)

        self.game_state = GameState(self.level)
        self.view = View()
        self.undo_stack = []
    def move(self,dx,dy):
        x,y = self.game_state.player_x,self.game_state.player_y
        new_x,new_y = x+dx,y+dy
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
        self.game_state.player_x = new_x
        self.game_state.player_y = new_y


    def update(self):
        pass
        #print after updating
if __name__ == "__main__":
    test_map = [
        "  ##### ",
        "###   # ",
        "#.@$  # ",
        "### * # ",
        "#..*$ # ",
        "#  @  # ",
        "####### "
    ]
    game = Game(level_w=len(test_map[0]), level_h=len(test_map),board=test_map)
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
