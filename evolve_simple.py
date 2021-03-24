from PIL import Image
from evol import Evolution, Population

import random
import os
from copy import deepcopy

from painting import Painting


def score(x: Painting) -> float:
    """
    Calculate the distance to the target image

    :param x: a Painting object to calculate the distance for
    :return: distance based on pixel differences
    """
    current_score = x.image_diff(x.target_image)
    print(".", end='', flush=True)
    return current_score


def pick_best_and_random(pop, maximize=False):
    """
    Here we select the best individual from a population and pair it with a random individual from a population

    :param pop: input population
    :param maximize: when true a higher fitness score is better, otherwise a lower score is considered better
    :return: a tuple with the best and a random individual
    """
    evaluated_individuals = tuple(filter(lambda x: x.fitness is not None, pop))
    if len(evaluated_individuals) > 0:
        mom = max(evaluated_individuals, key=lambda x: x.fitness if maximize else -x.fitness)
    else:
        mom = random.choice(pop)
    dad = random.choice(pop)
    return mom, dad


def mutate_painting(x: Painting, rate=0.04, swap=0.5, sigma=1) -> Painting:
    """
    This will mutate a painting by randomly applying changes to the triangles.

    :param x: Painting to mutate
    :param rate: the chance a triangle will be mutated
    :param swap: the chance a pair of traingles will be swapped
    :param sigma: the strenght of the mutation (how much a triangle can be changed)
    :return: New painting object with mutations
    """
    x.mutate_triangles(rate=rate, swap=swap, sigma=sigma)
    return deepcopy(x)


def mate(mom: Painting, dad: Painting):
    """
    Takes two paintings, the mom and dad, to create a new painting object made up with triangles from both parents

    :param mom: One parent painting
    :param dad: Other parent painting
    :return: new Painting with features from both parents
    """
    child_a, child_b = Painting.mate(mom, dad)

    return deepcopy(child_a)


def print_summary(pop, img_template="output%d.png", checkpoint_path="output") -> Population:
    """
    This will print a summary of the population fitness and store an image of the best individual of the current
    generation. Every fifty generations the entire population is stored.

    :param pop: Population
    :param img_template: a template for the name of the output images, should contain %d as the number of the generation is included
    :param checkpoint_path: directory to write output.
    :return: The input population
    """
    avg_fitness = sum([i.fitness for i in pop.individuals])/len(pop.individuals)

    print("\nCurrent generation %d, best score %f, pop. avg. %f " % (pop.generation,
                                                                     pop.current_best.fitness,
                                                                     avg_fitness))
    img = pop.current_best.chromosome.draw()
    img.save(img_template % pop.generation, 'PNG')

    if pop.generation % 50 == 0:
        pop.checkpoint(target=checkpoint_path, method='pickle')

    return pop


if __name__ == "__main__":
    target_image_path = "./img/starry_night_half.jpg"
    checkpoint_path = "./starry_night/"
    image_template = os.path.join(checkpoint_path, "drawing_%05d.png")
    target_image = Image.open(target_image_path).convert('RGBA')

    num_triangles = 150
    population_size = 200

    pop = Population(chromosomes=[Painting(num_triangles, target_image, background_color=(255, 255, 255)) for _ in range(population_size)],
                     eval_function=score, maximize=False, concurrent_workers=6)

    evolution = (Evolution()
                 .survive(fraction=0.05)
                 .breed(parent_picker=pick_best_and_random, combiner=mate, population_size=population_size)
                 .mutate(mutate_function=mutate_painting, rate=0.05, swap=0.25)
                 .evaluate(lazy=False)
                 .callback(print_summary,
                           img_template=image_template,
                           checkpoint_path=checkpoint_path))

    pop = pop.evolve(evolution, n=5000)

