""" This file contains the class definitions for the Goal objects"""


class Goal:

    def __init__(self, x, y, goal_id=1):
        self.goal_id = goal_id
        self.x = x
        self.y = y

    def get_position(self):
        return self.x, self.y
