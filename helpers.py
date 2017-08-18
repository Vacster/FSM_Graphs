import pygame, math, time

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
circles = []
font = pygame.font.SysFont("monospace", 30)

def find_circle(name):
    for circle in circles:
        if circle.text == name:
            return circle
    return None

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

class Object:
    def draw(self, screen, selected):
        raise NotImplementedError("Draw not implemented")

    def is_clicked(self, pos):
        raise NotImplementedError("Is_clicked not implemented")

    def edit(self, test):
        raise NotImplementedError("Edit not implemented")

    def update_pos(self, pos):
        raise NotImplementedError("Update not implemented")

class Graph_Display:
    def __init__(self):
        self.labels = [font.render("DFA", 1, BLACK),
            font.render("NFA", 1, BLACK)]

    def draw(self, screen, graph_state):
        label = self.labels[0 if graph_state == "DFA" else 1]
        screen.blit(label,
            (SCREEN_SIZE[0] - label.get_width(), 0))

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

    def toggle_final(self):
        self.final = not self.final

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

class Line(Object):
    def __init__(self, circle_a, circle_b, text):
        Object.__init__(self)
        self.circle_a = circle_a
        self.circle_b = circle_b
        self.circle_a_ref = find_circle(circle_a)
        self.circle_b_ref = find_circle(circle_b)
        self.text = text

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
                screen.blit(rendered_font, (x, y))
                pygame.draw.circle(screen, color,
                    (self.circle_a_ref.pos[0],
                    self.circle_a_ref.pos[1] - RADIUS),
                    RADIUS, 10)
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
                vec_line = (circle_b[0] - circle_a[0],
                            circle_b[1] - circle_a[1])
                vec_point = (pos[0] - circle_a[0],
                            pos[1] - circle_a[1])
                vec_extra = (pos[0] - circle_b[0],
                            pos[1] - circle_b[1])

                square_len = vec_point[0] * vec_line[0] \
                            + vec_line[1] * vec_line[1]
                dot_prod = vec_point[0] * vec_line[0] \
                            + vec_point[1] * vec_line[1]
                cross_prod = vec_point[1] * vec_line[0] \
                            - vec_point[0] * vec_line[1]

                distance_end_1 = math.sqrt(vec_point[0] ** 2
                                + vec_point[1] ** 2)
                distance_end_2 = math.sqrt(vec_extra[0] ** 2
                                + vec_extra[1] ** 2)

                if dot_prod < 0:
                    return distance_end_1 <= CLICK_RANGE
                if dot_prod > square_len:
                    return distance_end_2 <= CLICK_RANGE

                distance = math.fabs(cross_prod) / math.sqrt(square_len)
                return distance <= CLICK_RANGE
            else:
                return math.sqrt(((pos[0] - circle_a[0]) ** 2) + \
                ((pos[1] - (circle_a[1] - RADIUS)) ** 2)) < RADIUS
        except Exception as e:
            self.get_circle_refs()
            print(e)
