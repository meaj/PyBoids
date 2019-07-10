"""
Pyboids - SimulationManager
 * A class containing the definitions of the SimulationManager object
 * Copyright (c) 2019 Meaj
"""
import sys
import pygame
import random
from Entities.Entities import Boid, Entity
from Managers.FlockManager import FlockManager
from BoidControllers.GeneticReynoldsControl import move_all_boids_genetic, ReynoldsGeneticAlgorithm, \
    ReynoldsChromosome, SeededReynoldsGeneticAlgorithm
from Managers.DisplayManager import DisplayManager

# Game_state Definitions
RUN = 1
PAUSE = -1
EXIT = 0
EVALUATE = 2

# Format for update is completed_release.goal_number.update_number
VERSION = "5.0.0"

# TODO: Allow user to set number simulation iterations (continuous or N)
# TODO: Allow user to choose which simulation will run on startup instead of by editing code


class SimulationManager:
    def __init__(self, window_width=980, sim_area_height=620, fps=30, boid_radius=7, visual_mode=True):
        # Initialize random and pygame
        random.seed()
        pygame.init()
        # Setup Window
        pygame.display.set_caption("PyBoids Ver. {}".format(VERSION))
        self.boid_radius = boid_radius
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
        if visual_mode:
            self.display_manager = DisplayManager(pygame, (self.window_width, self.window_height),
                                                  sim_area_height, self.boid_radius)
        else:
            self.display_manager = None
        self.flock_manager = FlockManager()

        # Goal Deployment
        for i in range(0, 5):
            self.goal_list.append(Entity(i, random.randrange(boid_radius, self.window_width - boid_radius),
                                         random.randrange(15 + boid_radius, self.sim_area_height - boid_radius)))
        # Boid Deployment
        for i in range(0, 32):
            self.boid_list.append(Boid(i, random.randrange(boid_radius, self.window_width),
                                       random.randrange(15 + boid_radius, self.sim_area_height), boid_radius))

    # This is the fitness function we will use to determine the overall "score" of an iteration of the AIs
    def fitness_function(self, score, survivors=None):
        # If there are no survivors, the bonus is 0
        bonus = 0
        if survivors:
            for boid in survivors:
                bonus += boid.get_score()*2 + self.playtime
        return bonus + score

    # Removes boids that have collided and adds scores
    def get_collisions(self, sim_score):
        for boid in self.boid_list:
            col = boid.get_collisions()
            if col:
                for c in col:
                    if c in self.boid_list:
                        # Account for cost when boids die, reward based on time alive out of full time
                        sim_score -= c.get_cost()
                        sim_score += c.get_live_time()/10
                        sim_score += c.get_score()
                        self.boid_list.remove(c)
                    # print("{} died due to a collision!".format(c.get_id()))
                    del c
                # Account for cost when boids die, reward based on time alive out of full time
                sim_score -= boid.get_cost()
                sim_score += boid.get_live_time()/10
                sim_score += boid.get_score()
                self.boid_list.remove(boid)
                # print("{} died due to a collision!".format(boid.get_id()))
                del boid
            elif boid.get_touched():
                # print("Boid {} scored a point by touching goal {}".format(boid.get_id(), boid.nearest_goal.get_id()))
                sim_score += self.flock_manager.update_flock_score(boid)
                # temporary goal redeployment
                g_id = boid.nearest_goal.get_id()
                self.goal_list[g_id] = Entity(g_id, random.randrange(self.boid_radius,
                                                                     self.window_width - self.boid_radius),
                                              random.randrange(15 + self.boid_radius, self.sim_area_height -
                                                               self.boid_radius))
        return sim_score

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

    def iteration_loop(self, genome, gen_num, iter_num):
        self.playtime = 0
        num_flocks = 0
        game_state = RUN
        sim_score = 0
        fitness = 0
        while game_state != EXIT:
            if self.playtime > 10:
                for boid in self.boid_list:
                    sim_score -= boid.get_cost()
                fitness = self.fitness_function(sim_score, self.boid_list)
                print("Fitness was: {}".format(fitness))
                print("This sim was run for {0:.2f} seconds before finishing".format(self.playtime))
                game_state = EXIT
                continue

            # Get key presses/events
            if self.display_manager:
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
            sim_score = self.get_collisions(sim_score)

            move_all_boids_genetic(self.boid_list, self.flock_manager,
                                   (self.window_width, self.sim_area_height), self.playtime, genome)

            # Flock formation and Flock Data calculations
            self.flock_manager.form_flocks(self.boid_list)
            self.flock_manager.calc_flock_data()
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
            if self.display_manager:
                self.display_manager.draw_screen(self.clock, self.playtime, self.flock_manager,
                                                 self.boid_list, self.goal_list, self.show_centroids, gen_num, iter_num)

        return fitness

    # Controls the Genetic Algorithm
    def run_generations(self, crossover_type=0):
        # Create our algorithm manager with the number of generations from 0 to n,
        # the number of iterations per generation, and the mutation rate denominator
        # genetic_algorithm = ReynoldsGeneticAlgorithm(12, 12, 100)
        genetic_algorithm = SeededReynoldsGeneticAlgorithm(25, 12, 25, [1/7.5, 1, 1/2, 1, 1, 1.1])
        # Loop through each generation
        while genetic_algorithm.generation_number <= genetic_algorithm.max_generation:
            # Loop through each iteration
            idx = 1
            for iteration in genetic_algorithm.get_species_list():
                # Try to ensure that each iteration has the same seed for goal and boid placement
                random.seed(genetic_algorithm.generation_number)
                iteration.set_id(idx)
                print("Generation {} Iteration {}".format(genetic_algorithm.generation_number, iteration.get_id()))
                # Create new population for each generation
                self.boid_list = []
                for i in range(32):
                    self.boid_list.append(Boid(i, random.randrange(15, self.window_width),
                                               random.randrange(15, self.sim_area_height), self.boid_radius))
                fitness = self.iteration_loop(iteration.get_genome(), genetic_algorithm.generation_number, iteration.get_id())
                iteration.update_live_time(self.playtime)
                iteration.update_survivors(len(self.boid_list))
                iteration.update_performance(fitness)
                genetic_algorithm.genetic_history.append(
                    [genetic_algorithm.generation_number, iteration.get_id(),
                     iteration.get_genome(), fitness,
                     iteration.get_livetime(), iteration.get_survivors()])
                idx += 1
            # Find best iteration from each generation
            best_score = -sys.maxsize - 1
            best_iteration = genetic_algorithm.get_species_list()[0]
            for iteration in genetic_algorithm.get_species_list():
                tst = iteration.get_performance()
                if tst > best_score:
                    best_score = tst
                    best_iteration = iteration
            # Store genetic data for best in each generation
            genetic_algorithm.genetic_history_best_performers.append([genetic_algorithm.generation_number,
                                                                      best_iteration.get_id(),
                                                                      best_iteration.get_genome(), best_score,
                                                                      best_iteration.get_livetime(),
                                                                      best_iteration.get_survivors()])
            genetic_algorithm.advance_generation(crossover_type)
        # Determine best performing genome and display it
        best_iteration = genetic_algorithm.get_species_list()[0]
        for iteration in genetic_algorithm.get_species_list():
            if iteration.performance > best_iteration.performance:
                best_iteration = iteration
        print("The best genome evolved after {} generations was {}".format(genetic_algorithm.max_generation,
                                                                           best_iteration.get_genome()))
        best_performers = open("best_performers_method_{}.txt".format(crossover_type), "w")
        best_performers.write("Generation;Iteration;Chromosome;Performance;Live Time;Survivors\n")
        for entry in genetic_algorithm.genetic_history_best_performers:
            best_performers.write("{};{};{};{};{};{}\n".format(entry[0], entry[1], entry[2], entry[3], entry[4], entry[5]))
        best_performers.close()
        gene_history = open("genetic_history_method_{}.txt".format(crossover_type), "w")
        gene_history.write("Generation;Iteration;Chromosome;Performance;Live Time;Survivors\n")
        for entry in genetic_algorithm.genetic_history:
            gene_history.write("{};{};{};{};{};{}\n".format(entry[0], entry[1], entry[2], entry[3], entry[4], entry[5]))
        gene_history.close()

    # Game loop
    def run_loop(self):
        num_flocks = 0
        game_state = RUN
        sim_score = 0
        while game_state != EXIT:
            if self.playtime > 30:
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
            sim_score = self.get_collisions(sim_score)

            # TODO: When converting to NN control, velocity and direction will be calculated by each boid's network
            # Key based control
            # game_state, new_vel, new_dir = self.key_movement(presses, game_state, self.boids[0])
            # Reynolds' control schema, tweaked to work with my boids
            # move_all_boids(self.boid_list, self.flock_manager.get_flocks(), (self.window_width, self.sim_area_height),
            #               self.boid_height)
            # Test control for the genetic algorithm
            # Good test values:
            # .759, .985, .597, .103, -.199, -.555
            # 0.578, 0.7909894024404782, 0.917, 0.20089257410211592, -0.3285011686127677, -0.9371975566340713
            # 1, .25, 1/8, 1/128, 1, 1.1
            # -0.18180729355868763, 0.8241052487791916, 0.7028804320371147, -0.636696685674897, 0.07406855363421672, 0.6906995399561737
            # 5.102145871473336, 0.12225270560240276, -0.4907147143031878, 0.20564065542552967, -0.5995262699036377, -0.8545783665976601
            # -0.4674356703062049, 0.3025268101184942, 0.09942988837552422, -0.5665319558040931, -0.9697534112418487, 0.441
            genome = ReynoldsChromosome(1/7.5, 1, 1/2, 1, 1, 1.1)
            move_all_boids_genetic(self.boid_list, self.flock_manager,
                                   (self.window_width, self.sim_area_height), self.playtime, genome)

            # Flock formation and Flock Data calculations
            self.flock_manager.form_flocks(self.boid_list)
            self.flock_manager.calc_flock_data()
            if num_flocks != len(self.flock_manager.get_flocks()):
                num_flocks = len(self.flock_manager.get_flocks())
                print("There are {} flocks".format(num_flocks))

            # Exits simulation when all boids are dead
            if len(self.boid_list) == 0:
                print("Fitness was: {}".format(self.fitness_function(sim_score)))
                print("This sim was run for {0:.2f} seconds before all boids died".format(self.playtime))
                pygame.quit()
                exit()

            # Call our display functions
            if self.display_manager:
                self.display_manager.draw_screen(self.clock, self.playtime, self.flock_manager,
                                                 self.boid_list, self.goal_list, self.show_centroids)

        print("Fitness was: {}".format(self.fitness_function(sim_score, self.boid_list)))
        pygame.quit()
        print("This sim was run for {0:.2f} seconds before yeeting".format(self.playtime))
