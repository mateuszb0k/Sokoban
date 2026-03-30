from level_structure import LevelStructure, GameState,LevelGenerator
class View:
    def __init__(self):
        self.board = []
    def draw_board(self,level: LevelStructure,game: GameState):
        wall_array = level.wall_array
        target_array = level.target_array
        self.board = []
        for y in range(level.height):
            row = ""
            for x in range(level.width):
                if x==game.player_x and y==game.player_y:
                    if target_array[y][x]:
                        row+='+'
                    else:
                        row+='@'

                elif (x,y) in game.box_position:
                    if target_array[y][x]:
                        row+='*'
                    else:
                        row+='$'
                elif wall_array[y][x]:
                    row += "#"
                elif target_array[y][x]:
                    row+='.'
                else:
                    row+='-'

            self.board.append(row)

if __name__ == '__main__':
    test_map = LevelGenerator(30,10,10)
    level = LevelStructure(level_w=len(test_map.level[0]), level_h=len(test_map.level))
    print(level.height, level.width)
    level.parse(test_map.level, level_w=len(test_map.level[0]), level_h=len(test_map.level))
    game_state = GameState(level)
    view = View()
    view.draw_board(level, game_state)
    for row in view.board:
        print(row)