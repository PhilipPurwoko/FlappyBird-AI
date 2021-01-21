import pygame
import neat
import time
import os

from bird import Bird
from floor import Floor
from pipe import Pipe


class Engine:
    WIN_WIDTH = 375
    WIN_HEIGHT = 600

    PIPE_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'pipe.png')))
    FLOOR_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'base.png')))
    BG_IMG = pygame.transform.scale(pygame.image.load(os.path.join('imgs', 'bg.png')), (WIN_WIDTH, WIN_HEIGHT))
    BIRD_IMGS = [
        pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'bird1.png'))),
        pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'bird2.png'))),
        pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'bird3.png')))
    ]

    def draw_window(self, win, bird, pipes, floor):
        win.blit(self.BG_IMG, (0, 0))
        bird.draw(pygame, win)
        for pipe in pipes:
            pipe.draw(win)
        floor.draw(win)
        pygame.display.update()

    def start(self):
        # Game Objects
        bird = Bird(self.BIRD_IMGS, 100, 200)
        floor = Floor(self.FLOOR_IMG, 530)
        pipes = [Pipe(pygame, self.PIPE_IMG, 500)]

        # Pygame Misc
        win = pygame.display.set_mode((self.WIN_WIDTH, self.WIN_HEIGHT))
        clock = pygame.time.Clock()
        score = 0

        run = True
        while run:
            clock.tick(30)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False
            
            # Animation
            # bird.move()
            add_pipe = False
            removed_pipe = []
            for pipe in pipes:
                if pipe.collide(pygame, bird):
                    pass

                if pipe.x + pipe.PIPE_TOP.get_width() < 0:
                    removed_pipe.append(pipe)

                if not pipe.passed and pipe.x < bird.x:
                    pipe.passed = True
                    add_pipe = True

                pipe.move()

            if add_pipe:
                score += 1
                pipes.append(Pipe(pygame, self.PIPE_IMG, 500))
            for pipe in removed_pipe:
                pipes.remove(pipe)

            floor.move()
            self.draw_window(win, bird, pipes, floor)
        pygame.quit()
        quit()
