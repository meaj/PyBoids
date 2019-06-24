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
        return random.randrange(int(-self.genome[5]*100), int(self.genome[5]*100))/100

    def get_genome(self):
        return self.genome

    def get_id(self):
        return self.iteration_number

    def get_performance(self):
        return self.performance

    def set_id(self, value):
        self.iteration_number = value


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
                                                         ReynoldsChromosome(random.uniform(-1, 1),
                                                                            random.uniform(-1, 1),
                                                                            random.uniform(-1, 1),
                                                                            random.uniform(-1, 1),
                                                                            random.uniform(-1, 1),
                                                                            random.uniform(-1, 1))))

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
                print("Gen {} Iter {} survived and will breed".format(self.cur_generation, iteration.get_id()))
                self.survivors.append(iteration)
            if len(self.survivors) == self.max_iterations/2:
                break

    @staticmethod
    # Similar to crossover_genes, but allows each potential swap to be a average of the parent's genes
    def gene_commingling(chromosome_1, chromosome_2):
        overlap = random.randrange(1, len(chromosome_1) + 1)
        for i in range(0, overlap):
            beta = random.random()
            t_gene = (beta * chromosome_1[i]) + ((1 - beta) * chromosome_2[i])
            chromosome_1[i] = t_gene
            chromosome_2[i] = t_gene
        return chromosome_1, chromosome_2

    @staticmethod
    # Similar to crossover_genes, but allows each potential swap to be a average of the parent's genes
    def alternating_gene_commingling(chromosome_1, chromosome_2):
        overlap = random.randrange(1, len(chromosome_1) + 1)
        for i in range(0, overlap):
            beta = random.random()
            t_gene = (beta * chromosome_1[i]) + ((1 - beta) * chromosome_2[i])
            sign = -1 ** random.randrange(0, 1)
            chromosome_1[i] = t_gene * sign
            chromosome_2[i] = t_gene * -sign
        return chromosome_1, chromosome_2

    @staticmethod
    # Similar to crossover_genes, but allows each potential swap to be a average of the parent's genes
    def bounded_gene_commingling(chromosome_1, chromosome_2):
        overlap = random.randrange(1, len(chromosome_1) + 1)
        for i in range(0, overlap):
            beta = random.random()
            t_gene = (beta * chromosome_1[i]) + ((1-beta) * chromosome_2[i])
            sign = -1 ** random.randrange(0, 1)
            chromosome_1[i] += t_gene * sign
            while chromosome_1[i] > 1:
                chromosome_1[i] -= 1
            while chromosome_2[i] < -1:
                chromosome_2[i] += 1
            chromosome_2[i] -= t_gene * sign
            while chromosome_2[i] > 1:
                chromosome_2[i] -= 1
            while chromosome_2[i] < -1:
                chromosome_2[i] += 1
        return chromosome_1, chromosome_2

    @staticmethod
    # Similar to crossover_genes, but allows each potential swap to be a average of the parent's genes
    def unbounded_gene_commingling(chromosome_1, chromosome_2):
        overlap = random.randrange(1, len(chromosome_1) + 1)
        for i in range(0, overlap):
            beta = random.random()
            t_gene = (beta * chromosome_1[i]) + ((1 - beta) * chromosome_2[i])
            sign = -1 ** random.randrange(0, 1)
            chromosome_1[i] += t_gene * sign
            chromosome_2[i] -= t_gene * sign
        return chromosome_1, chromosome_2

    @staticmethod
    # Similar to crossover_genes, but allows each potential swap to be skipped as well
    def binary_choice_crossover_genes(chromosome_1, chromosome_2):
        overlap = random.randrange(1, len(chromosome_1)+1)
        for i in range(0, overlap):
            if random.randrange(0, 1) == 1:
                t_gene = chromosome_1[i]
                chromosome_1[i] = chromosome_2[i]
                chromosome_2[i] = t_gene
        return chromosome_1, chromosome_2

    @staticmethod
    # Allows for the genes of two parents to be swapped up to a random point. All genes up to that point are swapped
    def crossover_genes(chromosome_1, chromosome_2):
        overlap = random.randrange(1, len(chromosome_1)+1)
        for i in range(0, overlap):
            t_gene = chromosome_1[i]
            chromosome_1[i] = chromosome_2[i]
            chromosome_2[i] = t_gene
        return chromosome_1, chromosome_2

    # Allows for individual genes in the chromosome to be completely altered within the range of -0.999 to 0.999
    def mutate_genes(self, chromosome):
        for idx in range(0, len(chromosome)):
            chance = random.randrange(1, self.mutation_rate + 1, 1)
            if chance == self.mutation_rate:
                chromosome[idx] = random.randrange(-1000, 1000)/1000
            idx += 1
        return chromosome

    # Creates 4 children from 2 parents
    def breed_iterations(self, iteration_1, iteration_2, crossover_type=0):
        # Crossover
        # copy is use to ensure that the list values are exchanged and not the list values themselves
        if crossover_type == 1:
            offspring_genome_1, offspring_genome_2 = self.binary_choice_crossover_genes(
                copy.copy(iteration_2.get_genome()), copy.copy(iteration_1.get_genome()))
            offspring_genome_3, offspring_genome_4 = self.binary_choice_crossover_genes(
                copy.copy(iteration_1.get_genome()), copy.copy(iteration_2.get_genome()))
        elif crossover_type == 2:
            offspring_genome_1, offspring_genome_2 = self.unbounded_gene_commingling(
                copy.copy(iteration_2.get_genome()), copy.copy(iteration_1.get_genome()))
            offspring_genome_3, offspring_genome_4 = self.unbounded_gene_commingling(
                copy.copy(iteration_1.get_genome()), copy.copy(iteration_2.get_genome()))
        elif crossover_type == 3:
            offspring_genome_1, offspring_genome_2 = self.bounded_gene_commingling(
                copy.copy(iteration_2.get_genome()), copy.copy(iteration_1.get_genome()))
            offspring_genome_3, offspring_genome_4 = self.bounded_gene_commingling(
                copy.copy(iteration_1.get_genome()), copy.copy(iteration_2.get_genome()))
        elif crossover_type == 4:
            offspring_genome_1, offspring_genome_2 = self.alternating_gene_commingling(
                copy.copy(iteration_2.get_genome()), copy.copy(iteration_1.get_genome()))
            offspring_genome_3, offspring_genome_4 = self.alternating_gene_commingling(
                copy.copy(iteration_1.get_genome()), copy.copy(iteration_2.get_genome()))
        elif crossover_type == 5:
            offspring_genome_1, offspring_genome_2 = self.gene_commingling(
                copy.copy(iteration_2.get_genome()), copy.copy(iteration_1.get_genome()))
            offspring_genome_3, offspring_genome_4 = self.gene_commingling(
                copy.copy(iteration_1.get_genome()), copy.copy(iteration_2.get_genome()))
        else:
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
        offspring_1 = ReynoldsIteration(self.cur_generation, 0, offspring_genome_1)
        offspring_2 = ReynoldsIteration(self.cur_generation, 0, offspring_genome_2)
        offspring_3 = ReynoldsIteration(self.cur_generation, 0, offspring_genome_3)
        offspring_4 = ReynoldsIteration(self.cur_generation, 0, offspring_genome_4)
        return offspring_1, offspring_2, offspring_3, offspring_4

    def advance_generation(self, crossover_type=0):
        next_gen = []

        # Kill off the least performing chromosomes and randomly breed the survivors in pairs
        self.cull_bottom_half()
        random.shuffle(self.survivors)

        while self.survivors:
            parent_1 = self.survivors.pop()
            parent_2 = self.survivors.pop()
            child_list = self.breed_iterations(parent_1, parent_2, crossover_type)
            for child in child_list:
                next_gen.append(child)

        self.iteration_list = next_gen
        self.cur_generation += 1


def move_all_boids_genetic(boid_list, flock_manager, board_dims, playtime, iteration_chromosome=ReynoldsChromosome()):
    chromosome = iteration_chromosome
    # Create a dictionary of all boids by id to quickly search for boids by id values extracted from flock
    flock_list = flock_manager.get_flocks()
    boid_dict = dict()
    for boid in boid_list:
        boid_dict.update({boid.get_id(): boid})

    for boid in boid_list:
        idx = 0
        for flock in flock_list:
            b_id = boid.get_id()
            if b_id in flock:
                # Calculate components of our velocity based on various rules
                v1 = cohesion_rule(boid, flock, boid_dict) * chromosome.cohesion_gene
                v2 = separation_rule(boid, flock, boid_dict, chromosome.separation_gene)
                v3 = alignment_rule(boid, flock, boid_dict) * chromosome.alignment_gene
                # Special rule to check if goal is visible
                if boid.is_object_visible(boid.calc_angle_from_pos(boid.nearest_goal.get_position())):
                    v4 = tend_to_position(boid, boid.nearest_goal.get_position()) * chromosome.goal_seeking_gene
                    # If you are close to the goal, get a boost to goal velocity
                    if abs(boid.calc_dist_to_object(boid.nearest_goal.get_position())) < boid.too_close:
                        v4 *= 2
                else:
                    v4 = Vector2D(random.randrange(0.0, 2.0), random.randrange(0.0, 2.0))
                v5 = avoid_walls(boid, board_dims) * chromosome.wall_avoidance_gene

                dv = v1 + v2 + v3 + v4 + v5
                dv *= boid.get_divergence()

                boid.update_velocity(dv)
                boid.update_position(board_dims)

                boid.update_cost(boid_list, flock, flock_manager.get_thetas()[idx], flock_manager.get_goal_thetas()[idx],
                                 flock_manager.get_centroids()[idx], playtime)
            idx += 1


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
def separation_rule(boid, flock, boid_dict, avoidance_gene):
    avoid = Vector2D()
    for mem in flock:
        member = boid_dict.get(mem)
        if member is not boid and member is not None:
            if abs(member.get_position() - boid.get_position()) < boid.too_close:
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
def avoid_walls(boid, board_dims):
    wall_avoid = Vector2D(0, 0)
    boid_pos = boid.get_position()
    if boid_pos.x < boid.height * 2:
        wall_avoid.x = boid.height
    elif boid_pos.x >= board_dims[0] - boid.height * 2:
        wall_avoid.x = -boid.height

    if boid_pos.y < boid.height * 2:
        wall_avoid.y = boid.height
    elif boid_pos.y >= board_dims[1] - boid.height * 2:
        wall_avoid.y = -boid.height

    return wall_avoid
