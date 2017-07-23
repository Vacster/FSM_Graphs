from fysom import Fysom
import pygame
import math

#Init game
pygame.init()
font = pygame.font.SysFont("monospace", 30)

#Constants
BLACK = (  0,   0,   0)
WHITE = (255, 255, 255)
BLUE =  (  0,   0, 255)
GREEN = (  0, 120,   0)
RED =   (255,   0,   0)
GREY =  (175, 175, 175)
SCREEN_SIZE = [1000, 1000]
RADIUS = 50

screen = pygame.display.set_mode(SCREEN_SIZE)

pygame.display.set_caption("Graphs v0.3")

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

def get_events():
    events = []
    for line in lines:
        events.append([line.text, line.circle_a.text, line.circle_b.text])
    return events

def is_final(state):
    for circle in circles:
        if circle.text == state:
            return circle.final

class Circle:
    def __init__(self, pos, font, text):
        self.pos = pos
        self.color = BLUE
        self.label = font
        self.text = text
        self.final = False
    def update_pos(self, pos):
        self.pos = pos
    def select(self):
        self.color = RED
    def deselect(self):
        self.color = BLUE
    def is_clicked(self, pos):
        return math.sqrt(math.pow(pos[0] - self.pos[0], 2) +
                            math.pow(pos[1] - self.pos[1], 2)) < RADIUS
    def toggle_final(self):
        if self.final:
            self.color = BLUE
            self.final = False
        else:
            self.color = GREEN
            self.final = True

class Line:
    def __init__(self, circle_a, circle_b, font, text):
        self.circle_a = circle_a
        self.circle_b = circle_b
        self.label = font
        self.text = text

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
                            if selected != None \
                            and len(input_text) > 0 \
                            and not line_exists(selected, circles[index]):
                                text = '%s' % input_text[:5]
                                lines.append(
                                    Line(
                                    selected, circles[index],
                                    font.render(text, 1, BLACK),
                                    text))
                                input_text = ""
                            elif selected == None:
                                circle.toggle_final()
                    if selected != None:
                        selected.deselect()
                        selected = None
                #Left_click creates circle
                elif last_clicks[0] and len(input_text) > 0:
                    text = '%s' % input_text[:5]
                    circles.append(
                        Circle(pos,
                        font.render(text , 1, WHITE),
                        text))
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
            #Backspace
            if event.unicode == "\b":
                input_text = input_text[:-1]
            elif event.unicode == "\r":
                if selected != None:
                    fsm = Fysom(initial=selected.text,
                    events=get_events())
                    for c in input_text:
                        fsm.trigger(c)
                        print(fsm.current)
            else:
                input_text+=event.unicode

    #Drawing
    for line in lines:
        if line.circle_a != line.circle_b:
            pygame.draw.line(screen, GREY, line.circle_a.pos,
                line.circle_b.pos, 10)
            x = (line.circle_a.pos[0]/4) + (3 * line.circle_b.pos[0] / 4)
            y = (line.circle_a.pos[1]/4) + (3 * line.circle_b.pos[1] / 4)
            screen.blit(line.label, (x, y))
        else:
            pygame.draw.ellipse(screen, GREY,
                [line.circle_a.pos[0] - RADIUS,
                line.circle_a.pos[1] - (RADIUS * 2),
                RADIUS * 2, RADIUS * 2], 10)
            x = line.circle_a.pos[0] - (line.label.get_width()/2)
            y = line.circle_a.pos[1] - (RADIUS * 2) - line.label.get_height()
            screen.blit(line.label, (x, y))

    for circle in circles:
        pygame.draw.circle(screen, circle.color, circle.pos, RADIUS)
        screen.blit(circle.label, (circle.pos[0] - circle.label.get_width()/2,
                    circle.pos[1] - circle.label.get_height()/2))

    label = font.render(input_text, 1, BLACK)
    screen.blit(label,
        (SCREEN_SIZE[0]-label.get_width(), SCREEN_SIZE[1]-label.get_height()))

    pygame.display.flip()

pygame.quit()
