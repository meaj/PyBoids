"""
Pyboids - Entities
 * A class containing the definitions of the entity object and the objects that extend it
 * Copyright (c) 2019 Meaj
"""
import math
from Entities import Vector2D

MAX_VELOCITY = 5


class Entity:
    def __init__(self, entity_id=-1, x_pos=0, y_pos=0, radius=2):
        self.entity_id = entity_id  # Numerical identifier for this entity
        self.pos = Vector2D.Vector2D(x_pos, y_pos)  # Vector representing the position of the entity
        self.radius = radius

    """ Getter functions used to communicate with other classes """
    def get_position(self):
        return self.pos

    def get_id(self):
        return self.entity_id

    def get_radius(self):
        return self.radius


class Boid(Entity):
    def __init__(self, boid_id, x, y, radius=2):
        # Variables inherited from entity class
        super().__init__(boid_id, x, y, radius)

        # Movement Variables
        self.velocity = Vector2D.Vector2D()  # Vector representing the velocity of the entity
        self.divergence = 1.0  # Used to introduce random movement for related boids in each population

        # Flocking data
        # Range variables
        self.collision_range = radius * 2.5  # Distance from our position at which we collide with another boid
        self.separate_range = radius * 5  # Distance from our position at which we begin to avoid other boids
        self.flock_range = self.separate_range * 20  # Distance from our position at which we begin to form flocks
        # Flock formation variables
        self.visible_boids = []  # List of all boids within the visible arc of the boid
        self.connected_boids = []  # List of tuples of all visible boids within flock_range and the distance to them

        # Fitness data
        # Scoring Variables
        self.touched_goal = False  # Boolean used to inform simulation manager a goal has been touched
        self.nearest_goal = Entity()  # Entity object that will store information about the nearest goal
        self.score = 0  # Integer representing the number of points awarded to this boid for touching goals
        # Cost Variables
        self.collided = False  # Boolean used to inform simulation manager that the boid has collided with another
        self.cost = 0  # Float representing the ability of this boid to flock, avoid obstacles, and head toward goals
        self.live_time = 0  # Float representing the number of seconds this boid has been active for

    """ Getter functions used to communicate with other classes """
    # Return the magnitude of our velocity vector
    def get_acceleration(self):
        return abs(self.velocity)

    # Return the direction of our velocity vector
    def get_direction(self):
        return self.velocity.get_direction()

    # Return the distance between us and another entity
    def get_distance_to_other(self, other):
        return (self.pos.x - other.pos.x) ** 2 + (self.pos.y - other.pos.y) ** 2

    # Return the direction of another entity relative to us
    def get_direction_to_other(self, other):
        dx = self.pos.x - other.pos.x
        dy = self.pos.y - other.pos.y
        return math.atan2(dy, dx) * 180/math.pi

    # Return the direction of the nearest goal relative to us
    def get_goal_direction(self):
        theta = self.get_direction_to_other(self.nearest_goal)
        if self.is_entity_visible(theta):
            return theta
        else:
            return -1

    # Return the value of self.touched_goal
    def has_touched_goal(self):
        return self.touched_goal

    # Returns true or false depending on if the relative angle of the entity is within our visible arc
    def is_entity_visible(self, theta):
        arc = (135 + self.get_direction()) % 360, (225 + self.get_direction()) % 360
        if arc[0] <= theta <= arc[1]:
            return False
        else:
            return True

    """ Setter and updater functions used to change variables """
    # Change divergence by provided value
    def set_divergence(self, value):
        self.divergence = value

    # Change score by provided value
    def update_score(self, value=1):
        self.score += value

    # Change cost related variables by provided values
    def update_cost_variables(self, playtime):
        # Match our live_time to playtime
        self.live_time = playtime

    # Change velocity by provided vector
    def update_velocity(self, vector):
        # First ensure our velocity does not go over the limit
        vector += self.velocity

        if vector.x > MAX_VELOCITY:
            vector.x = MAX_VELOCITY
        elif vector.x < -MAX_VELOCITY:
            vector.x = -MAX_VELOCITY

        if vector.y > MAX_VELOCITY:
            vector.y = MAX_VELOCITY
        elif vector.y < -MAX_VELOCITY:
            vector.y = -MAX_VELOCITY

        # Update velocity vector after checks and apply divergence value
        self.velocity = vector * self.divergence

    def move_boid(self):
        self.pos += self.velocity

    # Updates the list of visible boids based on the provided list of all boids
    def update_visible_boids(self, boid_list):
        visible = []

        for other_boid in boid_list:
            if other_boid is not self:
                theta = self.get_direction_to_other(other_boid)
                if self.is_entity_visible(theta):
                    visible.append(other_boid)

        self.visible_boids = visible

    # Updates the list of connected boids based on the list of provided boids
    def update_connected_boids(self, boid_list):
        connections = []
        self.update_visible_boids(boid_list)

        for other_boid in boid_list:
            if other_boid is not self:
                distance = self.get_distance_to_other(other_boid)
                # Handle collisions first
                if distance <= self.collision_range:
                    self.collided = True
                # Add visible boids in range to connections, along with the distance to them
                if distance < self.flock_range and other_boid in self.visible_boids:
                    connections.append((other_boid, distance))

        self.connected_boids = connections

    # Updates nearest_goal based on the list of provided goals
    def update_nearest_goal(self, goal_list):
        nearest = goal_list[-1]
        for goal in goal_list:
            if nearest is not goal and self.is_entity_visible(self.get_direction_to_other(goal)):
                if abs(goal.get_position() - self.pos) < abs(nearest.get_position() - self.pos):
                    nearest = goal
        self.nearest_goal = nearest

    # Updates touched_goal boolean
    def update_touched_goal(self):
        if not self.touched_goal and self.get_distance_to_other(self.nearest_goal) < self.collision_range:
            self.touched_goal = True
        else:
            self.touched_goal = False

    # Move the boid on the simulation area
    def update_position(self, board_dims):
        self.pos += self.velocity
        x = self.pos.x
        y = self.pos.y
        # Change our x position
        if x >= board_dims[0] - self.radius:
            x = board_dims[0] - self.radius
        if x < self.radius:
            x = self.radius
        # Change our y position
        if y >= board_dims[1] - self.radius:
            y = board_dims[1] - self.radius
        if y < 12 + self.radius:  # 12 is the height of the text display at the top
            y = 12 + self.radius
        self.pos = Vector2D.Vector2D(x, y)

    # Increments the score by the passed value or 1 by default
    def increment_score(self, val=1):
        self.score += val

    def update_cost(self, flock_dir, flock_goal_dir, playtime):
        # penalty for not following the same average dir as the flock
        self.cost += (self.get_direction() - flock_dir) / 100
        # penalty for not heading towards the goal
        self.cost += (self.get_direction() - self.get_goal_direction()) / 100
        # penalty for not heading towards the flock's perceived goal direction
        # self.cost += (self.my_dir - flock_goal_dir)/100

        self.live_time = playtime

