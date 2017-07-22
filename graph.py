import pygame
import math

#Init game
pygame.init()
font = pygame.font.SysFont("monospace", 30)

BLACK = (  0,   0,   0)
WHITE = (255, 255, 255)
BLUE =  (  0,   0, 255)
GREEN = (  0, 255,   0)
RED =   (255,   0,   0)
GREY =  (175, 175, 175)

screen_size = [1000, 1000]
screen = pygame.display.set_mode(screen_size)

pygame.display.set_caption("Graphs v0.1")

clock = pygame.time.Clock()
done = False
drag = False
input_text = ""
selected = None

radius = 50
last_clicks = []
circles = []
lines = []

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
                            math.pow(pos[1] - self.pos[1], 2)) < radius

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
                            circles.remove(circle)
                #Middle_click adds transition
                elif last_clicks[1]:
                    for index, circle in enumerate(list(circles)):
                        if circle.is_clicked(pos):
                            if selected != index:
                                lines.append(
                                    Line(
                                    circles[selected], circles[index],
                                    font.render( '%s' % input_text, 1, BLACK)))
                                input_text = ""
                    circles[selected].deselect()
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
            for index, circle in enumerate(list(circles)):
                #Selects circle
                if circle.is_clicked(pos):
                    if last_clicks[0]:
                        if selected != None:
                            circles[selected].deselect()
                        selected = index
                        circles[index].select()
                        drag = True

        if event.type == pygame.MOUSEMOTION:
            if drag:
                circles[selected].update_pos(pos)

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
        screen.blit(line.label, ((line.circle_a.pos[0] + line.circle_b.pos[0])/2,
                    (line.circle_a.pos[1] + line.circle_b.pos[1])/2))

    for circle in circles:
        pygame.draw.circle(screen, circle.color, circle.pos, radius)
        screen.blit(circle.label, (circle.pos[0] - circle.label.get_width()/2,
                    circle.pos[1] - circle.label.get_height()/2))

    label = font.render(input_text, 1, BLACK)
    screen.blit(label,
        (screen_size[0]-label.get_width(), screen_size[1]-label.get_height()))

    pygame.display.flip()

pygame.quit()
