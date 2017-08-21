import pygame, math, time, parser

#Constants
BLACK = (  0,   0,   0)
WHITE = (255, 255, 255)
BLUE =  (  0,   0, 255)
GREEN = (  0, 120,   0)
RED =   (255,   0,   0)
GREY =  (130, 130, 130)
LIGHT_GREY = (190, 190, 190)
SCREEN_SIZE = [1600, 1200]
RADIUS = 50
FINAL_RADIUS = 75
CLICK_RANGE = 25
OP_EPS = '*'
circles = []
counter = None
total = None
font = pygame.font.SysFont("monospace", 30)

def add_node(pos, name, lines=None):
    cir = Circle(pos, name)
    if lines != None:
        cir.lines = lines
    circles.append(cir)
    return name

def circle_arrange(index, total):
    return [int((math.cos((index * (2*math.pi))/total)
    * 500) + (SCREEN_SIZE[0]/2)),
    int((math.sin((index * (2*math.pi))/total)
    * 500) + (SCREEN_SIZE[1]/2))]

def find_circle(name):
    for circle in circles:
        if circle.text == name:
            return circle
    return None

def add_value(previous, value):
    global counter
    counter += 1

    new_name = "q" + str(counter)
    new_circle = add_node(circle_arrange(counter, total), new_name)
    find_circle(new_circle).toggle_final()

    for cir in previous:
        circle = find_circle(cir)
        if circle != None:
            circle.lines.append(Line(circle.text, new_name, value))
            circle.toggle_final(False)
    return new_name

def recursive_parser(element, previous):
    global counter
    if previous == None:
        previous = add_node(circle_arrange(0, total), "Start")

    element_type, value = element.get_element()
    if element_type == parser.Token_ENUM.TK_LETTER \
    or element_type == parser.Token_ENUM.TK_DIGIT:
        return add_value([previous], value)
    elif element_type == parser.Token_ENUM.OP_OR:
        previous_1 = add_value([previous], OP_EPS)
        previous_2 = add_value([previous], OP_EPS)
        new_1 = recursive_parser(value[0], previous_1)
        new_2 = recursive_parser(value[1], previous_2)
        return add_value([new_1, new_2], OP_EPS)
    elif element_type == parser.Token_ENUM.OP_KLEENE:
        mid_start = add_value([previous], OP_EPS)
        mid_end = recursive_parser(value, mid_start)
        find_circle(mid_end).lines.append(Line(mid_end, mid_start, OP_EPS))
        return add_value([mid_end, previous], OP_EPS)
    elif element_type == parser.Token_ENUM.OP_CONCAT:
        left = recursive_parser(value[0], previous)
        eps = add_value([left], OP_EPS)
        right = recursive_parser(value[1], eps)
        return add_value([right], OP_EPS)

def regex_to_nfa(regex):
    global counter
    global total
    global circles
    counter = 0
    tree, total = parser.parse(regex)
    circles = []
    recursive_parser(tree, None)

class Message:
    def __init__(self):
        self.font = pygame.font.SysFont("monospace", 60)
        self.label = None
        self.val = 0
    def start(self, text):
        self.val = time.clock()
        self.label = self.font.render(text, 1, BLACK)
    def draw(self, screen, pos):
        if self.val > (time.clock() - 3):
            try:
                screen.blit(self.label,
                    (pos[0] - (self.label.get_width() / 2),
                    pos[1] - self.label.get_height()))
            except:
                pass

class Input_Message:
    def __init__(self):
        self.label = None

    def draw(self, screen, text):
        self.label = font.render(text, 1, BLACK)
        screen.blit(self.label,
            (SCREEN_SIZE[0] - self.label.get_width(),
            SCREEN_SIZE[1] - self.label.get_height()))

class Graph_Display:
    def __init__(self):
        self.labels = [font.render("DFA", 1, BLACK),
            font.render("NFA", 1, BLACK)]

    def draw(self, screen, graph_state):
        label = self.labels[0 if graph_state == "DFA" else 1]
        screen.blit(label,
            (SCREEN_SIZE[0] - label.get_width(), 0))

class Object:
    def draw(self, screen, selected):
        raise NotImplementedError("Draw not implemented")

    def is_clicked(self, pos):
        raise NotImplementedError("Is_clicked not implemented")

    def edit(self, test):
        raise NotImplementedError("Edit not implemented")

    def update_pos(self, pos):
        raise NotImplementedError("Update not implemented")

class Circle(Object):
    def __init__(self, pos, text):
        Object.__init__(self)
        self.pos = pos
        self.color = BLUE
        self.text = text
        self.final = False
        self.lines = []

    def update_pos(self, pos):
        self.pos = pos

    def is_clicked(self, pos):
        return math.sqrt(math.pow(pos[0] - self.pos[0], 2) +
                            math.pow(pos[1] - self.pos[1], 2)) < RADIUS

    def toggle_final(self, val=None):
        self.final = not self.final if val == None else val

    def draw(self, screen, selected):
        color = self.color if selected != self else RED
        pygame.draw.circle(screen, color,
        self.pos, RADIUS)
        if self.final:
            pygame.draw.circle(screen, color,
                self.pos, FINAL_RADIUS, 10)

        rendered_font = font.render(self.text, 1, WHITE)
        screen.blit(rendered_font, (self.pos[0] - rendered_font.get_width()/2,
                    self.pos[1] - rendered_font.get_height()/2))

    def edit(self, text):
        for circle in circles:
            if circle.text == text:
                raise ValueError("Circle name already exists.")
        self.text = text
        for circle in circles:
            for line in circle.lines:
                if line.circle_b == self.text:
                    line.circle_b = text
                    line.get_circle_refs()
                if line.circle_a == self.text:
                    line.circle_a = text
                    line.get_circle_refs()

    def is_final(self):
        if self.final:
            return True
        for line in self.lines:
            for transition in line.text.split("|"):
                if transition == OP_EPS:
                    if find_circle(line.circle_b).is_final():
                        return True
        return False

class Line(Object):
    def __init__(self, circle_a, circle_b, text):
        Object.__init__(self)
        self.circle_a = circle_a
        self.circle_b = circle_b
        self.circle_a_ref = find_circle(circle_a)
        self.circle_b_ref = find_circle(circle_b)
        self.text = str(text)

    def get_circle_refs(self):
        self.circle_a_ref = find_circle(self.circle_a)
        self.circle_b_ref = find_circle(self.circle_b)

    def draw(self, screen, selected):
        #TODO: Rendering the same font multiple times is slow
        rendered_font = font.render(self.text, 1, BLACK)
        color = RED if selected == self else LIGHT_GREY
        try:
            if self.circle_a_ref != self.circle_b_ref:
                start = self.circle_a_ref.pos
                end_c = self.circle_b_ref.pos

                x = end_c[0] - start[0]
                y = end_c[1] - start[1]
                ratio = (100 if self.circle_b_ref.final else 75) / math.sqrt(x * x + y * y)
                end = (end_c[0] - x * ratio, end_c[1] - y * ratio)

                rotation = math.atan2(start[1]-end[1],
                    end[0]-start[0]) + (math.pi / 2)
                arrow_size = 25
                radians_dif = 2 * math.pi / 3

                pygame.draw.line(screen,
                color , start, end_c, 10)
                pygame.draw.polygon(screen, color,
                ((end[0] + arrow_size * math.sin(rotation),
                end[1] + arrow_size * math.cos(rotation)),
                (end[0] + arrow_size * math.sin(rotation - radians_dif),
                end[1] + arrow_size * math.cos(rotation - radians_dif)),
                (end[0] + arrow_size * math.sin(rotation + radians_dif),
                end[1] + arrow_size * math.cos(rotation + radians_dif))))
                screen.blit(rendered_font, (end[0] - arrow_size * math.sin(rotation),
                end[1] - arrow_size * math.cos(rotation)))
            else:
                x = self.circle_a_ref.pos[0] - (rendered_font.get_width()/2)
                y = self.circle_a_ref.pos[1] - (RADIUS * 2) - 30
                pygame.draw.circle(screen, color,
                    (self.circle_a_ref.pos[0],
                    self.circle_a_ref.pos[1] - RADIUS),
                    RADIUS, 10)
                screen.blit(rendered_font, (x, y))
        except:
            self.get_circle_refs()

    def edit(self, text):
        self.text = text

    def update_pos(self, pos):
        pass

    def is_clicked(self, pos):
        try:
            circle_a = self.circle_a_ref.pos
            circle_b = self.circle_b_ref.pos

            if circle_a != circle_b:
                dxL = circle_b[0] - circle_a[0]
                dyL = circle_b[1] - circle_a[1]
                dxP = pos[0] - circle_a[0]
                dyP = pos[1] - circle_a[1]

                squareLen = dxL * dxL + dyL * dyL
                dotProd   = dxP * dxL + dyP * dyL
                crossProd = dyP * dxL - dxP * dyL

                distance = math.fabs(crossProd) / math.sqrt(squareLen)
                return (distance <= CLICK_RANGE and dotProd >= 0 and
                        dotProd <= squareLen)
            else:
                return math.sqrt(((pos[0] - circle_a[0]) ** 2) + \
                ((pos[1] - (circle_a[1] - RADIUS)) ** 2)) < RADIUS
        except Exception as e:
            self.get_circle_refs()
            print(e)
