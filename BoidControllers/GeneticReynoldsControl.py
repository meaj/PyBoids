"""
Pyboids - GeneticReynoldsControl
 * A version of Craig Reynolds Boids that has weights attached to each velocity vector. These weights are fed to a
 * genetic algorithm that will be optimizing for high score and high number of survivors after M minutes
 * Copyright (c) 2019 Meaj
"""
import copy
import random
import statistics
from BoidControllers.BoidRules import *


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


class ReynoldsSpecies:
    def __init__(self, generation_number=0, species_number=0, genome=ReynoldsChromosome()):
        self.generation_number = generation_number
        self.species_number = species_number
        self.survivor_number = 0
        self.live_time = 0
        self.genome = genome
        self.performance = 1.0

    def update_live_time(self, val):
        self.live_time = val

    def update_survivors(self, val):
        self.survivor_number = val

    def update_performance(self, value):
        self.performance = value

    def generate_divergence_value(self):
        return random.randrange(int(-self.genome[5]*100), int(self.genome[5]*100))/100

    def get_genome(self):
        return self.genome

    def get_id(self):
        return self.species_number

    def get_performance(self):
        return self.performance

    def get_livetime(self):
        return self.live_time

    def get_survivors(self):
        return self.survivor_number

    def set_id(self, value):
        self.species_number = value


class ReynoldsGeneticAlgorithm:
    def __init__(self, generation_number, max_species, mutation_rate):
        self.generation_number = 0  # This tracks which generation we are on
        self.max_generation = generation_number  # This indicates which generation to terminate on
        self.max_species = max_species  # This indicates how many species to create every generation
        self.mutation_rate = mutation_rate  # This is the rate at which genes will randomly mutate
        self.genetic_history_best_performers = []  # This tracks the chromosomes used by the best of each iteration
        self.genetic_history = []  # This tracks the chromosomes used by each iteration each generation
        self.species_list = []  # This tracks the iterations used each generation, this is cleared once per gen
        self.survivors = []  # This tracks the iterations that survive after each culling

        for i in range(self.max_species):
            self.species_list.append(ReynoldsSpecies(self.generation_number, i + 1, ReynoldsChromosome(
                random.uniform(-1, 1), random.uniform(-1, 1), random.uniform(-1, 1),
                random.uniform(-1, 1), random.uniform(-1, 1), random.uniform(-1, 1))))

    def get_species_list(self):
        return self.species_list

    def cull_bottom_half(self):
        species_performances = []
        self.survivors = []

        for species in self.species_list:
            species_performances.append(species.performance)
        median = statistics.median(species_performances)

        for species in self.species_list:
            if species.performance >= median and len(self.survivors) < self.max_species/2:
                print("Gen {} species {} survived and will breed".format(self.generation_number, species.get_id()))
                self.survivors.append(species)
            if len(self.survivors) == self.max_species/2:
                break

    @staticmethod
    # Similar to crossover_genes, but allows each potential swap to be a average of the parent's genes
    def gene_commingling(chromosome_1, chromosome_2):
        overlap = random.randrange(1, len(chromosome_1) + 1)
        for i in range(0, overlap):
            beta = random.random()
            t_gene = (beta * chromosome_1[i]) + ((1 - beta) * chromosome_2[i])
            o_gene = chromosome_1[i]
            chromosome_1[i] = t_gene
            beta = random.random()
            t_gene = (beta * o_gene) + ((1 - beta) * chromosome_2[i])
            chromosome_2[i] = t_gene
        return chromosome_1, chromosome_2

    @staticmethod
    # Similar to crossover_genes, but allows each potential swap to be a average of the parent's genes
    def winner_take_all_gene_commingling(chromosome_1, chromosome_2):
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
        return chromosome

    # Creates 4 children from 2 parents
    def breed_species(self, species_1, species_2, crossover_type=0):
        # Crossover
        # copy is use to ensure that the list values are exchanged and not the list values themselves
        child_1, child_2 = copy.copy(species_1.get_genome()), copy.copy(
            species_2.get_genome())
        if crossover_type == 1:
            child_3, child_4 = self.binary_choice_crossover_genes(
                copy.copy(species_1.get_genome()), copy.copy(species_2.get_genome()))
        elif crossover_type == 2:
            child_3, child_4 = self.unbounded_gene_commingling(
                copy.copy(species_1.get_genome()), copy.copy(species_2.get_genome()))
        elif crossover_type == 3:
            child_3, child_4 = self.bounded_gene_commingling(
                copy.copy(species_1.get_genome()), copy.copy(species_2.get_genome()))
        elif crossover_type == 4:
            child_3, child_4 = self.alternating_gene_commingling(
                copy.copy(species_1.get_genome()), copy.copy(species_2.get_genome()))
        elif crossover_type == 5:
            child_3, child_4 = self.winner_take_all_gene_commingling(
                copy.copy(species_1.get_genome()), copy.copy(species_2.get_genome()))
        elif crossover_type == 6:
            child_3, child_4 = self.gene_commingling(
                copy.copy(species_1.get_genome()), copy.copy(species_2.get_genome()))
        else:
            child_3, child_4 = self.crossover_genes(
                copy.copy(species_1.get_genome()), copy.copy(species_2.get_genome()))
        # Mutations
        child_1 = self.mutate_genes(child_1)
        child_2 = self.mutate_genes(child_2)
        child_3 = self.mutate_genes(child_3)
        child_4 = self.mutate_genes(child_4)

        # Iteration creation
        child_species_1 = ReynoldsSpecies(self.generation_number, 0, child_1)
        child_species_2 = ReynoldsSpecies(self.generation_number, 0, child_2)
        child_species_3 = ReynoldsSpecies(self.generation_number, 0, child_3)
        child_species_4 = ReynoldsSpecies(self.generation_number, 0, child_4)

        # Shuffling a list of the children prevents the first child from always being chosen if there are too many
        children = [child_species_1, child_species_2, child_species_3, child_species_4]
        random.shuffle(children)
        return children

    def advance_generation(self, crossover_type=0):
        if self.generation_number + 1 != self.max_generation:
            next_gen = []

            # Kill off the least performing chromosomes and randomly breed the survivors in pairs
            self.cull_bottom_half()
            random.shuffle(self.survivors)

            # Randomly select two survivors and collect children until the species maximum is reached
            # A backup parent is chosen if there is an odd number of parents, may cause inbreeding which will be neat
            backup = random.choice(self.survivors)
            while len(next_gen) != len(self.species_list):
                parent_1 = self.survivors.pop()
                if self.survivors:
                    parent_2 = self.survivors.pop()
                else:
                    parent_2 = backup
                child_list = self.breed_species(parent_1, parent_2, crossover_type)
                for child in child_list:
                    if len(next_gen) == len(self.species_list):
                        break
                    next_gen.append(child)

            self.species_list = next_gen
        self.generation_number += 1


class SeededReynoldsGeneticAlgorithm(ReynoldsGeneticAlgorithm):
    def __init__(self, generation_number, max_species, mutation_rate, seed):
        super().__init__(generation_number, max_species, mutation_rate)
        self.iteration_list = []
        for i in range(self.max_species):
            self.iteration_list.append(ReynoldsSpecies(self.generation_number, i + 1,
                                                       ReynoldsChromosome(random.uniform(-1, 1) + seed[0],
                                                                          random.uniform(-1, 1) + seed[1],
                                                                          random.uniform(-1, 1) + seed[2],
                                                                          random.uniform(-1, 1) + seed[3],
                                                                          random.uniform(-1, 1) + seed[4],
                                                                          random.uniform(-1, 1) + seed[5])))


def move_all_boids_genetic(boid_list, flock_manager, board_dims, playtime, iteration_chromosome=ReynoldsChromosome()):
    chromosome = iteration_chromosome
    # Create a dictionary of all boids by id to quickly search for boids by id values extracted from flock
    flock_list = flock_manager.get_flocks()

    for boid in boid_list:
        for flock in flock_list:
            if boid in flock.flock_members:
                # Calculate components of our velocity based on various rules
                if len(boid.connected_boids) > 1:
                    v1 = cohesion_rule(boid, boid.connected_boids) * chromosome.cohesion_gene
                    v2 = separation_rule(boid, boid.connected_boids) * chromosome.separation_gene
                    v3 = alignment_rule(boid, boid.connected_boids) * chromosome.alignment_gene
                else:
                    v1 = v2 = v3 = Vector2D()
                # Special rule to check if goal is visible
                if boid.is_object_visible(boid.calc_angle_from_pos(boid.nearest_goal.get_position())):
                    v4 = tend_to_position(boid, boid.nearest_goal.get_position())
                else:
                    v4 = Vector2D(random.randrange(-MAX_FORCE, MAX_FORCE), random.randrange(-MAX_FORCE, MAX_FORCE))
                v4 *= chromosome.goal_seeking_gene
                v5 = avoid_walls(boid, board_dims) * chromosome.wall_avoidance_gene

                dv = v1 + v2 + v3 + v4 + v5

                dv *= boid.get_divergence()

                boid.update_velocity(dv)
                boid.update_position(board_dims)

                boid.update_cost(flock, playtime)



