import pygame

# Game_state Definitions
LOADED = -2
EXIT = -1
MAIN_MENU = 0
NEW_SIM_MENU = 1
LOAD_SIM_MENU = 2
HELP_MENU = 3
RUN_SIMULATION = 4
PAUSE_SIMULATION = 5
END_SIMULATION = 6

# Color Definitions
RED = (255, 0, 0)
PURPLE = (230, 0, 230)
GREEN = (0, 255, 0)
DARK_GREEN = (0, 200, 0)
GREY = (35, 35, 35)
LIGHT_GREY = (85, 85, 85)
BLACK = (0, 0, 0)
GOLD = (128, 128, 64)

ENTRY_KEYS = [pygame.K_0, pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4, pygame.K_5, pygame.K_6,
              pygame.K_7, pygame.K_8, pygame.K_9, pygame.K_PERIOD, pygame.K_KP_MINUS, pygame.K_MINUS]

# Maximum velocity a boid can move in any direction
MAX_VELOCITY = 3.5

# Maximum force applied to the boid from control rules
MAX_FORCE = 2

# Format for update is completed_release.goal_number.update_number
VERSION = "0.5.1"


# Function to return a surface and rect for displaying data
def text_setup(string, font):
    surf = font.render(string, False, GREEN)
    return surf, surf.get_rect()
