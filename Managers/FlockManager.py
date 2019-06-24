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
                    for b in boids:
                        if b.get_id() == member:
                            # Each boid is awarded points equal to either the length of the flock or the pref. flock
                            # size, whichever is smaller. We also check to make sure the awards are in bounds
                            if 0 <= award < self.pref_flock_members:
                                b.increment_score(award)
                                total += award
                            elif self.pref_flock_members <= award < self.max_flock_members:
                                b.increment_score(self.pref_flock_members)
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
                for boid in boids:
                    # Gather data for each boid
                    if boid.get_id() == member:
                        t = boid.get_position()
                        sum_vel += boid.get_velocity()
                        sum_x += t[0]
                        sum_y += t[1]
                        sum_theta += boid.get_direction()
                        score += boid.get_score()
                        if boid.get_goal_dir() != -1:
                            sum_goal_theta += boid.get_goal_dir()
                            visible_goals += 1
            # Append each new value so that the indexes for the data match those of the flocks
            cent.append((sum_x/len(flock), sum_y/len(flock)))  # just the average position of each boid
            thetas.append(sum_theta/len(flock))  # this does not seem right, but it works anyway ¯\_(ツ)_/¯
            goals.append(sum_goal_theta / visible_goals)
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
            con = [boid.get_id()]
            for entry in boid.get_connected_boids():
                con.append(entry[0])
            # Begin placing con into flocks
            # When flocks is empty, add the current con to the list of flocks
            if not flocks:
                flocks.append(con)
            # If flocks exist, check for overlap and add to list if overlap exists
            else:
                placed = False
                for flock in flocks:
                    if (not set(flock).isdisjoint(set(con))) or (not set(con).isdisjoint(set(flock))):
                        update = set(flock).union(set(con))
                        flock.extend(update)
                        placed = True
                if not placed:
                    flocks.append(con)
        # One final pass to remove duplicates and merge any lingering overlaps, may be superfluous
        for flock in flocks:
            ext = False
            for final in self.flock_list:
                if (not set(flock).isdisjoint(set(final))) or (not set(final).isdisjoint(set(flock))):
                    list(final).extend(set(flock).union(set(final)))
                    ext = True
            if set(flock) not in self.flock_list and not ext:
                self.flock_list.append(set(flock))
