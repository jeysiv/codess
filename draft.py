import pygame
from pygame.locals import *
import os
import random
import math

pygame.init()

#screen size
screen_width = 1280
screen_height = 720

#time frame
clock = pygame.time.Clock()

screen = pygame.display.set_mode((screen_width, screen_height), pygame.FULLSCREEN | pygame.SCALED)

# screen = pygame.display.set_mode((screen_width, screen_height)) #, pygame.FULLSCREEN
pygame.display.set_caption("WHAT")#----> title




#FOR GRID
tile_size = 40

class Fonts():
    def __init__(self):
        self.font_title = pygame.font.Font(os.path.join("fonts", "pixelated.otf"))

    #render later siguro


class StartMenu():
    def __init__(self):
        self.active = True
        self.current_screen = "main"
        
        self.options = ["Play", "Mechanics", "Developers", "Quit"]
        self.selected = 0 # for options
        
        #fonts
        self.title_font = font_title(50) #change maya
        
        #bgd
        self.background = pygame.transform.scale(pygame.image.load(os.path.join("image_s", "whole_bgd_menu.png")), (screen_width, screen_height))
    
    def draw(self, screen):
        screen.blit(self.background, (0, 0))
        
        title = self.title_font.render("NOT A TRAP", True, (255, 255, 255))
        screen.blit(title, (100, 50))
        
        

class DeathParticle:
    def __init__(self, x, y, angle, speed):
        #position
        self.x = x
        self.y = y
        
        #random movemnt
        self.VELOCITY_X = math.cos(angle) * speed
        self.VELOCITY_Y = math.sin(angle) * speed
        
        #size of chunk
        self.chunk_size = random.randint(3, 5)
        
        self.color = (0, 0, 0)
        
        self.active = True
        
        # #gravity
        # self.gravity = 0.25
        
    def update(self, platforms):
        if not self.active:
            return
        
        #particle move
        self.x += self.VELOCITY_X
        particle_rect = pygame.Rect(int(self.x), int(self.y), self.chunk_size, self.chunk_size)
        for tile in platforms:
            if particle_rect.colliderect(tile.rect):
                if self.VELOCITY_X > 0:
                    self.x = tile.rect.left - self.chunk_size
                elif self.VELOCITY_X < 0:
                    self.x = tile.rect.right
                break
        
        self.y += self.VELOCITY_Y
        particle_rect = pygame.Rect(int(self.x), int(self.y), self.chunk_size, self.chunk_size)
        for tile in platforms:
            if particle_rect.colliderect(tile.rect):
                # Land on top of tile — stop vertical movement, slide horizontal
                if self.VELOCITY_Y > 0:
                    self.y = tile.rect.top - self.chunk_size
                    self.VELOCITY_Y = 0
                    self.VELOCITY_X *= 0.6  # friction when landing
                elif self.VELOCITY_Y < 0:
                    self.y = tile.rect.bottom
                    self.VELOCITY_Y = 0
                break
        
        #GRAVTIY ON PARTICLES
        self.VELOCITY_Y += 0.6
        if self.VELOCITY_Y > 12:
            self.VELOCITY_Y = 12
        
        #air resistance raw
        self.VELOCITY_X *= 1.1
        
        if self.y > screen_height + 50:
            self.active = False
    
    def draw(self, surface):
        if self.active:
            pygame.draw.rect(surface, self.color, (int(self.x), int(self.y), self.chunk_size, self.chunk_size))        



class Player(pygame.sprite.Sprite):
    def __init__(self, PLAYER_X, PLAYER_Y): #POSITION X, Y
        super().__init__()
        self.start_x = PLAYER_X
        self.start_y = PLAYER_Y
        
        #IMAGES
        self.player_static_r = pygame.transform.scale(
            pygame.image.load(os.path.join("image_s", "static.png")), (32, 36)
        )
        
        self.player_moving_r = [#list
            pygame.transform.scale(pygame.image.load(os.path.join("image_s", "move_1.png")), (32, 36)),
            pygame.transform.scale(pygame.image.load(os.path.join("image_s", "move_2.png")), (32, 36)),
            pygame.transform.scale(pygame.image.load(os.path.join("image_s", "move_3.png")), (32, 36)),
            pygame.transform.scale(pygame.image.load(os.path.join("image_s", "move_4.png")), (32, 36)),
        ]
        
        #FLIP THR RIGHT TO LEFT HAHAHAHAHAHAHAHAHAHAHAHAHAHAHA JK
        self.player_static_l = pygame.transform.flip(self.player_static_r, True, False)
        self.player_moving_l = [
            pygame.transform.flip(img, True, False) for img in self.player_moving_r
        ]
        
        #IMAGE CONTAINER
        self.image = self.player_moving_r[1] #1 for moving
        
        #FOR POSITIONING
        self.rect = pygame.Rect(0, 0, 17, 36)
        
        self.rect.x = PLAYER_X
        self.rect.y = PLAYER_Y
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        
        #FOR THE PHYSICS AY/SPEED FOR X AND Y
        self.VELOCITY_Y = 0
        self.VELOCITY_X = 0

        
        self.direction = "right"
        self.state = "static"
        
        self.frame_index = 0 #which frame is currently showing
        self.animation_speed = 0.20 #how fast the sprite frames for every loop
        
        #deads
        self.dead = False
        self.death_triggered = False
        self.particles = []
        
        #transparency
        self.alpha = 255
        self.fading = False
    
    def spawn_particles(self):
        num_particles = 20
        
        for i in range(num_particles):
            #spread
            angle = (2 * math.pi / num_particles) * i
            angle += random.uniform(-0.15, 0.15)
            
            speed = random.uniform(2.5, 9.0)
            
            spawn_x = self.rect.x + random.randint(0, self.rect.width - 1)
            spawn_y = self.rect.y + random.randint(0, self.rect.height - 1)
            
            particle = DeathParticle(spawn_x, spawn_y, angle, speed)
            
            self.particles.append(particle)
    
    def movement(self, world):
        if self.dead:
            if not self.death_triggered:
                self.spawn_particles()
                self.death_triggered = True
                self.alpha = 0
            
            return
        
        keys = pygame.key.get_pressed() #smooth movement (continuous)
        self.moving = False #reset every frame
        self.VELOCITY_X = 0 #reset so player doesnt accelerate forever
        
        #for keys
        if keys[pygame.K_LEFT]:
            self.VELOCITY_X -= 3.5 #-5
            self.direction = "left"
            self.moving = True
            
        if keys[pygame.K_RIGHT]:
            self.VELOCITY_X += 3.5 #+5
            self.direction = "right"
            self.moving = True
        
        #move x first then check collisions
        self.rect.x += self.VELOCITY_X #150 + (-+5) = ?
        self.check_collision_x(world)
        
        #GRAVITY
        self.VELOCITY_Y += 0.8 #velocity gets down(since positive)----> what pulls the velocity down
        if self.VELOCITY_Y > 10: #for jump
            self.VELOCITY_Y = 10 #limit fall speed
        self.rect.y += self.VELOCITY_Y
        self.check_collision_y(world)
        
        if self.rect.bottom > screen_height:
            self.dead = True
        
        #state
        if self.VELOCITY_Y != 0:
            self.state = "jump"
        elif self.moving:
            self.state = "walk"
        else:
            self.state = "static"
        
        #frame animation
        if self.state != "walk":
            self.frame_index = 0
            
            
        # #CONDITION FOR MOVEMENT(WALKING)
        if self.state == "walk":
            self.frame_index += self.animation_speed #0 + 0.15 if moving
            
            #if frame sprite is >= number in list(4), it resets to 0----> to reset the frames
            if self.frame_index >= len(self.player_moving_r): #len() for getting the list from the player_moving_r sa taas #if 0.15 >= 2 -> so false
                self.frame_index = 0 #goes back
            
            if self.direction == "right":
                self.image = self.player_moving_r[int(self.frame_index)]
            else:
                self.image = self.player_moving_l[int(self.frame_index)]
                
        elif self.state == "jump":
            if self.direction == "right":
                self.image = self.player_moving_r[1]
            else:
                self.image = self.player_moving_l[1]

            
        else:
            self.frame_index = 0
            
            if self.direction == "right":
                self.image = self.player_static_r
            else:
                self.image = self.player_static_l
                
          
        
    def check_collision_x(self, world):
        for tile in world.platforms:
            if self.rect.colliderect(tile.rect):
                if self.VELOCITY_X > 0:
                    self.rect.right = tile.rect.left
                elif self.VELOCITY_X < 0:
                    self.rect.left = tile.rect.right
        
    def check_collision_y(self, world):
        for tile in world.platforms:
            if self.rect.colliderect(tile.rect):
                if self.VELOCITY_Y > 0:
                    self.rect.bottom = tile.rect.top
                    self.VELOCITY_Y = 0
                elif self.VELOCITY_Y < 0:
                    self.rect.top = tile.rect.bottom
                    self.VELOCITY_Y = 0
    

#---------->
    
    def draw(self, surface):
        image_x = self.rect.x - (self.image.get_width() - self.rect.width) // 2
        image_y = self.rect.y - (self.image.get_height() - self.rect.height) // 2
        
        #for transpercy
        img = self.image.copy()
        img.set_alpha(self.alpha)
        
        surface.blit(img, (image_x, image_y))
    
    def reset(self):
        self.rect.x = self.start_x
        self.rect.y = self.start_y
        self.VELOCITY_X = 0
        self.VELOCITY_Y = 0
        self.state = "static"
        
        
        self.dead = False
        self.death_triggered = False
        self.particles = []
        
        self.alpha = 255
        self.fading = False




#--------------------------------------------------------------------->
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
        
        
        
    # def trigger(self, player):
    #     player_center_x = player.rect.centerx
    #     block_center_x = self.rect.centerx
        
    #     distance = abs(player_center_x - block_center_x) #horizontal d (absolute value so it can wrkk left or right of the block)
        
    #     if distance <= self.trigger_range:
    #         self.falling = True

    # # def trigger(self, player):
    # #     dx = abs(player.rect.centerx - self.rect.centerx)
    # #     dy = abs(player.rect.centery - self.rect.centery)

    # #     if dx <= self.trigger_range and dy <= 100:  # within range horizontally AND roughly same height
    # #         self.falling = True

    # def update_afttrigger(self):
    #     if self.falling:
    #         self.rect.y += self.fall_speed
    #         if self.rect.y > screen_height + 100:
    #             world.tile_list.remove(self)
            
    #Every frame, if the block is falling, it moves down by fall_speed pixels. Note: with a fall speed of 50 it'll jump very fast each frame — you may want to lower this.


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
        
        

#--------------------------------------------------------------->
class World():
    def __init__(self, data):
        self.platforms = pygame.sprite.Group()
        self.falling_blocks = pygame.sprite.Group()
        self.spikes = pygame.sprite.Group()
        self.door = pygame.sprite.Group()
        self.door_with_player = DoorWithPlayer()

        tile_surface = pygame.Surface((tile_size, tile_size))
        tile_surface.fill("#003a49")
        
        tile_surfs =  pygame.Surface((tile_size, tile_size))
        tile_surfs.fill("#003a49")
        
        tile_spike = pygame.transform.scale(pygame.image.load(os.path.join("image_s", "spike_static.png")), (40, 7))
        
        tile_door = pygame.transform.scale(pygame.image.load(os.path.join("image_s", "door.png")), (32, 38))

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
    
    def draw(self):
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
    
    def reset(self):
        for block in self.falling_blocks:
            block.rect.y = block.start_y
            block.falling = False
        
        for door in self.door:
            door.active = True
        self.door_with_player.reset()

            


world_data = [
    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,4,0,1],
    [1,1,1,1,1,1,1,2,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,2,1,1,1],
    [1,1,1,1,1,1,1,2,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,2,1,1,1],
    [1,1,1,1,1,1,1,2,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,2,1,1,1],
    [1,1,1,1,1,1,1,2,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,2,1,1,1],
    [1,1,1,1,1,1,1,2,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,2,1,1,1],
    [1,1,1,1,1,1,1,2,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,2,1,1,1],
    [1,1,1,1,1,1,1,2,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,2,1,1,1],
    [1,1,1,1,1,1,1,2,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,2,1,1,1],
    [1,1,1,1,1,1,1,2,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,2,1,1,1],
    [1,1,1,1,1,1,1,2,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,2,1,1,1]
]






def draw_grid():
    for line in range(0,100):
        pygame.draw.line(screen, (255, 255, 255), (0, line* tile_size), (screen_width, line * tile_size))
        pygame.draw.line(screen, (255, 255, 255), (line* tile_size, 0), (line * tile_size, screen_width))



# player = Player(150, 200) # x, y #starting pos
# world = World(world_data)

class Game():
    def __init__(self):
        pygame.init()
        
        self.screen = pygame.display.set_mode((screen_width, screen_height), pygame.FULLSCREEN | pygame.SCALED)
        self.clock = pygame.time.Clock()
        
        self.menu = StartMenu()
        self.state = "menu"

        # screen = pygame.display.set_mode((screen_width, screen_height)) #, pygame.FULLSCREEN
        pygame.display.set_caption("WHAT")#----> title


        self.player = Player(150, 200) # x, y #starting pos
        self.world = World(world_data)
        self.running = True
        
        

    
    def handles_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                
            if self.state == "menu":
                self.menu.handle_event(event)
                            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and self.player.VELOCITY_Y == 0:
                    self.player.VELOCITY_Y = -8
            
                if event.key == pygame.K_RETURN and self.player.dead:
                    self.world.reset()
                    self.player.reset()
                    self.player.dead = False
        
    def update(self):
        if self.state == "menu":
            self.menu.update()
        else:
            self.player.movement(self.world)
        
            for p in self.player.particles[:]:
                p.update(self.world.platforms)
                if not p.active:
                    self.player.particles.remove(p)
            
            self.world.update(self.player)
        
    def draw(self):
        if self.state == "menu":
            self.menu.draw(self.screen)
        else:
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
        

#MAIN LOOP
game = Game()
game.run()

pygame.quit()


    # draw_grid()        
        # if keys[pygame.K_SPACE] and self.VELOCITY_Y == 0:
        #     self.VELOCITY_Y = -12 #velocity becomes -12(goes up)