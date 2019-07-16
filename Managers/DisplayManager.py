"""
Pyboids - DisplayManager
 * A class containing the definitions of the DisplayManager object, which controls displaying data visually
 * Copyright (c) 2019 Meaj
"""
from math import radians
import pygame

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


def text_setup(string, font):
    surf = font.render(string, False, GREEN)
    return surf, surf.get_rect()


# TODO convert button function to button objects
class Button:
    def __init__(self, text, x_pos, y_pos, width, height, pygame_instance, function=None):
        self.pygame = pygame_instance
        self.x_pos = x_pos
        self.y_pos = y_pos
        self.width = width
        self.height = height
        self.color = LIGHT_GREY
        self.function = function
        self.text_rect = self.pygame.Rect(x_pos, y_pos, width, height)
        self.text = text
        self.font = pygame_instance.font.SysFont('courier new', 12, bold=True)
        self.text_surf = self.font.render(text, False, GREEN)
        
    def check_click(self):
        mouse = self.pygame.mouse.get_pos()
        click = self.pygame.mouse.get_pressed()
        if self.x_pos < mouse[0] < self.x_pos + self.width and self.y_pos < mouse[1] < self.y_pos + self.height:
            self.color = GREY
            if click[0] == 1 and self.function is not None:
                self.function()
        else:
            self.color = LIGHT_GREY
            
    def draw_button(self, screen):
        self.pygame.draw.rect(screen, self.color, (self.x_pos, self.y_pos, self.width, self.height))
        button_surf, button_rect = text_setup(self.text, self.font)
        button_rect.center = (self.x_pos + self.width / 2, self.y_pos + self.height / 2)
        screen.blit(button_surf, button_rect)


class InputBox:
    def __init__(self, in_text, title_text, x_pos, y_pos, width, height, pygame_instance):
        self.pygame = pygame_instance
        self.text_rect = self.pygame.Rect(x_pos + width, y_pos, width, height)
        self.in_text = in_text
        self.font = pygame_instance.font.SysFont('courier new', 12, bold=True)
        self.text_surf = self.font.render(in_text, False, GREEN)
        self.input_active = False
        self.title_rect = self.pygame.Rect(x_pos - width, y_pos, width, height)
        self.title_surf = self.font.render(title_text, False, GREEN)

    def handle_event(self, event, function=None):
        if event.type == self.pygame.MOUSEBUTTONDOWN:
            if self.text_rect.collidepoint(event.pos):
                self.input_active = not self.input_active
            else:
                self.input_active = False
        if event.type == self.pygame.KEYDOWN:
            if self.input_active:
                if event.key == self.pygame.K_RETURN:
                    if function:
                        function(self.in_text)
                    else:
                        print(self.in_text)
                elif event.key == self.pygame.K_BACKSPACE:
                    self.in_text = self.in_text[:-1]
                elif event.key in ENTRY_KEYS:
                    self.in_text += event.unicode
                self.text_surf = self.font.render(self.in_text, True, LIGHT_GREY)

    def draw_box(self, screen):
        screen.blit(self.text_surf, self.text_rect)
        screen.blit(self.title_surf, self.title_rect)
        self.pygame.draw.rect(screen, GREY, self.title_rect, 2)
        self.pygame.draw.rect(screen, LIGHT_GREY, self.text_rect, 2)


class DisplayManager:
    def __init__(self, pygame_instance, board_dims, sim_height, boid_radius):
        self.pygame = pygame_instance

        # Window setup
        self.window_width = board_dims[0]
        self.window_height = board_dims[1]
        self.sim_area_height = sim_height
        self.screen = pygame_instance.display.set_mode((self.window_width, self.window_height),
                                                       pygame_instance.DOUBLEBUF)
        self.background = pygame_instance.Surface(self.screen.get_size()).convert()
        self.background.fill(BLACK)

        # Boid image setup
        self.boid_image = pygame_instance.image.load("Sprites/boid_sprite.png")
        self.boid_image.convert_alpha(self.boid_image)
        self.pygame.display.set_icon(self.boid_image)
        self.boid_image = self.pygame.transform.smoothscale(self.boid_image, (boid_radius*2, boid_radius*2))


        # Font setup
        self.normal_font = pygame_instance.font.SysFont('courier new', 12, bold=True)
        self.large_font = pygame_instance.font.SysFont('courier new', 48, bold=True)

        # Input box setup
        # TODO: Clean this up

    def display_flock_data(self, flocks):
        flock_list = flocks.get_flocks()
        monitor = self.pygame.Surface((self.window_width, self.window_height - self.sim_area_height))
        monitor.blit(
            self.normal_font.render("Number  |     Centroids    |  Direction  |  Goal Direction  |  Score  |  Members", True,
                                    GREEN), (11, 0))

        for idx, flock in enumerate(flock_list):
            members = []
            for member in flock.flock_members:
                members.append(member.get_id())
            cent = "{:3.2f}, {:3.2f}".format(flock.flock_centroid.x, flock.flock_centroid.y)
            string = "{0:^6}{1:^5s}{2:^15}{1:^4s}{3:^10.2f}{1:^4s}{4:^14.2f}{1:^5s}{5:^6d}{1:^4s}{6:}"\
                .format(idx + 1, "|", cent, flock.flock_velocity.argument(), flock.flock_goal_dir, flock.flock_score, members)
            monitor.blit(self.normal_font.render(string, True, GREEN), (12, (idx + 1) * 13))
            self.pygame.draw.line(monitor, GREEN, (0, (idx+1) * 13), (self.window_width, (idx + 1) * 13))
        self.pygame.draw.line(monitor, GREEN, (0, (len(flock_list) + 1) * 13), (self.window_width, (len(flock_list) + 1) * 13))
        self.screen.blit(monitor, (0, self.sim_area_height+1))

    # Displays monitoring data at the top of the screen
    def display_simulation_overview(self, fps, playtime, num_flocks, gen_num, species_num):
        text = "FPS: {:6.2f}{}PLAYTIME: {:6.2f}{}FLOCKS: {}{}GENERATION: {}{}SPECIES: {}".\
            format(fps, " " * 5, playtime, " " * 5, num_flocks, " " * 5, gen_num, " " * 5, species_num)
        surface = self.normal_font.render(text, True, (0, 255, 0))
        self.screen.blit(surface, (0, 0))

    # Draws shapes representing goal objects
    def display_goal(self, pos, radius):
        x = pos[0]
        y = pos[1]
        surface = self.pygame.Surface((2*radius, 2*radius))
        surface.convert_alpha(surface)
        surface.set_colorkey(BLACK)
        self.pygame.draw.circle(surface, GOLD, (radius, radius), radius)
        self.screen.blit(surface, (x, y))

    # Draws shapes representing the boid objects
    def display_boid(self, boid, draw_details):
        x = boid.get_position().x
        y = boid.get_position().y
        angle = boid.my_dir
        boid_shape = self.boid_image
        boid_shape = self.pygame.transform.rotozoom(boid_shape, angle, 1)
        boid_rect = boid_shape.get_rect(center=(x, y))
        self.screen.blit(boid_shape, boid_rect)
        if draw_details:
            b_id = boid.get_id()
            txt_surface = self.pygame.font.SysFont('mono', 10, bold=False).render(str(b_id), True, (0, 255, 0))
            too_close_rect = self.pygame.Rect(0, 0, boid.too_close, boid.too_close)
            too_close_rect.center = (x, y)
            self.pygame.draw.arc(self.background, RED, too_close_rect,
                                 radians(angle - 135 + 90), radians(angle + 135 + 90))
            too_far_rect = self.pygame.Rect(0, 0, boid.too_far, boid.too_far)
            too_far_rect.center = (x, y)
            self.pygame.draw.arc(self.background, GOLD, too_far_rect,
                                 radians(angle - 135 + 90), radians(angle + 135 + 90))
            self.screen.blit(txt_surface, (x, y))

    # Draws shapes representing the centroids of the flocks of boid objects as well as the velocity of the flocks
    def display_flock_centroid_vectors(self, pos, angle):
        x = pos[0]
        y = pos[1]
        surface = self.pygame.Surface((6, 6))
        surface.convert_alpha(surface)
        surface.set_colorkey(BLACK)
        self.pygame.draw.circle(surface, PURPLE, (3, 3), 3)
        self.pygame.draw.line(self.background, RED, (x, y), (x + (angle.x * x / 16), y + (angle.y * y / 16)))
        self.screen.blit(surface, (x, y))

    def menu_button(self, text, x_pos, y_pos, width, height, on_color, off_color, function=None):
        mouse = self.pygame.mouse.get_pos()
        click = self.pygame.mouse.get_pressed()
        if x_pos < mouse[0] < x_pos + width and y_pos < mouse[1] < y_pos + height:
            self.pygame.draw.rect(self.screen, on_color, (x_pos, y_pos, width, height))
            if click[0] == 1 and function is not None:
                function()
        else:
            self.pygame.draw.rect(self.screen, off_color, (x_pos, y_pos, width, height))
        button_surf, button_rect = text_setup(text, self.normal_font)
        button_rect.center = (x_pos+width/2, y_pos+height/2)
        self.screen.blit(button_surf, button_rect)

    # Draws the menu that opens when starting the simulation
    def draw_start_screen(self, function_1, function_2, function_3, version="0.0.0"):
        self.background.fill(BLACK)
        self.screen.blit(self.background, (0, 0))
        title = "PyBoids"
        tagline = "An Experimental AI Simulation"
        version_data = "Version {}".format(version)

        title_surf, title_rect = text_setup(title, self.large_font)
        title_rect.center = (self.window_width/2, 3*self.window_height/16)

        tag_surf, tag_rect = text_setup(tagline, self.normal_font)
        tag_rect.center = (self.window_width/2, (3*self.window_height/16)+32)

        vers_surf, vers_rect = text_setup(version_data, self.normal_font)
        vers_rect.topleft = (6, self.window_height-12)

        self.screen.blit(title_surf, title_rect)
        self.screen.blit(tag_surf, tag_rect)
        self.screen.blit(vers_surf, vers_rect)

        self.menu_button("New Sim", self.window_width / 2 - 60, 1 * self.window_height / 2, 120, 60, LIGHT_GREY, GREY, function_1)
        self.menu_button("Load Sim", self.window_width / 2 - 60, 5 * self.window_height / 8, 120, 60, LIGHT_GREY, GREY, function_2)
        self.menu_button("Help ?", self.window_width / 2 - 60, 3 * self.window_height / 4, 120, 60, LIGHT_GREY, GREY, function_3)

        self.pygame.display.update()

    # Draws the menu that sets up the simulation
    def draw_simulation_settings_screen(self, function_1, function_2):
        self.background.fill(BLACK)
        self.screen.blit(self.background, (0, 0))

        title = "Setup New Simulation"
        title_surf, title_rect = text_setup(title, self.large_font)
        title_rect.center = (self.window_width / 2, 3 * self.window_height / 16)

        self.menu_button("Begin Sim", self.window_width/3 - 60, 3 * self.window_height / 4, 120, 60, LIGHT_GREY, GREY,
                         function_1)
        self.menu_button("Go Back", 2 * self.window_width / 3 - 60, 3 * self.window_height / 4, 120, 60, LIGHT_GREY, GREY,
                         function_2)

        self.screen.blit(title_surf, title_rect)
        self.pygame.display.update()

    # Draws the menu that sets up the simulation
    def draw_load_simulation_screen(self, function_1, function_2):
        self.background.fill(BLACK)
        self.screen.blit(self.background, (0, 0))
        title = "Load Simulation"
        title_surf, title_rect = text_setup(title, self.large_font)
        title_rect.center = (self.window_width / 2, 3 * self.window_height / 16)

        self.menu_button("Load Sim", self.window_width/3 - 60, 3 * self.window_height / 4, 120, 60, LIGHT_GREY, GREY,
                         function_1)
        self.menu_button("Go Back", 2 * self.window_width / 3 - 60, 3 * self.window_height / 4, 120, 60, LIGHT_GREY, GREY,
                         function_2)

        self.screen.blit(title_surf, title_rect)
        self.pygame.display.update()

    # Calls the relevant display functions once per frame
    def draw_simulation_screen(self, clock, playtime, flocks, boids, goals, draw_details=False, gen_num=0, iter_num=0):
        # Clear the screen
        self.background.fill(BLACK)
        # Draw the monitoring at the top of the screen
        self.display_simulation_overview(clock.get_fps(), playtime, len(flocks.get_flocks()), gen_num, iter_num)
        # Draw objects in the simulation area
        for boid in boids:
            self.display_boid(boid, draw_details)
        for goal in goals:
            self.display_goal(goal.get_position(), 3)
        if draw_details:
            # Draw flock centroids and velocity vectors
            for flock in flocks.get_flocks():
                self.display_flock_centroid_vectors(flock.flock_centroid, flock.flock_velocity)
        # Draw the flock data at the bottom
        self.display_flock_data(flocks)
        # Draw bottom line for sim area
        self.pygame.draw.line(self.background, GREEN, (0, self.sim_area_height),
                              (self.window_width, self.sim_area_height))
        # Draw top line for sim area
        self.pygame.draw.line(self.background, GREEN, (0, 12), (self.window_width, 12))
        self.pygame.display.flip()  # (╯°□°)╯︵ ┻━┻
        self.screen.blit(self.background, (0, 0))

