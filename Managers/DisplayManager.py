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
    def __init__(self, pygame, board_dims, sim_height):
        self.pygame = pygame
        self.font = pygame.font.SysFont('mono', 12, bold=True)

        self.window_width = board_dims[0]
        self.window_height = board_dims[1]
        self.sim_area_height = sim_height

        self.screen = pygame.display.set_mode((self.window_width, self.window_height), pygame.DOUBLEBUF)
        self.background = pygame.Surface(self.screen.get_size()).convert()
        self.background.fill(BLACK)

    def display_flock_data(self, flocks):
        flock_list = flocks.get_flocks()
        flock_thetas = flocks.get_thetas()
        flock_goals = flocks.get_goal_thetas()
        flock_centroids = flocks.get_centroids()
        flock_scores = flocks.get_scores()
        monitor = self.pygame.Surface((self.window_width, self.window_height - self.sim_area_height))
        monitor.blit(
            self.font.render("Number  |     Centroids    |  Direction  |  Goal Direction  |  Score  |  Members", True,
                             GREEN), (11, 0))

        i = 0
        for i in range(len(flock_list)):
            cent = "{:3.2f}, {:3.2f}".format(flock_centroids[i][0], flock_centroids[i][1])
            string = "{0:^6}{1:^5s}{2:^15}{1:^4s}{3:^10.2f}{1:^4s}{4:^14.2f}{1:^5s}{5:^6d}{1:^4s}{6:}"\
                .format(i + 1, "|", cent, flock_thetas[i], flock_goals[i], flock_scores[i], flock_list[i])
            monitor.blit(self.font.render(string, True, GREEN), (12, (i+1) * 13))
            self.pygame.draw.line(monitor, GREEN, (0, (i+1) * 13), (self.window_width, (i + 1) * 13))
        self.pygame.draw.line(monitor, GREEN, (0, (i + 2) * 13), (self.window_width, (i + 2) * 13))
        self.screen.blit(monitor, (0, self.sim_area_height+1))

    # Displays monitoring data at the top of the screen
    def display_simulation_overview(self, fps, playtime, num_flocks):
        text = "FPS: {:6.2f}{}PLAYTIME: {:6.2f}{}FLOCKS: {}".format(fps, " " * 5, playtime, " " * 5, num_flocks)
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
        height = boid.get_height()
        angle = boid.my_dir
        points = [(int(height // 2), 0),
                  (0, int(height)),
                  (int(height), int(height))]
        surface = self.pygame.Surface((height, height))
        surface.convert_alpha(surface)
        self.pygame.draw.polygon(surface, GREEN, points)
        surface.set_colorkey(BLACK)
        self.screen.blit(self.pygame.transform.rotozoom(surface, angle, 1), (x - height // 2, y - height // 2))
        if draw_details:
            b_id = boid.get_id()
            txt_surface = self.pygame.font.SysFont('mono', 10, bold=False).render(str(b_id), True, (0, 255, 0))
            self.pygame.draw.arc(self.background, GOLD, [x - 30, y - 30, 60, 60],
                                 radians(angle - 135 + 90), radians(angle + 135 + 90))
            self.screen.blit(txt_surface, (x - 2, y + 3 * height // 4))

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
    def draw_screen(self, clock, playtime, flocks, boids, goals, draw_details=False):
        # Clear the screen
        self.background.fill(BLACK)
        # Draw the monitoring at the top of the screen
        self.display_simulation_overview(clock.get_fps(), playtime, len(flocks.get_flocks()))
        # Draw objects in the simulation area
        for boid in boids:
            self.display_boid(boid, draw_details)
        for goal in goals:
            self.display_goal(goal.get_position(), 3)
        if draw_details:
            idx = 0
            for centroid in flocks.get_centroids():
                self.display_flock_centroid_vectors(centroid, flocks.get_velocities()[idx])
                idx += 1
        # Draw the flock data at the bottom
        self.display_flock_data(flocks)
        # Draw bottom line for sim area
        self.pygame.draw.line(self.background, GREEN, (0, self.sim_area_height),
                              (self.window_width, self.sim_area_height))
        # Draw top line for sim area
        self.pygame.draw.line(self.background, GREEN, (0, 12), (self.window_width, 12))
        self.pygame.display.flip()  # (╯°□°)╯︵ ┻━┻
        self.screen.blit(self.background, (0, 0))
