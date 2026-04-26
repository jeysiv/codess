import pygame
import os

from obstacles import Tile, Falling_Block, Spike, Door, DoorWithPlayer
from config import tile_size

class World():
    def __init__(self, data):
        self.data = data
        
        self.door_with_player = DoorWithPlayer()
        
        self.platforms = pygame.sprite.Group()
        self.falling_blocks = pygame.sprite.Group()
        self.spikes = pygame.sprite.Group()
        self.door = pygame.sprite.Group()

        tile_surface = pygame.Surface((tile_size, tile_size))
        tile_surface.fill("#003a49")
        
        tile_surfs =  pygame.Surface((tile_size, tile_size))
        tile_surfs.fill("#003a49")
        
        tile_spike = pygame.transform.scale(pygame.image.load(os.path.join("image_s", "spike_static.png")), (40, 7))
        
        # tile_door = pygame.transform.scale(pygame.image.load(os.path.join("image_s", "door.png")), (32, 38))

        for row_index, row in enumerate(data): #Loops through every cell in your 2D grid.
            for column_index, tile_type in enumerate(row): #Converts the grid position into pixel coordinates — e.g. column 3 = 3×50 = 150px from the left.
                    
                    rect_x = column_index * tile_size
                    rect_y = row_index * tile_size
                    
                    if tile_type == 1: #Tile
                        self.platforms.add(Tile(rect_x, rect_y, tile_surface))
                        
                    elif tile_type == 2: #Fallingblock
                        self.falling_blocks.add(Falling_Block(rect_x, rect_y, tile_surface, 50))  
                         
                    elif tile_type == 3: #Spike
                        self.spikes.add(Spike(rect_x, rect_y, tile_spike))
                    
                    elif tile_type == 4: #Door
                        self.door.add(Door(rect_x, rect_y))
                    
                        

    
    # def draw(self): #Loops through every tile and draws it onto the screen.
    #     for tile in self.tile_list:
    #         tile.draw(screen)
    
    def draw(self, screen):
        self.falling_blocks.draw(screen)
        self.spikes.draw(screen)
        self.door_with_player.draw(screen)
        self.platforms.draw(screen)
        for door in self.door:
            door.draw(screen)
        
        
    
    def update(self, player):
        self.falling_blocks.update(player)
        self.spikes.update(player)
        for door in self.door:
            door.update(player, self.door_with_player)
        self.door_with_player.update()
        
        if self.door_with_player.done:
            return "FINISHED"
    
    def reset(self):
        for block in self.falling_blocks:
            block.rect.y = block.start_y
            block.falling = False
        
        for door in self.door:
            door.active = True
        self.door_with_player.reset()
