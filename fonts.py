import pygame
import os

pygame.font.init()

font_path = os.path.join("fonts", "pixelated.otf")

def get_font(size):
    return pygame.font.Font(font_path, size)

#render later siguro
