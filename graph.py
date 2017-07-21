import pygame
import math

pygame.init()

BLACK = (  0,   0,   0)
WHITE = (255, 255, 255)
BLUE =  (  0,   0, 255)
GREEN = (  0, 255,   0)
RED =   (255,   0,   0)

size = [1000, 1000]
screen = pygame.display.set_mode(size)

pygame.display.set_caption("Graphs v0.1")

clock = pygame.time.Clock()
done = False
drag = False
selected = None

radius = 50
last_clicks = []
circles = []

class Circle:
    def __init__(self, pos):
        self.pos = pos
    def update_pos(self, pos):
        self.pos = pos

while not done:
    screen.fill(WHITE)
    clock.tick(24)

    for event in pygame.event.get():
        done = event.type == pygame.QUIT
        pos = pygame.mouse.get_pos()
        clicks = pygame.mouse.get_pressed()

        if event.type == pygame.MOUSEBUTTONUP:
            if not drag:
                if last_clicks[2]:
                    found = False
                    for circle in list(circles):
                        if math.sqrt(math.pow(pos[0] - circle.pos[0], 2) + math.pow(pos[1] - circle.pos[1], 2)) < radius:
                            circles.remove(circle)
                elif last_clicks[0]:
                    circles.append(Circle(pos))
            drag = False
            last_clicks = [0,0,0]

        if event.type == pygame.MOUSEBUTTONDOWN:
            last_clicks = clicks
            for index, circle in enumerate(circles):
                if math.sqrt(math.pow(pos[0] - circle.pos[0], 2) + math.pow(pos[1] - circle.pos[1], 2)) < radius and last_clicks[0]:
                    selected = index
                    drag = True

        if event.type == pygame.MOUSEMOTION:
            if drag:
                circles[selected].update_pos(pos)

    for circle in circles:
        pygame.draw.circle(screen, BLUE, circle.pos, radius)

    pygame.display.flip()

pygame.quit()
