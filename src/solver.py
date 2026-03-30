from level_structure import LevelStructure,GameState
import heapq
class GameSolver:
    def __init__(self,level: LevelStructure,game_state: GameState):
        self.level = level
        self.game_state = game_state

    def manhattan_distance(self,a,b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])
    def get_heuristic(self,game: GameState):
        total = 0
        for x,y in game.box_position:
            min_d = float('inf')
            for t_x,t_y in self.level.target_positions:
                dist = self.manhattan_distance((x,y),(t_x,t_y))
                min_d = min(min_d, dist)
            total+=min_d
        return total
    def get_state_tuple(self,game: GameState):
        sorted_boxes = sorted(game.box_position)
        state = (game.player_x,game.player_y,tuple(sorted_boxes))
        return state
    def is_corner(self,position):
            x,y = position
            if not self.level.target_array[y][x]:
                    wall_up = self.level.wall_array[y - 1][x]
                    wall_down = self.level.wall_array[y + 1][x]
                    wall_left = self.level.wall_array[y][x - 1]
                    wall_right = self.level.wall_array[y][x + 1]
                    if wall_up and wall_left:
                        return True
                    if wall_up and wall_right:
                        return True
                    if wall_down and wall_left:
                        return True
                    if wall_down and wall_right:
                        return True
            return False
    def get_neighbors(self,game: GameState):
        neighbors = []
        directions = [((0,1),'s'),((0,-1),'w'),((-1,0),'a'),((1,0),'d')]
        for direction,move in directions:
            new_x,new_y = game.player_x+direction[0],game.player_y+direction[1]
            if self.level.wall_array[new_y][new_x]:
                continue
            elif (new_x,new_y) in game.box_position:
                new_box_x,new_box_y = new_x+direction[0],new_y+direction[1]
                if (new_box_x,new_box_y) in game.box_position:
                    continue
                elif self.level.wall_array[new_box_y][new_box_x]:
                    continue
                elif self.is_corner((new_box_x,new_box_y)):
                    continue

                game_copy = GameState(self.level)
                game_copy.box_position = game.box_position.copy()
                game_copy.player_x,game_copy.player_y = new_x,new_y
                game_copy.box_position.append((new_box_x,new_box_y))
                game_copy.box_position.remove((new_x,new_y))
            else:
                game_copy = GameState(self.level)
                game_copy.box_position = game.box_position.copy()
                game_copy.player_x,game_copy.player_y = new_x,new_y
            neighbors.append((game_copy,move))

        return neighbors
    def solve(self):
        counter = 0
        visited = set()
        queue = []
        h = self.get_heuristic(self.game_state)
        solution = []
        '''
        push that way so if h values are equal we get the lowest counter
        '''
        heapq.heappush(queue,(h,counter,self.game_state,solution))
        while queue:
            prio,cnt,current_state,sol = heapq.heappop(queue)
            current_state_tuple = self.get_state_tuple(current_state)
            if current_state_tuple in visited:
                continue
            else:
                visited.add(current_state_tuple)
                if self.get_heuristic(current_state)==0:
                    return sol
                else:
                    neighbors = self.get_neighbors(current_state)
                    for new_state,move in neighbors:
                        if self.get_state_tuple(new_state) in visited:
                            continue
                        else:
                            moves = sol + [move]
                            new_prio = len(moves)+self.get_heuristic(new_state)
                            counter +=1
                            heapq.heappush(queue,(new_prio,counter,new_state,moves))
        return None






