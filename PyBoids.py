"""
Pyboids
 * An exploration of the ability of various AIs to develop flocking behavior
 * Copyright (c) 2019 Meaj
"""

from Managers.SimulationManager import SimulationManager


def main():

    for i in range(0, 7):
        manager = SimulationManager(visual_mode=True)
        print("Running simulation with crossover type {}".format(i))
        manager.run_generations(crossover_type=i)
        del manager
    # manager = SimulationManager(visual_mode=True)
    # manager.run_loop()


main()
