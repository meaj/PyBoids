"""
Pyboids
 * An exploration of the ability of various AIs to develop flocking behavior
 * Copyright (c) 2019 Meaj
"""

from Managers.SimulationManager import SimulationManager
from Constants import VERSION
# best so far:
# -0.2726218754477409, 0.22531065494572736, 0.012347193295672765, 0.4056808036681063, 0.5633023671766649, 0.768


def main():
    manager = SimulationManager(visual_mode=True, version=VERSION)
    manager.start_menu()


main()
