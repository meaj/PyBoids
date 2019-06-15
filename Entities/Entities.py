"""
Pyboids - Entities
 * A class containing the definitions of the entity object and the objects that extend it
 * Copyright (c) 2019 Meaj
"""
import math
from Entities import Vector2D


class Entity:
    def __init__(self, entity_id, x_pos, y_pos):
        self.entity_id = entity_id
        self.pos = Vector2D.Vector2D(x_pos, y_pos)

    def get_position(self):
        return self.pos

    def get_id(self):
        return self.entity_id


class Boid(Entity):

    def __init__(self, boid_id, x, y, side_len):
        super().__init__(boid_id, x, y)
        self.vel = Vector2D.Vector2D()
        self.height = math.sqrt(3) * (side_len // 2)

        self.goal_dir = 0  # direction of nearest goal relative to boid
        self.my_dir = 0  # current heading of the boid

        self.connected_boids = []  # list of all visible boids in range, their ids, and positions used to form flocks
        self.visible_boids = []  # List of all visible boids, used to encourage flocking by showing possible options
        self.collisions = []  # list of boids we are too close to
        self.touched_goal = False  # used to alert manager when a coin is touched
        self.nearest_goal = Entity(0, 0, 0)
        self.score = 0

    # Returns the magnitude of the velocity vector
    def get_speed(self):
        return abs(self.vel)

    def get_direction(self):
        return self.my_dir

    def get_goal_dir(self):
        return self.goal_dir

    def get_connected_boids(self):
        return self.connected_boids

    def get_visible_boids(self):
        return self.visible_boids

    def get_collisions(self):
        return self.collisions

    def get_touched(self):
        return self.touched_goal

    def get_score(self):
        return self.score

    def get_height(self):
        return self.height

    def get_velocity(self):
        return self.vel

    def update_velocity(self, val):
        val += self.vel
        # Velocity limiting rules
        if val.x >= 5:
            val.x = 5
        elif val.x <= -5:
            val.x = -5

        if val.y >= 5:
            val.y = 5
        elif val.y <= -5:
            val.y = -5

        self.vel = val

    def update_position(self, board_dims):
        self.pos += self.vel
        x = self.pos[0]
        y = self.pos[1]
        if x >= board_dims[0] - self.height // 2:
            x = board_dims[0] - self.height // 2
        if x < self.height // 2:
            x = self.height // 2
        # Change our y position
        if y >= board_dims[1] - 3 * self.height // 4:
            y = board_dims[1] - 3 * self.height // 4
        if y < 12 + self.height // 2:  # 12 is the height of the text display at the top
            y = 12 + self.height // 2
        self.pos = Vector2D.Vector2D(x, y)
        self.my_dir = (180 + self.vel.argument()) % 360

    # Increments the score by the passed value or 1 by default
    def increment_score(self, val=1):
        self.score += val

    # Takes a tuple containing the position of an object and returns its angle relative to the boid's heading
    def calc_angle_from_pos(self, obj_pos):
        temp_theta = math.atan2(self.pos.y - obj_pos.y, self.pos.x - obj_pos.x)
        if temp_theta < 0:
            temp_theta = abs(temp_theta)
        else:
            temp_theta = 2 * math.pi - temp_theta
        return (math.degrees(temp_theta) + 90) % 360

    # Takes an angle theta and checks if it is in visible range of the boid
    def is_object_visible(self, theta):
        arc = (135 + self.my_dir) % 360, (225 + self.my_dir) % 360
        if arc[0] <= theta <= arc[1]:
            return False
        else:
            return True

    # Just your friendly neighborhood distance formula
    def calc_dist_to_object(self, pos):
        return math.pow(self.pos[0] - pos[0], 2) + pow(self.pos[1] - pos[1], 2)

    # Creates a list of connections, that is boids that are visible and have a distance within range
    # If boids collide, a list is made so that the game manager can remove them
    def find_connections(self, list_of_boids):
        self.connected_boids = []
        self.visible_boids = []

        # For each boid that isn't us, get the id, distance to it, and relative angle
        for temp_boid in list_of_boids:
            if temp_boid.entity_id != self.entity_id:
                t_id = temp_boid.get_id()
                theta = self.calc_angle_from_pos(temp_boid.get_position())
                dist = self.calc_dist_to_object(temp_boid.get_position())
                if self.is_object_visible(theta):
                    self.visible_boids.append((t_id, dist))
                # If the boid is in our range of vision and close enough, add it to our connection list
                if self.is_object_visible(theta) and dist <= 3600:
                    self.connected_boids.append((t_id, dist))
                # If the boid is too close, add it to our collision list and remove it from our connections if present
                if dist < (self.height//2)**2:
                    self.collisions.append(temp_boid)
                    if (t_id, dist) in self.connected_boids:
                        self.connected_boids.remove((t_id, dist))

    def find_nearest_goal(self, goal_list):
        nearest = goal_list[-1]
        for goal in goal_list:
            if nearest is not goal and self.is_object_visible(self.calc_angle_from_pos(goal.get_position())):
                if abs(goal.get_position() - self.pos) < abs(nearest.get_position() - self.pos):
                    nearest = goal
        self.nearest_goal = nearest
        if not self.touched_goal and self.calc_dist_to_object(self.nearest_goal.get_position()) < 64:
            self.touched_goal = True
        else:
            self.touched_goal = False
        temp = self.calc_angle_from_pos(self.nearest_goal.get_position())
        if self.is_object_visible(temp):
            self.goal_dir = temp  # goal is visible
        else:
            self.goal_dir = -1  # goal is not visible

    def move(self, new_vel, new_dir, board_dims):
        # Change our heading
        if new_dir >= 360:
            new_dir -= 360
        if new_dir < 0:
            new_dir += 360
        self.my_dir = new_dir

        # Change our velocity
        self.vel = new_vel

        # Change our x position
        x = self.pos[0]
        x -= new_vel * math.sin(math.radians(new_dir))  # x component of our movement
        if x >= board_dims[0] - self.height // 2:
            x = board_dims[0] - self.height // 2
        if x < self.height // 2:
            x = self.height // 2
        # Change our y position
        y = self.pos[1]
        y -= new_vel * math.cos(math.radians(new_dir))  # y component of our movement
        if y >= board_dims[1] - 3 * self.height // 4:
            y = board_dims[1] - 3 * self.height // 4
        if y < 12 + self.height // 2:  # 12 is the height of the text display at the top
            y = 12 + self.height // 2
        self.pos = Vector2D.Vector2D(x, y)

