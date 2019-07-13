"""
Pyboids - FlockManager
 * A class containing the definitions of the FlockManager object
 * Copyright (c) 2019 Meaj
"""
from Entities.Vector2D import Vector2D
import math


class Flock:
    def __init__(self, member_list=None):
        self.flock_members = member_list  # List of boids that are flock members
        self.flock_centroid = Vector2D()  # Position vector representing the virtual centroid of the flock
        self.flock_velocity = Vector2D()  # Velocity vector representing the perceived velocity of the flock
        self.flock_goal = None            # This will contain an entity representing the most common goal of the flock
        self.flock_goal_dir = -1
        self.flock_score = 0              # The combined score of all members of the flock

    # Calculates the position of centroids, the value of average thetas, and the scores for each flock
    def update_flock_data(self):
        sum_pos = Vector2D()
        sum_vel = Vector2D(0, 0)
        score = 0
        goals = {}
        # More nasty cross referencing, see update_flock_scores()
        for member in self.flock_members:
            sum_vel += member.get_velocity()
            sum_pos += member.get_position()
            score += member.get_score()
            if member.nearest_goal not in goals:
                if member.goal_dir != -1:
                    goals.update({member.nearest_goal: 1})
            elif member.nearest_goal in goals:
                goals[member.nearest_goal] += 1

        max_votes = -1
        for vote in goals:
            if goals[vote] > max_votes:
                max_votes = goals[vote]
                self.flock_goal = vote
        # Append each new value so that the indexes for the data match those of the flocks
        self.flock_centroid = sum_pos/len(self.flock_members)  # the average position of each boid
        self.flock_velocity = sum_vel/len(self.flock_members)  # the average velocity of each boid
        self.flock_score = score  # scores are aggregated from boids to account for changes in flock members

        if max_votes != -1:
            temp_theta = math.atan2(self.flock_centroid.y - self.flock_goal.pos.y,
                                    self.flock_centroid.x - self.flock_goal.pos.x)
            if temp_theta < 0:
                temp_theta = abs(temp_theta)
            else:
                temp_theta = 2 * math.pi - temp_theta
            self.flock_goal_dir = (math.degrees(temp_theta)-90) % 360


class FlockManager:
    def __init__(self):
        self.flock_list = []  # List of flocks formed each frame by manager

        # These are currently unused, but would control the flock size
        # Score should be updated such that when the number of flock members is under pref_flock_members the flock gets
        # One point for each member of the flock. If the flock size goes over pref_flock_members, only
        # pref_flock_members points will be added. If it goes over max, no points will be added
        self.pref_flock_members = 8
        self.max_flock_members = 16

    # Getter functions that do what they say on the tin
    def get_flocks(self):
        return self.flock_list

    # Ensures that when a flock member collides with a goal, each member of the flock gets awarded some points
    def update_flock_score(self, boid):
        total = 0
        # First find the relevant flock
        for flock in self.flock_list:
            award = len(flock.flock_members) * 10
            if boid in flock.flock_members:
                # If the flock is too big, it won't score, so we can break
                if self.max_flock_members <= len(flock.flock_members):
                    break
                # Next each member needs to be awarded
                # Since FlockManager doesn't actually store boids, just their ids, we have to cross reference
                # the list of boids passed in from the game manager. If we change the list to a dictionary we won't
                # need to cross reference and lookup will be faster, but that may cause issues, hence the nastiness
                for member in flock.flock_members:
                    # Each boid is awarded points equal to either the length of the flock or the pref. flock
                    # size, whichever is smaller. We also check to make sure the awards are in bounds
                    if 0 <= len(flock.flock_members) < self.pref_flock_members:
                        member.increment_score(award)
                        total += award
                    elif self.pref_flock_members <= len(flock.flock_members) < self.max_flock_members:
                        member.increment_score(self.pref_flock_members * 10)
                        total += self.pref_flock_members * 10
        return total

    # Calculates the position of centroids, the value of average thetas, and the scores for each flock
    def update_all_flock_data(self):
        # Gather data for each flock
        for flock in self.flock_list:
            flock.update_flock_data()

    # calculates the number of flocks and stores their members as a list of lists
    # When the boids move quickly, the flocks sometime do not make sense, this is being examined
    def form_flocks(self, boids):
        self.flock_list = []
        flocks = []
        for boid in boids:
            # Extract all the boid IDs to the list of new connections, con
            con = []
            for entry in boid.get_connected_boids():
                con.append(entry)
            # Begin placing con into flocks
            # Check for overlap and add to list if overlap exists
            for flock in flocks:
                for entry in con:
                    if entry in flock.flock_members:
                        update = set(con).union(set(flock.flock_members))
                        con.extend(update)
                        flocks.remove(flock)
                        del flock
                        break
            con = list(set(con))
            if con not in flocks:
                flocks.append(Flock(con))
        self.flock_list = flocks
