"""
Pyboids - SimulationManager
 * A class containing the definitions of the SimulationManager object
 * Copyright (c) 2019 Meaj
"""
import pygame
import random
from Entities.Entities import Boid, Entity
from Managers.FlockManager import FlockManager
from BoidControllers.ReynoldsControl import move_all_boids
from BoidControllers.GeneticReynoldsControl import move_all_boids_genetic, ReynoldsGeneticAlgorithm, ReynoldsChromosome
from Managers.DisplayManager import DisplayManager

# Game_state Definitions
RUN = 1
PAUSE = -1
EXIT = 0
EVALUATE = 2

# Format for update is completed_release.goal_number.update_number
VERSION = "0.4.1"

# TODO: Allow user to set number simulation iterations (continuous or N)
# TODO: Allow user to choose which simulation will run on startup instead of by editing code


class SimulationManager:
    def __init__(self, window_width=980, sim_area_height=620, fps=30, boid_height=10):
        # Initialize random and pygame
        random.seed()
        pygame.init()
        # Setup Window
        pygame.display.set_caption("PyBoids Ver. {}".format(VERSION))
        self.boid_height = boid_height
        self.window_width = window_width  # width of the window and simulation area
        self.sim_area_height = sim_area_height  # height of the simulation area
        self.window_height = sim_area_height + 15 * 10

        # Timing and monitoring data
        self.clock = pygame.time.Clock()
        self.FPS = fps
        self.playtime = 0.0
        self.show_centroids = False

        # Entity list declaration
        self.goal_list = []
        self.boid_list = []

        # Manager creation
        self.display_manager = DisplayManager(pygame, (self.window_width, self.window_height), sim_area_height)
        self.flock_manager = FlockManager()

        # Goal Deployment
        for i in range(0, 5):
            self.goal_list.append(Entity(i, random.randrange(15, self.window_width - 15),
                                         random.randrange(15, self.sim_area_height - 15)))
        # Boid Deployment
        for i in range(0, 32):
            self.boid_list.append(Boid(i, random.randrange(15, self.window_width),
                                       random.randrange(15, self.sim_area_height), boid_height))

    # This is the fitness function we will use to determine the overall "score" of an iteration of the AIs
    @staticmethod
    def fitness_function(score, survivors=None):
        total = 0
        if survivors:
            for boid in survivors:
                total += boid.get_score()
        return total + score / 32

    # Removes boids that have collided and adds scores
    def get_collisions(self, sim_score):
        for boid in self.boid_list:
            col = boid.get_collisions()
            if col:
                for c in col:
                    if c in self.boid_list:
                        self.boid_list.remove(c)
                    # print("{} died due to a collision!".format(c.get_id()))
                    del c
                self.boid_list.remove(boid)
                # print("{} died due to a collision!".format(boid.get_id()))
                del boid
            elif boid.get_touched():
                # print("Boid {} scored a point by touching goal {}".format(boid.get_id(), boid.nearest_goal.get_id()))
                sim_score += self.flock_manager.update_flock_score(boid.get_id(), self.boid_list)
                # temporary goal redeployment
                g_id = boid.nearest_goal.get_id()
                self.goal_list[g_id] = Entity(g_id, random.randrange(15, self.window_width - 15),
                                              random.randrange(15, self.sim_area_height - 15))

    # Check for keyboard input
    def key_events(self, game_state):
        presses = pygame.key.get_pressed()
        # Exit game with escape or by clicking the close button
        for event in pygame.event.get():
            if event.type == pygame.QUIT or presses[pygame.K_ESCAPE]:
                print("game_state set to EXIT")
                game_state = EXIT
            # Pauses game with space
            if presses[pygame.K_SPACE]:
                game_state *= PAUSE
                if game_state == PAUSE:
                    print("game_state set to PAUSE")
                else:
                    print("game_state set to RUN")
            # Toggle centroid data on or off
            if presses[pygame.K_TAB]:
                self.show_centroids = not self.show_centroids
        # Pull up debugger with `
        if presses[pygame.K_BACKQUOTE]:
            import pdb
            pdb.set_trace()

        return game_state

    @staticmethod
    # TODO: This needs to be updated to work with new vectors
    # Default keyboard controls
    def key_movement(presses, run, boid):
        new_vel = boid.get_speed()
        new_dir = boid.get_direction()
        for event in pygame.event.get():
            # Check for quit
            if event.type == pygame.QUIT or presses[pygame.K_ESCAPE]:
                run = EXIT
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

    def iteration_loop(self, genome):
        self.playtime = 0
        num_flocks = 0
        game_state = RUN
        sim_score = 0
        fitness = 0
        while game_state != EXIT:
            if self.playtime > 300:
                fitness = self.fitness_function(sim_score, self.boid_list)
                print("Fitness was: {}".format(fitness))
                print("This sim was run for {0:.2f} seconds before finishing".format(self.playtime))
                game_state = EXIT
                continue

            # Get key presses/events
            game_state = self.key_events(game_state)

            # Timing calculations
            if game_state == PAUSE:
                self.clock.tick_busy_loop()
                continue
            self.playtime += self.clock.tick(self.FPS) / 1000.0

            # Setup connections and look for goals
            for temp_boid in self.boid_list:
                temp_boid.find_connections(self.boid_list)
                temp_boid.find_nearest_goal(self.goal_list)

            # Look for all collisions and handle accordingly
            self.get_collisions(sim_score)

            move_all_boids_genetic(self.boid_list, self.flock_manager.get_flocks(),
                                   (self.window_width, self.sim_area_height), self.boid_height, genome)

            # Flock formation and Flock Data calculations
            self.flock_manager.form_flocks(self.boid_list)
            self.flock_manager.calc_flock_data(self.boid_list)
            if num_flocks != len(self.flock_manager.get_flocks()):
                num_flocks = len(self.flock_manager.get_flocks())

            # Exits simulation when all boids are dead
            if len(self.boid_list) == 0:
                fitness = self.fitness_function(sim_score, self.boid_list)
                print("Fitness was: {}".format(fitness))
                print("This sim was run for {0:.2f} seconds before all boids died".format(self.playtime))
                game_state = EXIT
                continue

            # Call our display functions
            self.display_manager.draw_screen(self.clock, self.playtime, self.flock_manager,
                                             self.boid_list, self.goal_list, self.show_centroids)
        return fitness

    # Controls the Genetic Algorithm
    def run_generations(self):
        # Create our algorithm manager with the number of generations from 0 to n,
        # the number of iterations per generation, and the mutation rate
        genetic_algorithm = ReynoldsGeneticAlgorithm(24, 12, 6)
        # Loop through each generation
        while genetic_algorithm.cur_generation <= genetic_algorithm.max_generation:
            # Loop through each iteration
            for iteration in genetic_algorithm.get_iteration_list():
                print("Generation {} Iteration {}".format(genetic_algorithm.cur_generation, iteration.get_id()))
                # Create new population for each generation
                self.boid_list = []
                for i in range(32):
                    self.boid_list.append(Boid(i, random.randrange(15, self.window_width),
                                               random.randrange(15, self.sim_area_height), self.boid_height))
                fitness = self.iteration_loop(iteration.get_genome())
                iteration.update_performance(fitness)
                # Store genetic data (currently unused but I want more monitoring
                genetic_algorithm.genetic_history.append([genetic_algorithm.cur_generation, iteration, fitness])
            genetic_algorithm.advance_generation()
        # Determine best performing genome and display it
        best = genetic_algorithm.iteration_list[0]
        for iteration in genetic_algorithm.get_iteration_list():
            if iteration.performance > best.performance:
                best = iteration
        print("The best genome evolved after {} generations was {}".format(genetic_algorithm.max_generation,
                                                                           best.get_genome()))

    # Game loop
    def run_loop(self):
        num_flocks = 0
        game_state = RUN
        sim_score = 0
        while game_state != EXIT:
            if self.playtime > 20:
                break

            # Get key presses/events
            game_state = self.key_events(game_state)

            # Timing calculations
            if game_state == PAUSE:
                self.clock.tick_busy_loop()
                continue
            self.playtime += self.clock.tick(self.FPS) / 1000.0

            # Setup connections and look for goals
            for temp_boid in self.boid_list:
                temp_boid.find_connections(self.boid_list)
                temp_boid.find_nearest_goal(self.goal_list)

            # Look for all collisions and handle accordingly
            self.get_collisions(sim_score)

            # TODO: When converting to NN control, velocity and direction will be calculated by each boid's network
            # Key based control
            # game_state, new_vel, new_dir = self.key_movement(presses, game_state, self.boids[0])
            # Reynolds' control schema, tweaked to work with my boids
            # move_all_boids(self.boid_list, self.flock_manager.get_flocks(), (self.window_width, self.sim_area_height),
            #               self.boid_height)
            # Test control for the genetic algorithm
            genome = ReynoldsChromosome(1, 1/4, 1/8, 1/128, 1, 1.1)
            move_all_boids_genetic(self.boid_list, self.flock_manager.get_flocks(),
                                   (self.window_width, self.sim_area_height), self.boid_height, genome)

            # Flock formation and Flock Data calculations
            self.flock_manager.form_flocks(self.boid_list)
            self.flock_manager.calc_flock_data(self.boid_list)
            if num_flocks != len(self.flock_manager.get_flocks()):
                num_flocks = len(self.flock_manager.get_flocks())
                print("There are {} flocks: {}".format(num_flocks, self.flock_manager.get_flocks()))

            # Exits simulation when all boids are dead
            if len(self.boid_list) == 0:
                print("Fitness was: {}".format(self.fitness_function(sim_score)))
                print("This sim was run for {0:.2f} seconds before all boids died".format(self.playtime))
                pygame.quit()
                exit()

            # Call our display functions
            self.display_manager.draw_screen(self.clock, self.playtime, self.flock_manager,
                                             self.boid_list, self.goal_list, self.show_centroids)

        print("Fitness was: {}".format(self.fitness_function(sim_score, self.boid_list)))
        pygame.quit()
        print("This sim was run for {0:.2f} seconds before yeeting".format(self.playtime))
