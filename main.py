import pygame
import sys
from constants import *
from the_moss import TheMossManager
import numpy

pygame.init()
pygame.display.set_caption("Da Star")
clock = pygame.time.Clock()
FPS = 60

screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
the_moss = TheMossManager(screen)


def draw():
    screen.fill(BLACK)
    the_moss.update()
    pygame.display.flip()

def main():
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

        draw()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()