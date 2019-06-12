from Vector2D import Vector2D


def move_all_boids(boid_list, flock_list, goal, board_dims, boid_height):
    boid_dict = dict()
    for boid in boid_list:
        boid_dict.update({boid.get_id(): boid})

    for boid in boid_list:
        for flock in flock_list:
            b_id = boid.get_id()
            if b_id in flock:
                v1 = cohesion_rule(boid, flock, boid_dict)
                v2 = separation_rule(boid, flock, boid_dict)
                v3 = alignment_rule(boid, flock, boid_dict)
                v4 = tend_to_position(boid, goal.get_position())
                dv = v1 + v2 + v3 + v4
                # Velocity limiting rules
                if dv.x > 1:
                    dv.x = 1
                elif dv.x < -1:
                    dv.x = -1

                if dv.y > 1:
                    dv.y = 1
                elif dv.y < -1:
                    dv.y = -1

                boid.update_velocity(dv)
                boid.update_position(board_dims, boid_height)


def cohesion_rule(boid, flock, boid_dict):
    center = Vector2D()
    for mem in flock:
        member = boid_dict.get(mem)
        if member is not boid and member is not None:
            center += member.get_velocity()
    center /= len(flock)
    #print("Cohesion Vel: {}".format((center - boid.get_velocity()) / 1))
    return (center - boid.get_velocity()) / 1


def separation_rule(boid, flock, boid_dict):
    avoid = Vector2D()
    for mem in flock:
        member = boid_dict.get(mem)
        if member is not boid and member is not None:
            if 15 <= abs(member.get_position() - boid.get_position()) < 20:
                avoid -= (member.get_position() - boid.get_position())/2
            elif abs(member.get_position() - boid.get_position()) < 15:
                avoid -= member.get_position() - boid.get_position()
    #print("Separation Vel: {}".format(avoid))
    return avoid


def alignment_rule(boid, flock, boid_dict):
    perceived_vel = Vector2D()
    for mem in flock:
        member = boid_dict.get(mem)
        if member is not boid and member is not None:
            perceived_vel += member.get_velocity()
    perceived_vel /= len(flock)
    #print("Alignment Vel: {}".format(perceived_vel - boid.get_velocity()))
    return (perceived_vel - boid.get_velocity())/16


def tend_to_position(boid, position):
    #print("Goal Vel: {}".format((position - boid.get_position())))
    return (position - boid.get_position())/32
