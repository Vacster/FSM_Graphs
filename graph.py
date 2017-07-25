from fysom import Fysom
import pickle
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
SCREEN_SIZE = [1600, 1200]
RADIUS = 50

screen = pygame.display.set_mode(SCREEN_SIZE)

pygame.display.set_caption("Graphs v0.5")

clock = pygame.time.Clock()
done = False
drag = False
input_text = ""
selected = None

last_clicks = []
circles = []
lines = []

def line_exists(circle_a, circle_b, value):
    for line in lines:
        if line.circle_a == circle_a \
        and line.circle_b == circle_b \
        and line.text != value:
            return True
    return False

def circle_exists(text):
    for circle in circles:
        if circle.text == text:
            return True
    return False

def erase_line(circle):
    num = []
    for line in lines:
        if line.circle_a == circle.text or line.circle_b == circle.text:
            num.append(line)
    for x in num:
        lines.remove(x)

def get_events():
    events = []
    for line in lines:
        events.append([line.text, line.circle_a, line.circle_b])
    return events

def is_final(state):
    for circle in circles:
        if circle.text == state:
            return circle.final

def find_circle(name):
    for circle in circles:
        if circle.text == name:
            return circle
    return None

class Circle:
    def __init__(self, pos, text):
        self.pos = pos
        self.color = BLUE
        self.text = text
        self.final = False
    def update_pos(self, pos):
        self.pos = pos
    def select(self):
        self.color = RED
    def deselect(self):
        self.color = GREEN if self.final else BLUE
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
    def __init__(self, circle_a, circle_b, text):
        self.circle_a = circle_a
        self.circle_b = circle_b
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
                            text = '%s' % input_text[:5]
                            if selected != None \
                            and len(input_text) > 0 \
                            and not line_exists(selected, circles[index], text):
                                lines.append(
                                    Line(
                                    selected.text, circles[index].text,
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
                    if not circle_exists(text):
                        circles.append(
                            Circle(pos,
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
                if "save" in input_text:
                    try:
                        f = open(input_text[5:], "w")
                        pickle.dump(circles, f)
                        pickle.dump(lines, f)
                        f.close()
                    except:
                        print "Error saving file."
                    input_text = ""
                elif "load" in input_text:
                    try:
                        f = open(input_text[5:], "r")
                        circles = pickle.load(f)
                        lines = pickle.load(f)
                        f.close()
                        for circle in circles:
                            if circle.color == RED:
                                selected = circle
                                break
                    except:
                        print "Error loading file."
                    input_text = ""
                elif "edit" in input_text and selected != None:
                    splitted = input_text.split(" ")
                    if len(splitted) == 2:
                        for line in lines:
                            if line.circle_a == selected.text:
                                line.circle_a = splitted[1]
                            if line.circle_b == selected.text:
                                line.circle_b = splitted[1]
                        selected.text = splitted[1]
                        input_text = ""
                    else:
                        #Trash, Node, Line, New
                        for line in lines:
                            if line.text == splitted[2] \
                            and line.circle_a == selected.text \
                            and line.circle_b == splitted[1]:
                                line.text = splitted[3]
                                input_text = ""
                elif "delete" in input_text and selected != None:
                    splitted = input_text.split(" ")
                    remove = None
                    for line in lines:
                        if line.text == splitted[2] \
                        and line.circle_a == selected.text \
                        and line.circle_b == splitted[1]:
                            remove = line
                    lines.remove(remove)
                    input_text = ""
                elif selected != None:
                    try:
                        fsm = Fysom(initial=selected.text,
                        events=get_events())
                        for c in input_text:
                            fsm.trigger(c)
                        print("Last State:", fsm.current, is_final(fsm.current))
                    except:
                        print "Something went wrong when evaluating."
            else:
                input_text+=event.unicode

    #Drawing
    for line in lines:
        #TODO: Rendering the same font multiple times is wasteful
        rendered_font = font.render(line.text, 1, BLACK)
        circle_a = find_circle(line.circle_a)
        circle_b = find_circle(line.circle_b)
        if circle_a != circle_b:
            pygame.draw.line(screen, GREY, circle_a.pos,
                circle_b.pos, 10)
            x = (circle_a.pos[0]/4) + (3 * circle_b.pos[0] / 4)
            y = (circle_a.pos[1]/4) + (3 * circle_b.pos[1] / 4)
            screen.blit(rendered_font, (x, y))
        else:
            pygame.draw.ellipse(screen, GREY,
                [circle_a.pos[0] - RADIUS,
                circle_a.pos[1] - (RADIUS * 2),
                RADIUS * 2, RADIUS * 2], 10)
            x = circle_a.pos[0] - (rendered_font.get_width()/2)
            y = circle_a.pos[1] - (RADIUS * 2) - rendered_font.get_height()
            screen.blit(rendered_font, (x, y))

    for circle in circles:
        pygame.draw.circle(screen, circle.color, circle.pos, RADIUS)
        rendered_font = font.render(circle.text, 1, WHITE)
        screen.blit(rendered_font, (circle.pos[0] - rendered_font.get_width()/2,
                    circle.pos[1] - rendered_font.get_height()/2))

    label = font.render(input_text, 1, BLACK)
    screen.blit(label,
        (SCREEN_SIZE[0]-label.get_width(), SCREEN_SIZE[1]-label.get_height()))

    pygame.display.flip()

pygame.quit()
