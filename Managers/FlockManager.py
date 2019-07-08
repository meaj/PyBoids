"""
Pyboids - FlockManager
 * A class containing the definitions of the FlockManager object
 * Copyright (c) 2019 Meaj
"""
from Entities.Vector2D import Vector2D


class FlockManager:
    def __init__(self):
        # Set of flocks formed each frame by manager
        self.flock_list = []
        # Data corresponding to each flock
        # These should always have the same order as flocks
        self.flock_centroids = []
        self.flock_thetas = []
        self.flock_goal_thetas = []
        self.flock_velocities = []
        # This will need to be implemented
        self.flock_scores = [0]
        # These are currently unused, but would control the flock size
        # Score should be updated such that when the number of flock members is under pref_flock_members the flock gets
        # One point for each member of the flock. If the flock size goes over pref_flock_members, only
        # pref_flock_members points will be added. If it goes over max, no points will be added
        self.pref_flock_members = 8
        self.max_flock_members = 16

    # Getter functions that do what they say on the tin
    def get_flocks(self):
        return self.flock_list

    def get_centroids(self):
        return self.flock_centroids

    def get_thetas(self):
        return self.flock_thetas

    def get_scores(self):
        return self.flock_scores

    def get_goal_thetas(self):
        return self.flock_goal_thetas

    def get_velocities(self):
        return self.flock_velocities

    # Ensures that when a flock member collides with a goal, each member of the flock gets awarded some points
    def update_flock_score(self, boid, boids):
        total = 0
        # First find the relevant flock
        for flock in self.flock_list:
            award = len(flock)
            if boid in flock:
                # If the flock is too big, it won't score, so we can break
                if self.max_flock_members <= award:
                    break
                # Next each member needs to be awarded
                # Since FlockManager doesn't actually store boids, just their ids, we have to cross reference
                # the list of boids passed in from the game manager. If we change the list to a dictionary we won't
                # need to cross reference and lookup will be faster, but that may cause issues, hence the nastiness
                for member in flock:
                    # Each boid is awarded points equal to either the length of the flock or the pref. flock
                    # size, whichever is smaller. We also check to make sure the awards are in bounds
                    if 0 <= award < self.pref_flock_members:
                        member.increment_score(award)
                        total += award
                    elif self.pref_flock_members <= award < self.max_flock_members:
                        member.increment_score(self.pref_flock_members)
                        total += self.pref_flock_members
        return total

    # Calculates the position of centroids, the value of average thetas, and the scores for each flock
    def calc_flock_data(self, boids):
        cent = []
        thetas = []
        scores = []
        goals = []
        vels = []
        # Gather data for each flock
        for flock in self.flock_list:
            sum_x = 0
            sum_y = 0
            sum_theta = 0
            sum_goal_theta = 0
            sum_vel = Vector2D(0, 0)
            score = 0
            # More nasty cross referencing, see update_flock_scores()
            visible_goals = 0
            for member in flock:
                t = member.get_position()
                sum_vel += member.get_velocity()
                sum_x += t[0]
                sum_y += t[1]
                sum_theta += member.get_direction()
                score += member.get_score()
                if member.get_goal_dir() != -1:
                    sum_goal_theta += member.get_goal_dir()
                    visible_goals += 1
            # Append each new value so that the indexes for the data match those of the flocks
            cent.append(Vector2D(sum_x/len(flock), sum_y/len(flock)))  # just the average position of each boid
            thetas.append(sum_theta/len(flock))  # this does not seem right, but it works anyway ¯\_(ツ)_/¯
            if visible_goals != 0:
                goals.append(sum_goal_theta / visible_goals)
            else:
                goals.append(-1)
            vels.append(sum_vel/len(flock))
            scores.append(score)  # scores are aggregated from boids to account for changes in flock members
            # Clear everything to ensure no references to nonexistent flocks
            self.flock_centroids = cent
            self.flock_thetas = thetas
            self.flock_scores = scores
            self.flock_goal_thetas = goals
            self.flock_velocities = vels

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
                    if entry in flock:
                        update = set(con).union(set(flock))
                        con.extend(update)
                        flocks.remove(flock)
                        del flock
                        break
            con = list(set(con))
            if con not in flocks:
                flocks.append(con)
        self.flock_list = flocks
