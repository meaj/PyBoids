"""
Pyboids - SimulationManager
 * A class containing the definitions of the SimulationManager object
 * Copyright (c) 2019 Meaj
"""
import sys
import random
from Constants import *
from Entities.Entities import Boid, Goal
from Entities.MenuEntities import Button, InputBox
from Managers.FlockManager import FlockManager
from BoidControllers.GeneticReynoldsControl import move_all_boids_genetic, \
    ReynoldsChromosome, SeededReynoldsGeneticAlgorithm


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
            if not flock_monitoring:
                self.window_height = self.sim_area_height
            self.screen = pygame.display.set_mode((self.window_width, self.sim_area_height), pygame.DOUBLEBUF)
            # Setup Background
            self.background = pygame.Surface(self.screen.get_size()).convert()
            self.background.fill(BLACK)

            # Boid image setup
            self.boid_image = pygame.image.load("Sprites/boid_sprite.png")
            self.boid_image.convert_alpha(self.boid_image)
            pygame.display.set_icon(self.boid_image)
            self.boid_image = pygame.transform.smoothscale(self.boid_image, (boid_radius * 2, boid_radius * 2))

            # Font setup
            self.normal_font = pygame.font.SysFont('courier new', 12, bold=True)
            self.large_font = pygame.font.SysFont('courier new', 48, bold=True)

        self.visual_mode = visual_mode
        self.flock_monitoring = flock_monitoring

        self.flock_manager = FlockManager()

        # Button creation
        self.main_menu_button = Button("Main Menu", -1000, -1000, 120, 60, self.start_menu)
        self.load_menu_button = Button("Load Sim", -1000, -1000, 120, 60, self.simulation_load_menu)
        self.setup_menu_button = Button("Setup Sim", -1000, -1000, 120, 60, self.simulation_setup_menu)
        self.start_sim_button = Button("Begin", -1000, -1000, 120, 60, self.run_simulation)
        self.load_sim_button = Button("Begin", -1000, -1000, 120, 60, self.run_loop)

        # TextBox creation
        self.population_input = InputBox("", "Population Size", -1000, -1000, 60, 14)

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
                self.goal_list[g_id] = Goal(g_id, random.randrange(self.boid_radius,
                                                                   self.window_width - self.boid_radius),
                                            random.randrange(15 + self.boid_radius, self.sim_area_height -
                                                             self.boid_radius), 3)
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
            self.goal_list.append(Goal(i, random.randrange(self.boid_radius, self.window_width - self.boid_radius),
                                  random.randrange(15 + self.boid_radius,
                                  self.sim_area_height - self.boid_radius), 3))

    # Boid Deployment
    def deploy_boids(self, boid_number):
        for i in range(0, boid_number):
            self.boid_list.append(Boid(i, random.randrange(self.boid_radius, self.window_width),
                                       random.randrange(15 + self.boid_radius, self.sim_area_height), self.boid_radius))

    def display_flock_data(self):
        flock_list = self.flock_manager.get_flocks()
        monitor = pygame.Surface((self.window_width, self.window_height - self.sim_area_height))
        monitor.blit(
            self.normal_font.render("Number  |     Centroids    |  Direction  |  Goal Direction  |  Score  |  Members",
                                    True, GREEN), (11, 0))

        for idx, flock in enumerate(flock_list):
            members = []
            for member in flock.flock_members:
                members.append(member.get_id())
            cent = "{:3.2f}, {:3.2f}".format(flock.flock_centroid.x, flock.flock_centroid.y)
            string = "{0:^6}{1:^5s}{2:^15}{1:^4s}{3:^10.2f}{1:^4s}{4:^14.2f}{1:^5s}{5:^6d}{1:^4s}{6:}".\
                format(idx + 1, "|", cent, flock.flock_velocity.argument(),
                       flock.flock_goal_dir, flock.flock_score, members)
            monitor.blit(self.normal_font.render(string, True, GREEN), (12, (idx + 1) * 13))
            pygame.draw.line(monitor, GREEN, (0, (idx+1) * 13), (self.window_width, (idx + 1) * 13))
        pygame.draw.line(monitor, GREEN, (0, (len(flock_list) + 1) * 13), (self.window_width,
                                                                           (len(flock_list) + 1) * 13))
        self.screen.blit(monitor, (0, self.sim_area_height+1))

    # Displays monitoring data at the top of the screen
    # clock.get_fps(), playtime, len(flocks.get_flocks()), gen_num, iter_num
    def display_simulation_overview(self, gen_num, species_num):
        text = "FPS: {:6.2f}{}PLAYTIME: {:6.2f}{}FLOCKS: {}{}GENERATION: {}{}SPECIES: {}".\
            format(self.clock.get_fps(), " " * 5, self.playtime, " " * 5, len(self.flock_manager.flock_list), " " * 5,
                   gen_num, " " * 5, species_num)
        surface = self.normal_font.render(text, True, (0, 255, 0))
        self.screen.blit(surface, (0, 0))

    def draw_simulation_screen(self, gen_num=0, iter_num=0):
        # Clear the screen
        self.background.fill(BLACK)
        # Draw the monitoring at the top of the screen
        self.display_simulation_overview(gen_num, iter_num)
        # Draw objects in the simulation area
        for boid in self.boid_list:
            boid.display_boid(self.boid_image, self.screen, self.background, self.show_centroids)
        for goal in self.goal_list:
            goal.display_goal(self.screen)
        if self.show_centroids:
            # Draw flock centroids and velocity vectors
            for flock in self.flock_manager.flock_list:
                flock.display_flock_centroid_vectors(self.screen, self.background)
        # Draw the flock data at the bottom
        self.display_flock_data()
        # Draw bottom line for sim area
        pygame.draw.line(self.background, GREEN, (0, self.sim_area_height), (self.window_width, self.sim_area_height))
        # Draw top line for sim area
        pygame.draw.line(self.background, GREEN, (0, 12), (self.window_width, 12))
        pygame.display.flip()  # (╯°□°)╯︵ ┻━┻
        self.screen.blit(self.background, (0, 0))

    def species_simulation(self, genome, gen_num, species_number):
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
                print("Species {0:} ran for {1:.2f} seconds before being stopped".format(species_number, self.playtime))
                self.game_state = END_SIMULATION
                continue

            # Get key presses/events
            if self.visual_mode:
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
                print("Species {0:} ran for {0:.2f} seconds before all boids died".
                      format(species_number, self.playtime))
                self.game_state = END_SIMULATION
                continue

            # Call our display functions
            if self.visual_mode:
                self.draw_simulation_screen(gen_num, species_number)

        return fitness

    # Controls the simulation
    def run_simulation(self, crossover_type=6, generations=25, species=24, mutation_rate=20,
                       genome=None):
        # the number of iterations per generation, the mutation rate denominator, and our seed
        if not genome:
            genome = [random.uniform(-1, 1), random.uniform(-1, 1),  random.uniform(-1, 1), random.uniform(-1, 1),
                      random.uniform(-1, 1), random.uniform(-1, 1)]
        genetic_algorithm = SeededReynoldsGeneticAlgorithm(generations, species, mutation_rate, genome)
        if self.end_time == 0:
            self.end_time = 10
        if self.max_pop == 0:
            self.max_pop = 32
        # Loop through each generation
        while genetic_algorithm.generation_number < genetic_algorithm.max_generation and self.game_state != EXIT:
            # Loop through each species
            for idx, species in enumerate(genetic_algorithm.get_species_list()):
                if self.game_state == EXIT:
                    break
                self.playtime = 0
                # Try to ensure that each species has the same seed for goal and boid placement
                random.seed(genetic_algorithm.generation_number)
                species.set_id(idx+1)
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
    def run_loop(self):
        self.playtime = 0
        num_flocks = 0
        self.game_state = RUN_SIMULATION
        sim_score = 0

        self.deploy_goals(5)
        if self.end_time == 0:
            self.end_time = 100
        if self.max_pop == 0:
            self.max_pop = 32
        self.deploy_boids(self.max_pop)
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

            genome = ReynoldsChromosome(-0.421513923207689, 0.544929141246922, -0.05488413118915939, 0.8147349755792612, 0.359, -0.673)
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
            if self.visual_mode:
                self.draw_simulation_screen(1, 1)

        print("Fitness was: {}".format(self.fitness_function(sim_score, self.boid_list)))
        pygame.quit()
        print("This sim was run for {0:.2f} seconds before yeeting".format(self.playtime))
        self.game_state = EXIT
        exit()

    # Runs the start menu
    def start_menu(self):
        self.game_state = MAIN_MENU
        self.load_menu_button.set_pos(self.window_width / 2 - 60, 5 * self.window_height / 8)
        self.setup_menu_button.set_pos(self.window_width / 2 - 60, 1 * self.window_height / 2)
        while self.game_state != EXIT:
            self.listen_for_keys()

            self.background.fill(BLACK)
            self.screen.blit(self.background, (0, 0))
            title = "PyBoids"
            tag_line = "An Experimental AI Simulation"
            version_data = "Version {}".format(self.version)

            title_surf, title_rect = text_setup(title, self.large_font)
            title_rect.center = (self.window_width / 2, 3 * self.window_height / 16)

            tag_surf, tag_rect = text_setup(tag_line, self.normal_font)
            tag_rect.center = (self.window_width / 2, (3 * self.window_height / 16) + 32)

            vers_surf, vers_rect = text_setup(version_data, self.normal_font)
            vers_rect.topleft = (6, self.window_height - 12)

            self.screen.blit(title_surf, title_rect)
            self.screen.blit(tag_surf, tag_rect)
            self.screen.blit(vers_surf, vers_rect)

            self.load_menu_button.check_click()
            self.load_menu_button.draw_button(self.screen)
            self.setup_menu_button.check_click()
            self.setup_menu_button.draw_button(self.screen)
            # self.menu_button("Help ?", self.window_width / 2 - 60, 3 * self.window_height / 4, 120, 60, LIGHT_GREY,
            # GREY, function_3)

            pygame.display.update()
        print("Program exited from start menu")
        pygame.quit()
        exit()

    # Runs the menu for setting up a new simulation
    def simulation_setup_menu(self):
        self.game_state = NEW_SIM_MENU
        self.start_sim_button.set_pos(self.window_width / 3 - 60, 3 * self.window_height / 4)
        self.main_menu_button.set_pos(2 * self.window_width / 3 - 60, 3 * self.window_height / 4)
        self.population_input.set_pos(self.window_width/3, 200)
        pop_string = ""
        self.population_input.in_text = pop_string
        while self.game_state != EXIT:
            self.listen_for_keys()

            self.background.fill(BLACK)
            self.screen.blit(self.background, (0, 0))

            #self.population_input.draw_box(self.screen)
            #self.population_input.handle_event()

            self.main_menu_button.check_click()
            self.main_menu_button.draw_button(self.screen)
            self.start_sim_button.check_click()
            self.start_sim_button.draw_button(self.screen)

            title = "SETUP IN DEVELOPMENT: PRESS BEGIN"
            title_surf, title_rect = text_setup(title, self.large_font)
            title_rect.center = (self.window_width / 2, 3 * self.window_height / 16)


            self.screen.blit(title_surf, title_rect)
            pygame.display.update()
        print("Program exited from setup menu")
        pygame.quit()
        exit()

    # Runs the menu for loading a simulation file or manually input species
    def simulation_load_menu(self):
        self.game_state = LOAD_SIM_MENU
        self.main_menu_button.set_pos(2 * self.window_width / 3 - 60, 3 * self.window_height / 4)
        self.load_sim_button.set_pos(self.window_width / 3 - 60, 3 * self.window_height / 4)
        while self.game_state != EXIT:
            self.listen_for_keys()
            self.background.fill(BLACK)
            self.screen.blit(self.background, (0, 0))
            title = "Load Simulation: Coming Soon"
            title_surf, title_rect = text_setup(title, self.large_font)
            title_rect.center = (self.window_width / 2, 3 * self.window_height / 16)

            self.main_menu_button.check_click()
            self.main_menu_button.draw_button(self.screen)
            self.load_sim_button.check_click()
            self.load_sim_button.draw_button(self.screen)

            self.screen.blit(title_surf, title_rect)
            pygame.display.update()

        print("Program exited from load menu")
        pygame.quit()
        exit()
