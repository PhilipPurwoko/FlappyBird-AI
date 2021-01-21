import pygame
import neat
import os
import pickle

from bird import Bird
from floor import Floor
from pipe import Pipe
from bg import Bg

pygame.font.init()


class Engine:
    running_generation = 0
    WIN_WIDTH = 375
    WIN_HEIGHT = 600

    TEXT_FONT = pygame.font.SysFont('comicsans', 30)
    PIPE_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'pipe.png')))
    FLOOR_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'base.png')))
    BG_IMG = pygame.transform.scale(pygame.image.load(os.path.join('imgs', 'bg.png')), (WIN_WIDTH, WIN_HEIGHT))
    BIRD_IMGS = [
        pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'bird1.png'))),
        pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'bird2.png'))),
        pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'bird3.png')))
    ]

    def draw_window(self, win, bg, birds, pipes, floor, score, gen):
        bg.draw(win)
        for bird in birds:
            bird.draw(pygame, win)
        
        for pipe in pipes:
            pipe.draw(win)
        
        floor.draw(win)

        text_score = self.TEXT_FONT.render('Score : ' + str(score), True, (255, 255, 255))
        win.blit(text_score, (self.WIN_WIDTH - 10 - text_score.get_width(), 10))

        text_gen = self.TEXT_FONT.render('Generation : ' + str(gen), True, (255, 255, 255))
        win.blit(text_gen, (self.WIN_WIDTH - 10 - text_gen.get_width(), 30))

        pygame.display.update()

    def game(self, genomes, config):
        score = 0
        nets = []
        generation = []
        birds = []

        for _, gen in genomes:
            net = neat.nn.FeedForwardNetwork.create(gen, config)
            nets.append(net)
            birds.append(Bird(self.BIRD_IMGS, 100, 200))
            gen.fitness = 0
            generation.append(gen)

        # Game Objects
        bg = Bg(self.BG_IMG)
        floor = Floor(self.FLOOR_IMG, 530)
        pipes = [Pipe(pygame, self.PIPE_IMG, 500)]

        # Pygame Misc
        win = pygame.display.set_mode((self.WIN_WIDTH, self.WIN_HEIGHT))
        clock = pygame.time.Clock()

        run = True
        while run:
            clock.tick(30)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False
                    pygame.quit()
                    quit()

            pipe_ind = 0
            if (len(birds)) > 0:
                if (len(pipes)) > 1 and birds[0].x > pipes[0].x + pipes[0].PIPE_TOP.get_width():
                    pipe_ind = 1
            else:
                self.running_generation += 1
                break

            for x, bird in enumerate(birds):
                bird.move()
                generation[x].fitness += 0.1
                outputs = nets[x].activate((bird.y, abs(bird.y - pipes[pipe_ind].height), abs(bird.y - pipes[pipe_ind].bottom)))
                if outputs[0] > 0.5:
                    bird.flap()
            
            # Animation
            add_pipe = False
            removed_pipe = []
            for pipe in pipes:
                for x, bird in enumerate(birds):
                    if pipe.collide(pygame, bird):
                        generation[x].fitness -= 1
                        birds.pop(x)
                        nets.pop(x)
                        generation.pop(x)

                    if not pipe.passed and pipe.x < bird.x:
                        pipe.passed = True
                        add_pipe = True

                if pipe.x + pipe.PIPE_TOP.get_width() < 0:
                    removed_pipe.append(pipe)

                pipe.move()

            if add_pipe:
                score += 1
                for g in generation:
                    g.fitness += 5
                pipes.append(Pipe(pygame, self.PIPE_IMG, 400))
            
            for pipe in removed_pipe:
                pipes.remove(pipe)

            for x, bird in enumerate(birds):
                if bird.y + bird.img.get_height() >= 530 or bird.y < 0:
                    birds.pop(x)
                    nets.pop(x)
                    generation.pop(x)

            floor.move()
            bg.move()
            self.draw_window(win, bg, birds, pipes, floor, score, self.running_generation)

            if score > 30:
                print('Target Acquired! (50++ Flappy Score)')
                with open('best_bird.pkl', 'wb') as file:
                    pickle.dump(nets[0], file)
                    break

    def start(self):
        config = neat.config.Config(
            neat.DefaultGenome,
            neat.DefaultReproduction,
            neat.DefaultSpeciesSet,
            neat.DefaultStagnation,
            'config-feedforward.txt'
        )

        population = neat.Population(config)
        population.add_reporter(neat.StdOutReporter(True))
        population.add_reporter(neat.StatisticsReporter())

        winner = population.run(self.game, 50)
        print('The Best Genome :')
        print(winner)
