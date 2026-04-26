import pygame
import os

from config import tile_size

class Tile(pygame.sprite.Sprite):
    def __init__(self, rect_x, rect_y, image):
        super().__init__()
        self.image = image
        self.rect = image.get_rect()
        self.rect.x = rect_x #builtin attribute (.x)
        self.rect.y = rect_y #same here
        
    # def draw(self, screen): #puts tile on the screen
    #     screen.blit(self.image, self.rect)
        

class Falling_Block(Tile):
    def __init__(self, rect_x, rect_y, image, fall_speed):
        super().__init__(rect_x, rect_y, image)
        self.fall_speed = fall_speed
        self.falling = False
        self.trigger_range = 50 #how many pixels away the trigger
        self.start_y = rect_y
        
    def update(self, player):
        if abs(player.rect.centerx - self.rect.centerx) <= self.trigger_range:
            self.falling = True

        if self.falling:
            self.rect.y += self.fall_speed


class Spike(pygame.sprite.Sprite):
    def __init__(self, rect_x, rect_y, image):
        super().__init__()
        self.image = image
        
        self.rect = pygame.Rect(rect_x, rect_y + (40 - 7), 40, 7)
    
    def update(self, player):
        self.check_player_hit(player)
        
    def check_player_hit(self, player):
        if self.rect.colliderect(player.rect):
            player.dead = True

class Door(pygame.sprite.Sprite):
    def __init__(self, rect_x, rect_y):
        super().__init__()
        self.image = pygame.transform.scale(pygame.image.load(os.path.join("image_s", "door.png")), (tile_size, 36))
        
        self.rect = self.image.get_rect()
        self.rect.x = rect_x
        self.rect.y = rect_y - (self.rect.height - tile_size)
        self.active = True
        self.enter_range = 10 #how close the player and door
    
    def update(self, player, door_with_player):
        if not self.active:
            return
        
        distance_x = abs(player.rect.centerx - self.rect.centerx)
        distance_y = abs(player.rect.centery - self.rect.centery)
        if distance_x <= self.enter_range and distance_y  <= self.enter_range and player.rect.bottom <= self.rect.bottom:
            self.active = False
            player.alpha = 0
            door_with_player.activate(self.rect.x, self.rect.y)
    
    def draw(self, surface):
        if self.active:
            surface.blit(self.image, self.rect)


class DoorWithPlayer():
    def __init__(self):
        
        self.image = pygame.transform.scale(pygame.image.load(os.path.join("image_s", "door_player.png")), (tile_size,  36))
        
        self.rect = self.image.get_rect()
        
        self.active = False
        self.sinking = False
        
        self.sink_speed = 0.8
        self.sink_target = 0
        
        self.done = False
    
    def activate(self, rect_x, rect_y):
        #positon
        self.rect.x = rect_x
        self.rect.y = rect_y
        
        self.active = True
        self.sinking = True
        
        self.sink_target = self.rect.y + self.rect.height
        
        self.done = False
    
    def update(self):
        if not self.active:
            return
        if self.sinking:
            self.rect.y += self.sink_speed
            if self.rect.y >= self.sink_target:
                self.rect.y = self.sink_target
                self.sinking = False
                self.done = True
    
    def draw(self, surface):
        if self.active:
            surface.blit(self.image, self.rect)
    
    def reset(self):
        self.active = False
        self.sinking = False
        self.done = False
        
        