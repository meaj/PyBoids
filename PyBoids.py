"""
Pyboids
 * An exploration of the ability of various AIs to develop flocking behavior
 * Copyright (c) 2019 Meaj
"""

from Managers.SimulationManager import SimulationManager


def main():

    for i in range(3, 4):
        manager = SimulationManager(visual_mode=True)
        manager.run_generations(crossover_type=i)
        del manager
    # manager.run_loop()


main()
