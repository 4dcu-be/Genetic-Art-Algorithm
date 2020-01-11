from PIL import Image
from evol import Evolution, Population

import random
import os
from copy import deepcopy

from painting import Painting


def score(x: Painting) -> float:
    current_score = x.image_diff(x.target_image)
    print(".", end='', flush=True)
    return current_score


def pick_best_and_random(pop, maximize=False):
    evaluated_individuals = tuple(filter(lambda x: x.fitness is not None, pop))
    if len(evaluated_individuals) > 0:
        mom = max(evaluated_individuals, key=lambda x: x.fitness if maximize else -x.fitness)
    else:
        mom = random.choice(pop)
    dad = random.choice(pop)
    return mom, dad


def pick_random(pop):
    mom = random.choice(pop)
    dad = random.choice(pop)
    return mom, dad


def mutate_painting(x: Painting, rate=0.04, swap=0.5, sigma=1) -> Painting:
    x.mutate_triangles(rate=rate, swap=swap, sigma=sigma)
    return deepcopy(x)


def mate(mom: Painting, dad: Painting):
    child_a, child_b = Painting.mate(mom, dad)

    return deepcopy(child_a)


def print_summary(pop, img_template="output%d.png", checkpoint_path="output") -> Population:
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
    checkpoint_path = "./starry_night2/"
    image_template = os.path.join(checkpoint_path, "drawing_%05d.png")
    target_image = Image.open(target_image_path).convert('RGBA')

    num_triangles = 150
    population_size = 200

    pop = Population(chromosomes=[Painting(num_triangles, target_image, background_color=(255, 255, 255)) for _ in range(population_size)],
                     eval_function=score, maximize=False, concurrent_workers=6)

    early_evo = (Evolution()
                 .survive(fraction=0.05)
                 .breed(parent_picker=pick_random, combiner=mate, population_size=population_size)
                 .mutate(mutate_function=mutate_painting, rate=0.20, swap=0.75)
                 .evaluate(lazy=False)
                 .apply(print_summary,
                        img_template=image_template,
                        checkpoint_path=checkpoint_path))

    mid_evo = (Evolution()
               .survive(fraction=0.15)
               .breed(parent_picker=pick_best_and_random, combiner=mate, population_size=population_size)
               .mutate(mutate_function=mutate_painting, rate=0.15, swap=0.5)
               .evaluate(lazy=False)
               .apply(print_summary,
                      img_template=image_template,
                      checkpoint_path=checkpoint_path))

    late_evo = (Evolution()
                .survive(fraction=0.05)
                .breed(parent_picker=pick_best_and_random, combiner=mate, population_size=population_size)
                .mutate(mutate_function=mutate_painting, rate=0.05, swap=0.25)
                .evaluate(lazy=False)
                .apply(print_summary,
                       img_template=image_template,
                       checkpoint_path=checkpoint_path))

    final_evo = (Evolution()
                 .survive(fraction=0.025)
                 .breed(parent_picker=pick_best_and_random, combiner=mate, population_size=population_size)
                 .mutate(mutate_function=mutate_painting, rate=0.05, swap=0, sigma=0.15)
                 .evaluate(lazy=False)
                 .apply(print_summary,
                        img_template=image_template,
                        checkpoint_path=checkpoint_path))

    evo_step_5 = (Evolution()
                  .survive(fraction=0.025)
                  .breed(parent_picker=pick_best_and_random, combiner=mate, population_size=population_size)
                  .mutate(mutate_function=mutate_painting, rate=0.03, swap=0, sigma=0.12)
                  .evaluate(lazy=False)
                  .apply(print_summary,
                         img_template=image_template,
                         checkpoint_path=checkpoint_path))

    pop = pop.evolve(early_evo, n=200)
    pop = pop.evolve(mid_evo, n=300)
    pop = pop.evolve(late_evo, n=1000)
    pop = pop.evolve(final_evo, n=1500)
    pop = pop.evolve(evo_step_5, n=2000)
