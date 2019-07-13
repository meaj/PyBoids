"""
Pyboids
 * An exploration of the ability of various AIs to develop flocking behavior
 * Copyright (c) 2019 Meaj
"""

from Managers.SimulationManager import SimulationManager
# best so far:
# -0.2726218754477409, 0.22531065494572736, 0.012347193295672765, 0.4056808036681063, 0.5633023671766649, 0.768

# Format for update is completed_release.goal_number.update_number
VERSION = "0.5.0"

def main():
    manager = SimulationManager(visual_mode=True, version=VERSION)
    manager.start_menu()




    # Prompt user for simulation type
    print("Welcome to PyBoids V{}\nThe following options are available:".format(VERSION))
    print("\t1: Display Single Species\n\t2: New Breeding Simulation")
    sim_type = int(input("Enter the number of the option you wish to run: "))
    pop_size = int(input("Enter the number of boids to simulate at once: "))
    if sim_type == 1:
        end_time = float(input("Enter the number of seconds you want the simulation to run for: "))
        cohesion = float(input("Enter the value for the cohesion gene: "))
        separation = float(input("Enter the value for the separation gene: "))
        alignment = float(input("Enter the value for the alignment gene: "))
        goal_seek = float(input("Enter the value for the goal seeking gene: "))
        wall_avoid = float(input("Enter the value for the wall avoidance gene: "))
        divergence = float(input("Enter the value for the divergence gene: "))
        # Create gene from user inputs
        genome = [cohesion, separation, alignment, goal_seek, wall_avoid, divergence]

        manager = SimulationManager(visual_mode=True)
        manager.run_loop(genome)
        del manager

    elif sim_type == 2:
        max_gen = int(input("Enter the number of generations to test: "))
        max_species = int(input("Enter number of species to evaluate each generation: "))
        end_time = float(input("Enter the number of seconds you want each species to run for: "))
        mutation_rate = int(input("Enter the denominator for the mutation rate for new genes (1/n): "))
        want_seed = input("Do you want to seed the genetic algorithm? (Y/N)")
        if want_seed.lower() == "y":
            cohesion = float(input("Enter the value for the cohesion gene: "))
            separation = float(input("Enter the value for the separation gene: "))
            alignment = float(input("Enter the value for the alignment gene: "))
            goal_seek = float(input("Enter the value for the goal seeking gene: "))
            wall_avoid = float(input("Enter the value for the wall avoidance gene: "))
            divergence = float(input("Enter the value for the divergence gene: "))
            # Create seed from user inputs
            seed = [cohesion, separation, alignment, goal_seek, wall_avoid, divergence]
        else:
            seed = [1 / 7.5, 1, 1 / 2, 1, 1, 1.1]

        for i in range(0, 7):
            manager = SimulationManager(visual_mode=True)
            print("Running simulation with crossover type {}".format(i))
            manager.run_simulation(i, max_gen, max_species, mutation_rate, seed)
            del manager


main()
