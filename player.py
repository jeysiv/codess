import pygame
import os
import random
import math

from config import screen_width, screen_height


class DeathParticle():
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
    
    def draw(self, screen):
        if self.active:
            pygame.draw.rect(screen, self.color, (int(self.x), int(self.y), self.chunk_size, self.chunk_size))        



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
    
    def draw(self, screen):
        image_x = self.rect.x - (self.image.get_width() - self.rect.width) // 2
        image_y = self.rect.y - (self.image.get_height() - self.rect.height) // 2
        
        #for transpercy
        img = self.image.copy()
        img.set_alpha(self.alpha)
        
        screen.blit(img, (image_x, image_y))
    
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

