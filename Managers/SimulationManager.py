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
from BoidControllers.GeneticReynoldsControl import move_all_boids_genetic, \
    ReynoldsChromosome, SeededReynoldsGeneticAlgorithm
from Managers.DisplayManager import DisplayManager

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

class SimulationManager:
    def __init__(self, window_width=980, sim_area_height=620, fps=30, boid_radius=7,
                 visual_mode=True, flock_monitoring=False, version="0.0.0"):
        # Initialize random and pygame
        random.seed()
        pygame.init()
        # Setup Window
        pygame.display.set_caption("PyBoids Ver. {}".format(version))
        self.boid_radius = boid_radius
        self.window_width = window_width  # width of the window and simulation area
        self.sim_area_height = sim_area_height  # height of the simulation area
        self.window_height = sim_area_height + 15 * 10
        self.version = version

        # Timing and monitoring data
        self.clock = pygame.time.Clock()
        self.FPS = fps
        self.playtime = 0.0
        self.show_centroids = False
        self.end_time = 0

        # Entity list declaration
        self.goal_list = []
        self.boid_list = []
        self.max_pop = 0

        # Manager creation
        if visual_mode:
            if flock_monitoring:
                self.display_manager = DisplayManager(pygame, (self.window_width, self.window_height),
                                                      sim_area_height, self.boid_radius)
            else:
                self.display_manager = DisplayManager(pygame, (self.window_width, sim_area_height),
                                                      sim_area_height, self.boid_radius)
        else:
            self.display_manager = None
        self.flock_manager = FlockManager()
        self.game_state = LOADED

    def set_end_time(self, time):
        self.end_time = time

    def set_max_pop(self, val):
        self.max_pop = val

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
    def listen_for_keys(self):
        presses = pygame.key.get_pressed()
        # Exit game with escape or by clicking the close button
        for event in pygame.event.get():
            if event.type == pygame.QUIT or presses[pygame.K_ESCAPE]:
                print("game_state set to EXIT")
                self.game_state = EXIT
            # Pauses game with space
            if presses[pygame.K_SPACE]:
                if self.game_state == RUN_SIMULATION:
                    self.game_state = PAUSE_SIMULATION
                    print("game_state set to PAUSE")
                elif self.game_state == PAUSE_SIMULATION:
                    self.game_state = RUN_SIMULATION
                    print("game_state set to RUN")
            # Toggle centroid data on or off
            if presses[pygame.K_TAB] and self.game_state == RUN_SIMULATION:
                self.show_centroids = not self.show_centroids
            if self.game_state == NEW_SIM_MENU or self.game_state == LOAD_SIM_MENU:
                # Check for number, period, or minus key then add appropriate value to string
                continue
        # Pull up debugger with `
        if presses[pygame.K_BACKQUOTE]:
            import pdb
            pdb.set_trace()

    # Goal Deployment
    def deploy_goals(self, goal_number):
        for i in range(0, goal_number):
            self.goal_list.append(Entity(i, random.randrange(self.boid_radius, self.window_width - self.boid_radius),
                                         random.randrange(15 + self.boid_radius,
                                                          self.sim_area_height - self.boid_radius)))

    # Boid Deployment
    def deploy_boids(self, boid_number):
        for i in range(0, boid_number):
            self.boid_list.append(Boid(i, random.randrange(self.boid_radius, self.window_width),
                                       random.randrange(15 + self.boid_radius, self.sim_area_height), self.boid_radius))

    def species_simulation(self, genome, gen_num, iter_num):
        self.playtime = 0
        num_flocks = 0
        self.game_state = RUN_SIMULATION
        sim_score = 0
        fitness = 0
        while self.game_state != EXIT and self.game_state != END_SIMULATION:
            if self.playtime > self.end_time:
                for boid in self.boid_list:
                    sim_score -= boid.get_cost()
                fitness = self.fitness_function(sim_score, self.boid_list)
                print("Fitness was: {}".format(fitness))
                print("This sim was run for {0:.2f} seconds before finishing".format(self.playtime))
                self.game_state = END_SIMULATION
                continue

            # Get key presses/events
            if self.display_manager:
                self.listen_for_keys()

            # Timing calculations
            if self.game_state == PAUSE_SIMULATION:
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
            self.flock_manager.update_all_flock_data()
            if num_flocks != len(self.flock_manager.get_flocks()):
                num_flocks = len(self.flock_manager.get_flocks())

            # Exits simulation when all boids are dead
            if len(self.boid_list) == 0:
                fitness = self.fitness_function(sim_score, self.boid_list)
                print("Fitness was: {}".format(fitness))
                print("This sim was run for {0:.2f} seconds before all boids died".format(self.playtime))
                self.game_state = END_SIMULATION
                continue

            # Call our display functions
            if self.display_manager:
                self.display_manager.draw_simulation_screen(self.clock, self.playtime, self.flock_manager,
                                                            self.boid_list, self.goal_list, self.show_centroids,
                                                            gen_num, iter_num)

        return fitness

    # Controls the simulation
    def run_simulation(self, crossover_type=0, generations=25, species=12, mutation_rate=25,
                       genome=None):
        # the number of iterations per generation, the mutation rate denominator, and our seed
        if not genome:
            genome = [1 / 7.5, 1, 1 / 2, 1, 1, 1.1]
        genetic_algorithm = SeededReynoldsGeneticAlgorithm(generations, species, mutation_rate, genome)
        if self.end_time == 0:
            self.end_time = 15
        if self.max_pop == 0:
            self.max_pop = 12
        # Loop through each generation
        while genetic_algorithm.generation_number < genetic_algorithm.max_generation and self.game_state != EXIT:
            # Loop through each species
            idx = 1
            for species in genetic_algorithm.get_species_list():
                if self.game_state == EXIT:
                    break
                # Try to ensure that each species has the same seed for goal and boid placement
                random.seed(genetic_algorithm.generation_number)
                species.set_id(idx)
                print("Generation {} Species {}".format(genetic_algorithm.generation_number, species.get_id()))
                # Create new population for each generation
                self.boid_list = []
                self.goal_list = []
                self.deploy_boids(self.max_pop)
                self.deploy_goals(5)
                fitness = self.species_simulation(species.get_genome(), genetic_algorithm.generation_number,
                                                  species.get_id())
                species.update_live_time(self.playtime)
                species.update_survivors(len(self.boid_list))
                species.update_performance(fitness)
                genetic_algorithm.genetic_history.append(
                    [genetic_algorithm.generation_number, species.get_id(),
                     species.get_genome(), fitness,
                     species.get_livetime(), species.get_survivors()])
                idx += 1
            # Find best species from each generation
            best_score = -sys.maxsize - 1
            best_species = genetic_algorithm.get_species_list()[0]
            for species in genetic_algorithm.get_species_list():
                tst = species.get_performance()
                if tst > best_score:
                    best_score = tst
                    best_species = species
            # Store genetic data for best in each generation
            genetic_algorithm.genetic_history_best_performers.append([genetic_algorithm.generation_number,
                                                                      best_species.get_id(),
                                                                      best_species.get_genome(), best_score,
                                                                      best_species.get_livetime(),
                                                                      best_species.get_survivors()])

            genetic_algorithm.advance_generation(crossover_type)
        # Determine best performing genome and display it
        best_species = genetic_algorithm.get_species_list()[0]
        for species in genetic_algorithm.get_species_list():
            if species.performance > best_species.performance:
                best_species = species
        print("The best genome evolved after {} generations was {}".format(genetic_algorithm.max_generation,
                                                                           best_species.get_genome()))
        best_performers = open("best_performers_method_{}.txt".format(crossover_type), "w")
        best_performers.write("Generation;Species;Chromosome;Performance;Live Time;Survivors\n")
        for entry in genetic_algorithm.genetic_history_best_performers:
            best_performers.write("{};{};{};{};{};{}\n".format(entry[0], entry[1], entry[2], entry[3], entry[4],
                                                               entry[5]))
        best_performers.close()
        gene_history = open("genetic_history_method_{}.txt".format(crossover_type), "w")
        gene_history.write("Generation;Species;Chromosome;Performance;Live Time;Survivors\n")
        for entry in genetic_algorithm.genetic_history:
            gene_history.write("{};{};{};{};{};{}\n".format(entry[0], entry[1], entry[2], entry[3], entry[4], entry[5]))
        gene_history.close()

    # Game loop
    def run_loop(self, seed):
        num_flocks = 0
        self.game_state = RUN_SIMULATION
        sim_score = 0
        self.deploy_boids(self.max_pop)
        self.deploy_goals(5)

        while self.game_state != EXIT:
            if self.playtime > self.end_time:
                break

            # Get key presses/events
            self.listen_for_keys()

            # Timing calculations
            if self.game_state == PAUSE_SIMULATION:
                self.clock.tick_busy_loop()
                continue
            self.playtime += self.clock.tick(self.FPS) / 1000.0

            # Setup connections and look for goals
            for temp_boid in self.boid_list:
                temp_boid.find_connections(self.boid_list)
                temp_boid.find_nearest_goal(self.goal_list)

            # Look for all collisions and handle accordingly
            sim_score = self.get_collisions(sim_score)

            genome = ReynoldsChromosome(seed[0], seed[1], seed[2], seed[3], seed[4], seed[5])
            move_all_boids_genetic(self.boid_list, self.flock_manager,
                                   (self.window_width, self.sim_area_height), self.playtime, genome)

            # Flock formation and Flock Data calculations
            self.flock_manager.form_flocks(self.boid_list)
            self.flock_manager.update_all_flock_data()
            if num_flocks != len(self.flock_manager.get_flocks()):
                num_flocks = len(self.flock_manager.get_flocks())
                print("There are {} flocks".format(num_flocks))

            # Exits simulation when all boids are dead
            if len(self.boid_list) == 0:
                self.game_state = EXIT
                print("Fitness was: {}".format(self.fitness_function(sim_score)))
                print("This sim was run for {0:.2f} seconds before all boids died".format(self.playtime))
                pygame.quit()
                exit()

            # Call our display functions
            if self.display_manager:
                self.display_manager.draw_simulation_screen(self.clock, self.playtime, self.flock_manager,
                                                            self.boid_list, self.goal_list, self.show_centroids)

        print("Fitness was: {}".format(self.fitness_function(sim_score, self.boid_list)))
        pygame.quit()
        print("This sim was run for {0:.2f} seconds before yeeting".format(self.playtime))

    # Runs the start menu
    def start_menu(self):
        self.game_state = MAIN_MENU
        while self.game_state != EXIT:
            self.listen_for_keys()

            self.display_manager.draw_start_screen(version=self.version, function_1=self.simulation_setup_menu,
                                                   function_2=self.simulation_load_menu,
                                                   function_3=self.simulation_setup_menu)
        print("Program exited from start menu")
        pygame.quit()
        exit()

    # Runs the menu for setting up a new simulation
    def simulation_setup_menu(self):
        self.game_state = NEW_SIM_MENU
        while self.game_state != EXIT:
            self.listen_for_keys()

            self.display_manager.draw_simulation_settings_screen(self.run_simulation, self.start_menu)
        print("Program exited from setup menu")
        pygame.quit()
        exit()

    # Runs the menu for loading a simulation file or manually input species
    def simulation_load_menu(self):
        self.game_state = LOAD_SIM_MENU
        while self.game_state != EXIT:
            self.listen_for_keys()
            self.display_manager.draw_load_simulation_screen(self.run_simulation, self.start_menu)
        print("Program exited from load menu")
        pygame.quit()
        exit()
