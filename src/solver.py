from level_structure import LevelStructure,GameState
import heapq
from collections import deque,defaultdict
from config_manager import ConfigManager
'''
A* solver with added optimizations to improve solution time
'''
class GameSolver:
    def __init__(self,level: LevelStructure,game_state: GameState):
        self.level = level
        self.config = ConfigManager()
        self.max_iters = self.config.max_iters
        self.game_state = game_state
        self.alive_squares = self.build_alive_squares()
    def manhattan_distance(self,a,b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])
    def get_heuristic(self,game: GameState):
        total = 0
        targets = sorted(self.level.target_positions.copy())
        sorted_boxes = sorted(game.box_position)
        for x,y in sorted_boxes:
            min_d = float('inf')
            best_target = None
            for t_x,t_y in targets:
                dist = self.manhattan_distance((x,y),(t_x,t_y))
                if dist<min_d:
                    min_d = dist
                    best_target = (t_x,t_y)
            total+=min_d
            targets.remove(best_target)
        return total
    def get_state_tuple(self,game: GameState):
        sorted_boxes = tuple(sorted(game.box_position))
        can_x,can_y = self.get_position(game.player_x,game.player_y,sorted_boxes)
        return (can_x, can_y, sorted_boxes)
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
        directions = [((0, 1), 's'), ((0, -1), 'w'), ((-1, 0), 'a'), ((1, 0), 'd')]
        reachable = self.get_reachable_spaces(game.player_x,game.player_y,game.box_position)
        for box_x,box_y in game.box_position:
            for direction,key in directions:
                n_box_x,n_box_y = box_x+direction[0], box_y+direction[1]
                player_x,player_y = box_x-direction[0], box_y-direction[1]
                if (player_x,player_y) not in reachable:
                    continue
                if self.level.wall_array[n_box_y][n_box_x] or (n_box_x, n_box_y) in game.box_position:
                    continue
                if (n_box_x, n_box_y) not in self.alive_squares:
                    continue
                new_game = GameState(self.level)
                new_game.box_position = game.box_position.copy()
                new_game.box_position.remove((box_x,box_y))
                new_game.box_position.append((n_box_x,n_box_y))
                new_game.player_x = box_x
                new_game.player_y = box_y
                if self.check_freeze_deadlock(n_box_x,n_box_y,new_game.box_position):
                    continue
                steps = reachable[(player_x,player_y)]+[key]
                neighbors.append((new_game,steps))
        return neighbors
    def solve(self):
        counter = 0
        visited = set()
        queue = []
        h = self.get_heuristic(self.game_state)
        solution = []
        iters = 0
        '''
        push that way so if h values are equal we get the lowest counter
        '''
        heapq.heappush(queue,(h,counter,self.game_state,solution))
        while queue and iters<self.max_iters:
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
                            moves = sol + move
                            new_prio = len(moves)+self.get_heuristic(new_state)
                            counter +=1
                            heapq.heappush(queue,(new_prio,counter,new_state,moves))
            iters+=1
        return None
    def get_reachable_spaces(self,player_x,player_y,current_boxes):
        reachable = defaultdict(list)
        visited = set()
        visited.add((player_x,player_y))
        queue = deque()
        queue.append((player_x,player_y,[]))
        directions = [((0, 1), 's'), ((0, -1), 'w'), ((-1, 0), 'a'), ((1, 0), 'd')]
        while queue:
            position = queue.popleft()
            reachable[(position[0],position[1])] = position[2]
            for direction,key in directions:
                n_player_x,n_player_y = position[0]+direction[0],position[1]+direction[1]
                if (n_player_x,n_player_y) in visited:
                    continue
                if self.level.wall_array[n_player_y][n_player_x]:
                    continue
                if (n_player_x,n_player_y) in current_boxes:
                    continue
                new_path = position[2]+[key]
                visited.add((n_player_x,n_player_y))
                queue.append((n_player_x,n_player_y,new_path))
        return reachable
    def build_alive_squares(self):
        queue = deque()
        alive_squares = set()
        for x,y in self.level.target_positions:
            queue.append((x,y))
            alive_squares.add((x,y))
        while queue:
            x,y = queue.popleft()
            directions = [(0,1),(0,-1),(-1,0),(1,0)]
            for dir in directions:
                nx,ny  = x+dir[0],y+dir[1]
                if 0 <= nx < self.level.width and 0 <= ny < self.level.height:
                    if (nx,ny) in alive_squares:
                        continue
                    if self.level.wall_array[ny][nx]:
                        continue
                    px,py = nx+dir[0],ny+dir[1]
                    if not (0 <= px < self.level.width and 0 <= py < self.level.height):
                        continue
                    if self.level.wall_array[py][px]:
                            continue
                    alive_squares.add((nx,ny))
                    queue.append((nx,ny))
        return alive_squares
    def get_position(self,player_x,player_y,current_boxes):
        visited = set()
        visited.add((player_x,player_y))
        queue = deque()
        queue.append((player_x,player_y))
        directions = [(0, 1), (0, -1), (-1, 0), (1, 0)]
        while queue:
            pos = queue.popleft()
            for dir in directions:
                nx,ny = pos[0]+dir[0],pos[1]+dir[1]
                if (nx,ny) in visited:
                    continue
                if self.level.wall_array[ny][nx]:
                    continue
                if (nx,ny) in current_boxes:
                    continue
                visited.add((nx,ny))
                queue.append((nx,ny))
        return min(visited)
    def check_freeze_deadlock(self,bx,by,current_boxes):
        quadrants = [
            [(0, 0), (1, 0), (0, 1), (1, 1)],
            [(0, 0), (-1, 0), (0, 1), (-1, 1)],
            [(0, 0), (1, 0), (0, -1), (1, -1)],
            [(0, 0), (-1, 0), (0, -1), (-1, -1)]
        ]
        for quad in quadrants:
            is_deadlocked = True
            for dx,dy in quad:
                nx,ny = dx+bx,dy+by
                if not (self.level.wall_array[ny][nx] or (nx, ny) in current_boxes):
                    is_deadlocked = False
                    break
            if is_deadlocked:
                return True
        return False




