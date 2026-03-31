from PyQt6.QtGui import QPixmap, QBrush, QColor
from PyQt6.QtWidgets import QGraphicsPixmapItem
class EntityFactory:
    def __init__(self,textures,tile_size):
        self.textures = textures
        self.tile_size = tile_size
    def create_sprite(self,entity_type,grid_x,grid_y):
        true_x = self.tile_size*grid_x
        true_y = self.tile_size*grid_y
        sprite = QGraphicsPixmapItem(self.textures[entity_type])
        sprite.setPos(true_x,true_y)
        return sprite
