"""
Pyboids - BoidRules
 * A file containing the flocking rules based on those used in Craig Reynold's simulation
"""

from Entities.Vector2D import Vector2D


# Encourage boids to move towards flock center
def cohesion_rule(boid, flock):
    center = Vector2D()
    for member in flock:
        if member is not boid and member is not None:
            center += member.get_position()
    center /= len(flock) - 1
    return center - boid.get_position() - boid.get_velocity()


# Encourage boids to avoid colliding as this causes mutual boid death
def separation_rule(boid, flock, avoidance_gene):
    avoid = Vector2D()
    for member in flock:
        if member is not boid and member is not None:
            if abs(member.get_position() - boid.get_position()) <= boid.too_close:
                boid.cost += 1  # Increment cost if we are too close
                avoid -= (member.get_position() - boid.get_position()) * avoidance_gene
    return avoid - boid.get_velocity()


# Encourage boids in a given flock to match the average velocity of the flock
def alignment_rule(boid, flock):
    perceived_vel = Vector2D()
    for member in flock:
        if member is not boid and member is not None:
            perceived_vel += member.get_velocity()
    perceived_vel /= len(flock) - 1
    return perceived_vel - boid.get_velocity()


# Encourage boids to head in the direction of the goal
def tend_to_position(boid, position):
    return position - boid.get_position() - boid.get_velocity()


# Encourage boids to head away from the position
def avoid_position(boid, position):
    return -1 * (position - boid.get_position() - boid.get_velocity())


# Encourage boids to avoid walls as they can increase chance of collision
def avoid_walls(boid, board_dims):
    wall_avoid = Vector2D(0, 0)
    boid_pos = boid.get_position()
    if boid_pos.x < boid.radius * 2:
        wall_avoid.x = boid.radius
    elif boid_pos.x >= board_dims[0] - boid.radius * 2:
        wall_avoid.x = -boid.radius

    if boid_pos.y < boid.radius * 2:
        wall_avoid.y = boid.radius
    elif boid_pos.y >= board_dims[1] - boid.radius * 2:
        wall_avoid.y = -boid.radius

    return wall_avoid
