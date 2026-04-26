import pygame
import os

from fonts import get_font
from config import screen_width, screen_height
# from game import

class StartMenu():
    def __init__(self):
        self.active = True
        self.current_screen = "main"
        
        self.options = ["Play", "Mechanics", "Developers", "Quit"]
        self.selected = 0 # for options
        
        #fonts
        self.title_font = get_font(60) #change maya
        self.option_font = get_font(32)
        
        #bgd
        self.dark_topd = pygame.transform.scale(pygame.image.load(os.path.join("image_s", "dark_top.png")), (screen_width, 250))
        self.pathways = pygame.transform.scale(pygame.image.load(os.path.join("image_s", "pathway_all.png")), (875, 303))
        
        #doorlevels
        self.door_img = pygame.transform.scale(
            pygame.image.load(os.path.join("image_s", "door_spiker.png")).convert_alpha(), 
            (100, 80)
        )
        
        #PROGRESSION
        self.unlocked = 1
        self.selected_level = 0
        #up=-
        #left=-
        #rects of doors
        self.doors = [#rect = x,y,w,h
            {"rect": pygame.Rect(467, 554, 100, 90), "level": 1},
            {"rect": pygame.Rect(277, 495, 100, 90), "level": 2},
            {"rect": pygame.Rect(214, 373, 100, 90), "level": 3},
            {"rect": pygame.Rect(404, 295, 100, 90), "level": 4},
            {"rect": pygame.Rect(590, 320, 100, 90), "level": 5},
            {"rect": pygame.Rect(690, 430, 100, 90), "level": 6},
            {"rect": pygame.Rect(857, 497, 100, 90), "level": 7},
            {"rect": pygame.Rect(1015, 440, 100, 90), "level": 8}
        ]
        
    def complete_level(self, level_idx):
        next_level = level_idx + 1
        if next_level > self.unlocked and next_level < len(self.doors):
            self.unlocked = next_level #one new door
    
    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_DOWN:
                self.selected = (self.selected + 1) % len(self.options) #to movr
            if event.key == pygame.K_UP:
                 self.selected = (self.selected - 1) % len(self.options)
            if event.key == pygame.K_RETURN:
                choice = self.options[self.selected]
                
                if choice == "Quit":
                    pygame.quit()
                    exit()
                
                if choice == "Play":
                    self.selected_level = self.unlocked - 1
                    self.active = False #exits startmenu and proceeds to the game
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            
            for door in self.doors:
                 if door["rect"].collidepoint(mouse_pos):
                    idx = door["level_idx"]
                    if idx < self.unlocked:
                        self.selected_level = idx  
                        self.active = False
        
    
    def update(self):
        pass
    
    def draw(self, screen):
        screen.fill("#0088aa")
        
        screen.blit(self.dark_topd, (0, 0))
        screen.blit(self.pathways, (224, 331))
        
        title = self.title_font.render("NOT A TRAP", True, (255, 255, 255))
        screen.blit(title, (100, 50))
        
        for door in self.doors:
            screen.blit(self.door_img, door["rect"].topleft)
        
        
        
        
        