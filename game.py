import pygame
from pygame.locals import *


from config import screen_width, screen_height
from start_menu import StartMenu
from player import Player
from world import World
from levels import world_data



class Game():
    def __init__(self):
        pygame.init()
        
        self.screen = pygame.display.set_mode((screen_width, screen_height), pygame.FULLSCREEN | pygame.SCALED)
        self.clock = pygame.time.Clock()
        
        self.menu = StartMenu()
        self.state = "menu"
        self.running = True

        # screen = pygame.display.set_mode((screen_width, screen_height)) #, pygame.FULLSCREEN
        pygame.display.set_caption("WHAT")#----> title


        self.player = Player(150, 200) # x, y #starting pos
        self.running = True
        
        

    
    def handles_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                
            if self.state == "menu":
                self.menu.handle_event(event)
                if not self.menu.active and self.state == "menu":
                    self.state = "play"
                    self.world = World(world_data[self.menu.selected_level])
            
            elif self.state == "play":
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE and self.player.VELOCITY_Y == 0:
                        self.player.VELOCITY_Y = -8
                
                    if event.key == pygame.K_RETURN and self.player.dead:
                        self.world.reset()
                        self.player.reset()
                        self.player.dead = False
        
    def update(self):
        # if self.state == "game" and self.world is None:
        #     self.world = World(world_data[self.menu.selected_level])
            
        if self.state == "menu":
            return
        
        elif self.state == "play":
            self.player.movement(self.world)
        
            for p in self.player.particles[:]:
                p.update(self.world.platforms)
                if not p.active:
                    self.player.particles.remove(p)
            
            self.world.update(self.player)
            
            if self.world.door_with_player.done:
                self.state = "menu"
                
                self.world = None
                self.player.reset()
        
    def draw(self):
        if self.state == "menu":
            self.menu.draw(self.screen)
        elif self.state == "play":
            self.screen.fill("#0088aa")
            self.world.draw(self.screen)
            # draw_grid()
            
            for p in self.player.particles:
                p.draw(self.screen)
                
            self.player.draw(self.screen)
        
    def run(self):
        while self.running:
            self.handles_events()
            self.update()
            self.draw()
            
            pygame.display.update() #----> to show the content
            self.clock.tick(60) #----> 60 frames per second
        
