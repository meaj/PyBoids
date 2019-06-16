"""
Pyboids - GeneticReynoldsControl
 * A version of Craig Reynolds Boids that has weights attached to each velocity vector. These weights are fed to a
 * genetic algorithm that will be optimizing for high score and high number of survivors after M minutes
 * Copyright (c) 2019 Meaj
"""
import copy
import random
import statistics
from Entities.Vector2D import Vector2D

# TODO: Allow user to set the number of generations to breed or to breed until stopped
# TODO: Implement method to store genes and fitness of each boid iteration for genetic culling


class ReynoldsChromosome:
    def __init__(self, m1=1, m2=1, m3=1, m4=1, m5=1, dv1=1.1):
        self.cohesion_gene = m1  # Cohesion
        self.separation_gene = m2  # Separation
        self.alignment_gene = m3  # Alignment
        self.goal_seeking_gene = m4  # Goal Seek
        self.wall_avoidance_gene = m5  # Wall Avoid
        self.divergence_gene = dv1  # Species Divergence Gene

    # Allows indexing of the chromosome
    def __getitem__(self, item):
        if item == 0:
            return self.cohesion_gene
        elif item == 1:
            return self.separation_gene
        elif item == 2:
            return self.alignment_gene
        elif item == 3:
            return self.goal_seeking_gene
        elif item == 4:
            return self.wall_avoidance_gene
        elif item == 5:
            return self.divergence_gene
        else:
            print("Index out of range")

    def __setitem__(self, key, item):
        if key == 0:
            self.cohesion_gene = item
        elif key == 1:
            self.separation_gene = item
        elif key == 2:
            self.alignment_gene = item
        elif key == 3:
            self.goal_seeking_gene = item
        elif key == 4:
            self.wall_avoidance_gene = item
        elif key == 5:
            self.divergence_gene = item
        else:
            print("Index out of range")

    def __len__(self):
        return 6

    def __str__(self):
        return '[{}, {}, {}, {}, {}, {}]'.format(self.cohesion_gene, self.separation_gene, self.alignment_gene,
                                                 self.goal_seeking_gene, self.wall_avoidance_gene, self.divergence_gene)


class ReynoldsIteration:
    def __init__(self, generation_number=0, iteration_number=0, genome=ReynoldsChromosome()):
        self.generation_number = generation_number
        self.iteration_number = iteration_number
        self.genome = genome
        self.performance = 1.0

    def update_performance(self, value):
        self.performance = value

    def generate_divergence_value(self):
        return random.randrange(-self.genome[5], self.genome[5])

    def get_genome(self):
        return self.genome

    def get_id(self):
        return self.iteration_number


class ReynoldsGeneticAlgorithm:
    def __init__(self, generation_number, iteration_size, mutation_rate):
        self.cur_generation = 0  # This tracks which generation we are on
        self.max_generation = generation_number  # This indicates which generation to terminate on
        self.max_iterations = iteration_size  # This indicates how many iterations to create every generation
        self.mutation_rate = mutation_rate  # This is the rate at which genes will randomly mutate
        self.genetic_history = []  # This tracks the chromosomes used by each iteration each generation
        self.iteration_list = []  # This tracks the iterations used each generation, this is cleared once per gen
        self.survivors = []  # This tracks the iterations that survive after each culling

        for i in range(self.max_iterations):
            self.iteration_list.append(ReynoldsIteration(self.cur_generation, i+1,
                                                         ReynoldsChromosome(random.randrange(-1000, 1000)/100,
                                                                            random.randrange(-1000, 1000)/100,
                                                                            random.randrange(-1000, 1000)/100,
                                                                            random.randrange(-1000, 1000)/100,
                                                                            random.randrange(-1000, 1000)/100,
                                                                            random.randrange(-1000, 1000)/100)))

    def get_iteration_list(self):
        return self.iteration_list

    def cull_bottom_half(self):
        iteration_performances = []
        self.survivors = []

        for iteration in self.iteration_list:
            iteration_performances.append(iteration.performance)
        median = statistics.median(iteration_performances)

        for iteration in self.iteration_list:
            if iteration.performance >= median and len(self.survivors) < self.max_iterations/2:
                self.survivors.append(iteration)
            if len(self.survivors) == self.max_iterations/2:
                break

    @staticmethod
    def crossover_genes(chromosome_1, chromosome_2):
        overlap = random.randrange(1, len(chromosome_1)+1)
        for i in range(0, overlap):
            t_gene = chromosome_1[i]
            chromosome_1[i] = chromosome_2[i]
            chromosome_2[i] = t_gene
        return chromosome_1, chromosome_2

    def mutate_genes(self, chromosome):
        for idx in range(0, len(chromosome)):
            chance = random.randrange(1, self.mutation_rate + 1, 1)
            if chance == self.mutation_rate:
                chromosome[idx] = random.randrange(-1000, 1000)/100
            idx += 1
        return chromosome

    # Creates 4 children from 2 parents
    def breed_iterations(self, iteration_1, iteration_2):
        # Crossover
        offspring_genome_1, offspring_genome_2 = self.crossover_genes(copy.copy(iteration_2.get_genome()),
                                                                      copy.copy(iteration_1.get_genome()))
        offspring_genome_3, offspring_genome_4 = self.crossover_genes(copy.copy(iteration_1.get_genome()),
                                                                      copy.copy(iteration_2.get_genome()))
        # Mutations
        offspring_genome_1 = self.mutate_genes(offspring_genome_1)
        offspring_genome_2 = self.mutate_genes(offspring_genome_2)
        offspring_genome_3 = self.mutate_genes(offspring_genome_3)
        offspring_genome_4 = self.mutate_genes(offspring_genome_4)

        # Iteration creation
        offspring_1 = ReynoldsIteration(self.cur_generation, iteration_1.get_id(), offspring_genome_1)
        offspring_2 = ReynoldsIteration(self.cur_generation, iteration_2.get_id(), offspring_genome_2)
        offspring_3 = ReynoldsIteration(self.cur_generation, iteration_1.get_id()+1, offspring_genome_3)
        offspring_4 = ReynoldsIteration(self.cur_generation, iteration_2.get_id()+1, offspring_genome_4)
        return offspring_1, offspring_2, offspring_3, offspring_4

    def advance_generation(self, fitness_function):
        next_gen = []
        for iteration in self.iteration_list:
            iteration.update_performance(fitness_function(iteration.get_genome()))

        self.cull_bottom_half()
        random.shuffle(self.survivors)

        while self.survivors:
            parent_1 = self.survivors.pop()
            parent_2 = self.survivors.pop()
            child_list = self.breed_iterations(parent_1, parent_2)
            idx = 1
            for child in child_list:
                child.iteration_number = idx
                next_gen.append(child)
                idx += 1

        self.iteration_list = next_gen
        self.cur_generation += 1


def move_all_boids_genetic(boid_list, flock_list, board_dims, boid_height, iteration_chromosome=ReynoldsChromosome()):
    chromosome = iteration_chromosome
    # Create a dictionary of all boids by id to quickly search for boids by id values extracted from flock
    boid_dict = dict()
    for boid in boid_list:
        boid_dict.update({boid.get_id(): boid})

    for boid in boid_list:
        for flock in flock_list:
            b_id = boid.get_id()
            if b_id in flock:

                # Calculate components of our velocity based on various rules
                v1 = cohesion_rule(boid, flock, boid_dict) * chromosome.cohesion_gene
                v2 = separation_rule(boid, flock, boid_dict, boid_height, chromosome.separation_gene)
                v3 = alignment_rule(boid, flock, boid_dict) * chromosome.alignment_gene
                # Special rule to check if goal is visible
                if boid.is_object_visible(boid.calc_angle_from_pos(boid.nearest_goal.get_position())):
                    v4 = tend_to_position(boid, boid.nearest_goal.get_position()) * chromosome.goal_seeking_gene
                    if len(flock) == 1:
                        v4 *= chromosome.goal_seeking_gene * 16
                    if abs(boid.calc_dist_to_object(boid.nearest_goal.get_position())) < 4*boid_height:
                        v4 *= chromosome.goal_seeking_gene * 32
                else:
                    v4 = Vector2D(random.randrange(0.0, 2.0), random.randrange(0.0, 2.0))
                v5 = avoid_walls(boid, board_dims, boid_height) * chromosome.wall_avoidance_gene

                dv = v1 + v2 + v3 + v4 + v5
                dv *= boid.get_divergence()

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
def separation_rule(boid, flock, boid_dict, boid_height, avoidance_gene):
    avoid = Vector2D()
    for mem in flock:
        member = boid_dict.get(mem)
        if member is not boid and member is not None:
            if abs(member.get_position() - boid.get_position()) < boid_height*2:
                avoid -= (member.get_position() - boid.get_position()) * avoidance_gene
    return avoid


# Encourage boids in a given flock to match the average velocity of the flock
def alignment_rule(boid, flock, boid_dict):
    perceived_vel = Vector2D()
    for mem in flock:
        member = boid_dict.get(mem)
        if member is not boid and member is not None:
            perceived_vel += member.get_velocity()
    perceived_vel /= len(flock)
    return perceived_vel - boid.get_velocity()


# Encourage boids to head in the direction of the goal
def tend_to_position(boid, position):
    return position - boid.get_position()


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
