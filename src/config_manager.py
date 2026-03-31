import json
import os
class ConfigManager:
    def __init__(self,config_path='../config.json'):
        self.path = config_path
        self.tile_size = 64
        self.width = 5
        self.height = 5
        self.boxes = 2
        self.max_iters = 10000
        self.startup_map = ''
        self.load_config()
    def load_config(self):
        try:
            if os.path.exists(self.path):
                with open(self.path,'r') as f:
                    config = json.load(f)
                w_val = config.get('default_width',self.width)
                if isinstance(w_val,int) and w_val>0:
                    self.width = w_val
                t_val = config.get('tile_size',self.tile_size)
                if isinstance(t_val,int) and t_val>0:
                    self.tile_size = t_val
                h_val = config.get('default_height',self.height)
                if isinstance(h_val,int) and h_val>0:
                    self.height = h_val
                b_val = config.get('default_boxes',self.boxes)
                if isinstance(b_val,int) and b_val>0:
                    self.boxes = b_val
                iters = config.get('solver_max_iterations',self.max_iters)
                if isinstance(iters,int) and iters>0:
                    self.max_iters = iters
                map = config.get('map',self.startup_map)
                if isinstance(map,str) and map !='':
                    self.startup_map = map

        except Exception as e:
            print(e,"Using default config")

if __name__ == '__main__':
    config = ConfigManager()
    print(config.tile_size)
    print(config.width)
    print(config.height)
