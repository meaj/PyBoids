"""
Pyboids - DisplayManager
 * A class containing the definitions of the DisplayManager object, which controls displaying data visually
 * Copyright (c) 2019 Meaj
"""
from math import radians

# Color Definitions
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)
GOLD = (128, 128, 64)

# TODO: adjust drawing methods to be more efficient and actually alpha the unused parts of their rects
# TODO: Add ability to toggle flock data display at bottom


class DisplayManager:
    def __init__(self, pygame, board_dims, sim_height, boid_radius):
        self.pygame = pygame

        self.window_width = board_dims[0]
        self.window_height = board_dims[1]
        self.sim_area_height = sim_height

        self.screen = pygame.display.set_mode((self.window_width, self.window_height), pygame.DOUBLEBUF)
        self.background = pygame.Surface(self.screen.get_size()).convert()
        self.background.fill(BLACK)

        self.boid_image = pygame.image.load("Sprites/boid_sprite.png")
        self.boid_image.convert_alpha(self.boid_image)
        self.boid_image = self.pygame.transform.smoothscale(self.boid_image, (boid_radius*2, boid_radius*2))
        self.font = pygame.font.SysFont('mono', 12, bold=True)

    def display_flock_data(self, flocks):
        flock_list = flocks.get_flocks()
        monitor = self.pygame.Surface((self.window_width, self.window_height - self.sim_area_height))
        monitor.blit(
            self.font.render("Number  |     Centroids    |  Direction  |  Goal Direction  |  Score  |  Members", True,
                             GREEN), (11, 0))

        i = 0
        for flock in flock_list:
            members = []
            for member in flock.flock_members:
                members.append(member.get_id())
            cent = "{:3.2f}, {:3.2f}".format(flock.flock_centroid.x, flock.flock_centroid.y)
            string = "{0:^6}{1:^5s}{2:^15}{1:^4s}{3:^10.2f}{1:^4s}{4:^14.2f}{1:^5s}{5:^6d}{1:^4s}{6:}"\
                .format(i + 1, "|", cent, flock.flock_velocity.argument(), -1, flock.flock_score, members)
            monitor.blit(self.font.render(string, True, GREEN), (12, (i+1) * 13))
            self.pygame.draw.line(monitor, GREEN, (0, (i+1) * 13), (self.window_width, (i + 1) * 13))
            i += 1
        self.pygame.draw.line(monitor, GREEN, (0, (i + 1) * 13), (self.window_width, (i + 1) * 13))
        self.screen.blit(monitor, (0, self.sim_area_height+1))

    # Displays monitoring data at the top of the screen
    def display_simulation_overview(self, fps, playtime, num_flocks, gen_num, iter_num):
        text = "FPS: {:6.2f}{}PLAYTIME: {:6.2f}{}FLOCKS: {}{}GENERATION: {}{}ITERATION: {}".\
            format(fps, " " * 5, playtime, " " * 5, num_flocks, " " * 5, gen_num, " " * 5, iter_num)
        surface = self.font.render(text, True, (0, 255, 0))
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
        boid_rect = boid_shape.get_rect(center=(x, y))
        boid_shape = self.pygame.transform.rotozoom(boid_shape, angle, 1)
        self.screen.blit(boid_shape, boid_rect)
        if draw_details:
            b_id = boid.get_id()
            txt_surface = self.pygame.font.SysFont('mono', 10, bold=False).render(str(b_id), True, (0, 255, 0))
            self.pygame.draw.arc(self.background, GOLD, [x - boid.too_close, y - boid.too_close, 60, 60],
                                 radians(angle - 135 + 90), radians(angle + 135 + 90))
            self.screen.blit(txt_surface, (x, y))

    # Draws shapes representing the centroids of the flocks of boid objects as well as the velocity of the flocks
    def display_flock_centroid_vectors(self, pos, angle):
        x = pos[0]
        y = pos[1]
        surface = self.pygame.Surface((6, 6))
        surface.convert_alpha(surface)
        surface.set_colorkey(BLACK)
        self.pygame.draw.circle(surface, RED, (3, 3), 3)
        self.pygame.draw.line(self.background, RED, (x, y), (x + (angle.x * x / 16), y + (angle.y * y / 16)))
        self.screen.blit(surface, (x, y))

    # Calls the relevant display functions once per frame
    def draw_screen(self, clock, playtime, flocks, boids, goals, draw_details=False, gen_num=0, iter_num=0):
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
