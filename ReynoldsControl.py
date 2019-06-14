"""
Pyboids - ReynoldsControl
 * My implementation of the flocking algorithm devised by Craig Reynolds
 * Copyright (c) 2019 Meaj
"""
from Vector2D import Vector2D
import random


def move_all_boids(boid_list, flock_list, board_dims, boid_height):
    # Create a dictionary of all boids by id to quickly search for boids by id values extracted from flock
    boid_dict = dict()
    for boid in boid_list:
        boid_dict.update({boid.get_id(): boid})

    for boid in boid_list:
        for flock in flock_list:
            b_id = boid.get_id()
            if b_id in flock:

                # Calculate components of our velocity based on various rules
                v1 = cohesion_rule(boid, flock, boid_dict)
                v2 = separation_rule(boid, flock, boid_dict, boid_height)
                v3 = alignment_rule(boid, flock, boid_dict)
                # Special rule to check if goal is visible
                if boid.is_object_visible(boid.calc_angle_from_pos(boid.nearest_goal.get_position())):
                    v4 = tend_to_position(boid, boid.nearest_goal.get_position())
                else:
                    v4 = Vector2D(random.randrange(0.0, 2.0), random.randrange(0.0, 2.0))
                v5 = avoid_walls(boid, board_dims, boid_height)

                dv = v1 + v2 + v3 + v4 + v5

                boid.update_velocity(dv)
                boid.update_position(board_dims)


# Encourage boids to form flocks
def cohesion_rule(boid, flock, boid_dict):
    center = Vector2D()
    for mem in flock:
        member = boid_dict.get(mem)
        if member is not boid and member is not None:
            center += member.get_velocity()
    center /= len(flock)
    return center - boid.get_velocity()


# Encourage boids to avoid colliding as this causes mutual boid death
def separation_rule(boid, flock, boid_dict, boid_height):
    avoid = Vector2D()
    for mem in flock:
        member = boid_dict.get(mem)
        if member is not boid and member is not None:
            if abs(member.get_position() - boid.get_position()) < boid_height*2:
                avoid -= (member.get_position() - boid.get_position())/4
    return avoid


# Encourage boids in a given flock to match the average velocity of the flock
def alignment_rule(boid, flock, boid_dict):
    perceived_vel = Vector2D()
    for mem in flock:
        member = boid_dict.get(mem)
        if member is not boid and member is not None:
            perceived_vel += member.get_velocity()
    perceived_vel /= len(flock)
    return (perceived_vel - boid.get_velocity())/8


# Encourage boids to head in the direction of the goal
def tend_to_position(boid, position):
    return (position - boid.get_position())/128


# Encourage boids to avoid walls as they can increase chance of collision
def avoid_walls(boid, board_dims, boid_height):
    wall_avoid = Vector2D(0, 0)
    boid_pos = boid.get_position()
    if boid_pos.x < 2*boid_height:
        wall_avoid.x = boid_height
    elif boid_pos.x >= board_dims[0] - 2*boid_height:
        wall_avoid.x = -boid_height

    if boid_pos.y < 2*boid_height:
        wall_avoid.y = boid_height
    elif boid_pos.y >= board_dims[1] - 2*boid_height:
        wall_avoid.y = -boid_height

    return wall_avoid
