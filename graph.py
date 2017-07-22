import pygame
import math

#Init game
pygame.init()
font = pygame.font.SysFont("monospace", 30)

#Constants
BLACK = (  0,   0,   0)
WHITE = (255, 255, 255)
BLUE =  (  0,   0, 255)
GREEN = (  0, 255,   0)
RED =   (255,   0,   0)
GREY =  (175, 175, 175)
SCREEN_SIZE = [1000, 1000]
RADIUS = 50

screen = pygame.display.set_mode(SCREEN_SIZE)

pygame.display.set_caption("Graphs v0.2")

clock = pygame.time.Clock()
done = False
drag = False
input_text = ""
selected = None

last_clicks = []
circles = []
lines = []

def line_exists(circle_a, circle_b):
    for line in lines:
        if line.circle_a == circle_a and line.circle_b == circle_b:
            return True
    return False

def erase_line(circle):
    num = []
    for line in lines:
        if line.circle_a == circle or line.circle_b == circle:
            num.append(line)
    for x in num:
        lines.remove(x)

class Circle:
    def __init__(self, pos, font):
        self.pos = pos
        self.color = BLUE
        self.label = font
    def update_pos(self, pos):
        self.pos = pos
    def select(self):
        self.color = RED
    def deselect(self):
        self.color = BLUE
    def is_clicked(self, pos):
        return math.sqrt(math.pow(pos[0] - self.pos[0], 2) +
                            math.pow(pos[1] - self.pos[1], 2)) < RADIUS

class Line:
    def __init__(self, circle_a, circle_b, font):
        self.circle_a = circle_a
        self.circle_b = circle_b
        self.label = font

#Main Loop
while not done:
    screen.fill(WHITE)
    clock.tick(24)

    for event in pygame.event.get():
        done = event.type == pygame.QUIT
        pos = pygame.mouse.get_pos()
        clicks = pygame.mouse.get_pressed()

        if event.type == pygame.MOUSEBUTTONUP:
            if not drag:
                #Right_click removes circle
                if last_clicks[2]:
                    found = False
                    for circle in list(circles):
                        if circle.is_clicked(pos):
                            erase_line(circle)
                            circles.remove(circle)
                #Middle_click adds transition
                elif last_clicks[1]:
                    for index, circle in enumerate(list(circles)):
                        if circle.is_clicked(pos):
                            if selected != circles[index] and \
                            not line_exists(selected, circles[index]):
                                lines.append(
                                    Line(
                                    selected, circles[index],
                                    font.render( '%s' % input_text, 1, BLACK)))
                                input_text = ""
                    if selected != None:
                        selected.deselect()
                        selected = None
                #Left_click creates circle
                elif last_clicks[0]:
                    circles.append(Circle(pos,
                        font.render( '%s' % input_text, 1, WHITE)))
                    input_text = ""
            drag = False
            last_clicks = [0,0,0]

        if event.type == pygame.MOUSEBUTTONDOWN:
            last_clicks = clicks
            for index, circle in enumerate(circles):
                #Selects circle
                if circle.is_clicked(pos):
                    if last_clicks[0]:
                        if selected != None:
                            selected.deselect()
                        selected = circles[index]
                        selected.select()
                        drag = True

        if event.type == pygame.MOUSEMOTION:
            if drag:
                selected.update_pos(pos)

        #Write input_text
        if event.type == pygame.KEYDOWN:
            if event.unicode == "\b":
                input_text = input_text[:-1]
            else:
                if len(input_text) < 5:
                    input_text+=event.unicode

    #Drawing
    for line in lines:
        pygame.draw.line(screen, GREY, line.circle_a.pos, line.circle_b.pos, 10)
        screen.blit(line.label, ((line.circle_a.pos[0]+line.circle_b.pos[0])/2,
                    (line.circle_a.pos[1] + line.circle_b.pos[1])/2))

    for circle in circles:
        pygame.draw.circle(screen, circle.color, circle.pos, RADIUS)
        screen.blit(circle.label, (circle.pos[0] - circle.label.get_width()/2,
                    circle.pos[1] - circle.label.get_height()/2))

    label = font.render(input_text, 1, BLACK)
    screen.blit(label,
        (SCREEN_SIZE[0]-label.get_width(), SCREEN_SIZE[1]-label.get_height()))

    pygame.display.flip()

pygame.quit()
