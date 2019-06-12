"""
Pyboids - GameManager
 * A class containing the definitions of the GameManager object
 * Copyright (c) 2019 Meaj
"""
import pygame
import math
import random
from Entities import Boid, Goal
from FlockManager import FlockManager
from ReynoldsControl import move_all_boids

# TODO: adjust drawing methods to be more efficient and actually alpha the unused parts of their rects
# TODO: Draw a line representing the direction of the flock
# TODO: Draw visible range of each boid for connection formation

RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)
GOLD = (128, 128, 64)


class GameManager:

    def __init__(self, window_width=980, sim_area_height=620, fps=60, boid_height=12):
        # Initialize random and pygame
        random.seed()
        pygame.init()
        # Setup Window
        pygame.display.set_caption("Press ESC to quit")
        self.boid_height = boid_height
        self.window_width = window_width  # width of the window and simulation area
        self.sim_area_height = sim_area_height  # height of the simulation area
        self.window_height = sim_area_height + 15 * 10
        self.screen = pygame.display.set_mode((self.window_width, self.window_height), pygame.DOUBLEBUF)
        self.background = pygame.Surface(self.screen.get_size()).convert()
        self.background.fill(BLACK)
        self.surface = self.screen
        # Timing and monitoring data
        self.clock = pygame.time.Clock()
        self.FPS = fps
        self.playtime = 0.0
        self.font = pygame.font.SysFont('mono', 12, bold=True)
        # Object lists
        self.goals = []
        self.boids = []
        self.flocks = FlockManager()
        # temporary goal deployment
        self.goals.append(Goal(1, random.randrange(15, self.window_width - 15),
                               random.randrange(15, self.sim_area_height - 15)))
        # temporary testing boid to setup controls, hitboxes, etc
        for i in range(0, 16):
            self.boids.append(Boid(i, random.randrange(0, self.window_width), random.randrange(1, self.sim_area_height),
                                   boid_height))

        # Triangle test
        # self.boids.append(Boid(1, 315, 270, boid_height))
        # self.boids.append(Boid(2, 300, 300, boid_height))
        # self.boids.append(Boid(3, 330, 300, boid_height))
        # self.boids.append(Boid(4, 345, 330, boid_height))
        # self.boids.append(Boid(5, 315, 330, boid_height))
        # self.boids.append(Boid(6, 285, 330, boid_height))
        # Square test
        # self.boids.append(Boid(1, 330, 330, boid_height))
        # self.boids.append(Boid(2, 300, 300, boid_height))
        # self.boids.append(Boid(3, 330, 300, boid_height))
        # self.boids.append(Boid(4, 300, 330, boid_height))

    def get_boid_by_id(self, boid_id):
        for boid in self.boids:
            if boid.get_id() == boid_id:
                return boid

    # removes boids that have collided and adds scores
    def get_collisions(self):
        for boid in self.boids:
            col = boid.get_collisions()
            if col:
                for c in col:
                    if c in self.boids:
                        self.boids.remove(c)
                    print("{} died due to a collision!".format(c.get_id()))
                    del c
                self.boids.remove(boid)
                print("{} died due to a collision!".format(boid.get_id()))
                del boid
            elif boid.get_touched():
                print("{} scored a point by touching a goal".format(boid.get_id()))
                self.flocks.update_flock_score(boid.get_id(), self.boids)
                # temporary goal redeployment
                del self.goals[0]
                self.goals.append(Goal(1, random.randrange(15, self.window_width - 15),
                                       random.randrange(15, self.sim_area_height - 15)))

    # Displays monitoring data at the top of the screen
    def display_monitoring(self, fps,  playtime, num_flocks):
        text = "FPS: {:6.2f}{}PLAYTIME: {:6.2f}{}FLOCKS: {}".format(fps, " " * 5, playtime, " " * 5, num_flocks)
        surface = self.font.render(text, True, (0, 255, 0))
        self.screen.blit(surface, (0, 0))

    # Draws shapes representing goal objects
    def draw_goal(self, pos, radius):
        x = pos[0]
        y = pos[1]
        surface = pygame.Surface((2*radius, 2*radius))
        surface.convert_alpha(surface)
        surface.set_colorkey(BLACK)
        pygame.draw.circle(surface, GOLD, (radius, radius), radius)
        self.surface.blit(surface, (x, y))

    # Draws shapes representing the boid objects
    def draw_boid(self, x, y, height, angle, b_id):
        points = [(int(height // 2), 0),
                  (0, int(height)),
                  (int(height), int(height))]
        surface = pygame.Surface((height, height))
        surface.convert_alpha(surface)
        pygame.draw.polygon(surface, GREEN, points)
        surface.set_colorkey(BLACK)
        txt_surface = pygame.font.SysFont('mono', 10, bold=False).render(str(b_id), True, (0, 255, 0))
        self.surface.blit(pygame.transform.rotozoom(surface, angle, 1), (x - height//2, y - height//2))
        self.surface.blit(txt_surface, (x-2, y + 3 * height // 4))

    def draw_centroid(self, pos, angle=90):
        x = pos[0]
        y = pos[1]
        surface = pygame.Surface((6, 6))
        surface.convert_alpha(surface)
        surface.set_colorkey(BLACK)
        pygame.draw.circle(surface, RED, (3, 3), 3)
        self.surface.blit(surface, (x, y))

    @staticmethod
    def key_movement(presses, run, new_vel, new_dir):
        for event in pygame.event.get():
            # Check for quit
            if event.type == pygame.QUIT or presses[pygame.K_ESCAPE]:
                run = False
        if presses[pygame.K_DOWN]:
            if new_vel <= 0.04:
                new_vel = 0
            else:
                new_vel -= 0.05
        # Adjust heading
        if presses[pygame.K_LEFT]:
            new_dir += 1
        elif presses[pygame.K_RIGHT]:
            new_dir -= 1
        # Adjust velocity
        if presses[pygame.K_UP]:
            if new_vel >= 2:
                new_vel = 2
            else:
                new_vel += 0.05
        return run, new_vel, new_dir

    def display_flock_data(self):
        flock_list = self.flocks.get_flocks()
        flock_thetas = self.flocks.get_thetas()
        flock_goals = self.flocks.get_goal_thetas()
        flock_centroids = self.flocks.get_centroids()
        flock_scores = self.flocks.get_scores()
        monitor = pygame.Surface((self.window_width, self.window_height - self.sim_area_height))
        monitor.blit(
            self.font.render("Number  |     Centroids    |  Direction  |  Goal Direction  |  Score  |  Members", True,
                             GREEN), (11, 0))

        i = 0
        for i in range(len(flock_list)):
            cent = "{:3.2f}, {:3.2f}".format(flock_centroids[i][0], flock_centroids[i][1])
            string = "{0:^6}{1:^5s}{2:^15}{1:^4s}{3:^10.2f}{1:^4s}{4:^14.2f}{1:^5s}{5:^6d}{1:^4s}{6:}"\
                .format(i + 1, "|", cent, flock_thetas[i], flock_goals[i], flock_scores[i], flock_list[i])
            monitor.blit(self.font.render(string, True, GREEN), (12, (i+1) * 13))
            pygame.draw.line(monitor, GREEN, (0, (i+1) * 13), (self.window_width, (i + 1) * 13))
        pygame.draw.line(monitor, GREEN, (0, (i + 2) * 13), (self.window_width, (i + 2) * 13))
        self.screen.blit(monitor, (0, self.sim_area_height+1))

    # Game loop
    def run_loop(self):
        num_flocks = 0
        run = True
        while run:
            ms = self.clock.tick(self.FPS)
            self.playtime += ms / 1000.0
            presses = pygame.key.get_pressed()
            for event in pygame.event.get():
                # Check for quit
                if event.type == pygame.QUIT or presses[pygame.K_ESCAPE]:
                    run = False
            # Use this during testing for key based control
            # TODO: When converting to NN control, new_vel and new_dir will be calculated by each boid's network
            # run, new_vel, new_dir = self.key_movement(presses, run, self.boids[0].get_speed(),
            #                                         self.boids[0].get_direction())
            # Pull up debugger
            if presses[pygame.K_SPACE]:
                import pdb
                pdb.set_trace()

            self.get_collisions()
            move_all_boids(self.boids, self.flocks.get_flocks(), self.goals[0],
                           (self.window_width, self.sim_area_height), self.boid_height)

            for temp_boid in self.boids:
                temp_boid.find_connections(self.boids)
                # TODO: When converting to NN control, new_vel and new_dir will be calculated by each boid's network
                temp_boid.set_goal_dir(self.goals[0].get_position())
                self.draw_boid(temp_boid.get_position()[0], temp_boid.get_position()[1], temp_boid.get_height(),
                               temp_boid.my_dir, temp_boid.get_id())

            self.flocks.form_flocks(self.boids)
            self.flocks.calc_flock_data(self.boids)
            if num_flocks != len(self.flocks.get_flocks()):
                num_flocks = len(self.flocks.get_flocks())
                print("There are {} flocks: {}".format(num_flocks, self.flocks.get_flocks()))


            if len(self.boids) == 0:
                print("This sim was run for {0:.2f} seconds before all boids died".format(self.playtime))
                pygame.quit()
                exit()

            self.display_monitoring(self.clock.get_fps(), self.playtime, len(self.flocks.get_flocks()))
            self.draw_goal(self.goals[0].get_position(), 3)
            for centroid in self.flocks.get_centroids():
                self.draw_centroid(centroid)
            self.display_flock_data()
            # bottom line
            pygame.draw.line(self.background, GREEN, (0, self.sim_area_height),
                             (self.window_width, self.sim_area_height))
            # top line
            pygame.draw.line(self.background, GREEN, (0, 12), (self.window_width, 12))
            pygame.display.flip()
            self.screen.blit(self.background, (0, 0))
        pygame.quit()
        print("This sim was run for {0:.2f} seconds before yeeting".format(self.playtime))
