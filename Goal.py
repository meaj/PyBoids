"""
Pyboids - Goal
 * A class containing the definitions of the Goal objects
 * Copyright (c) 2019 Meaj
"""


class Goal:

    def __init__(self, x, y, goal_id=1):
        self.goal_id = goal_id
        self.x = x
        self.y = y

    def get_position(self):
        return self.x, self.y

    def get_id(self):
        return self.goal_id
