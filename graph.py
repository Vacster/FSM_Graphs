import automaton, pickle, pygame, math, pybutton

class Message:
    def __init__(self):
        self.font = pygame.font.SysFont("monospace", 60)
        self.label = None
        self.val = 0
    def start(self, text):
        self.val = 600
        self.label = self.font.render(text, 1, BLACK)
    def draw(self, screen, pos):
        if self.val > 0:
            try:
                screen.blit(self.label,
                    (pos[0] - (self.label.get_width() / 2),
                    pos[1] - self.label.get_height()))
                self.val-=1
            except:
                pass

class Circle:
    def __init__(self, pos, text):
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
        if self.final:
            self.final = False
        else:
            self.final = True

    def draw(self):
        color = circle.color if selected != self else RED
        pygame.draw.circle(screen, color,
        circle.pos, RADIUS)
        if self.final:
            pygame.draw.circle(screen, color,
                circle.pos, FINAL_RADIUS, 10)

        rendered_font = font.render(circle.text, 1, WHITE)
        screen.blit(rendered_font, (circle.pos[0] - rendered_font.get_width()/2,
                    circle.pos[1] - rendered_font.get_height()/2))

class Line:
    def __init__(self, circle_a, circle_b, text):
        self.circle_a = circle_a
        self.circle_b = circle_b
        self.circle_a_ref = find_circle(circle_a)
        self.circle_b_ref = find_circle(circle_b)
        self.text = text

    def get_circle_refs(self):
        self.circle_a_ref = find_circle(self.circle_a)
        self.circle_b_ref = find_circle(self.circle_b)

    def draw(self):
        #TODO: Rendering the same font multiple times is slow
        rendered_font = font.render(line.text, 1, BLACK)
        color = RED if selected == self else LIGHT_GREY
        try:
            if self.circle_a_ref != self.circle_b_ref:
                start = self.circle_a_ref.pos
                end = self.circle_b_ref.pos
                pygame.draw.line(screen,
                    color , start, end, 10)

                x = end[0] - start[0]
                y = end[1] - start[1]
                ratio = (100 if self.circle_b_ref.final else 75) / math.sqrt(x * x + y * y)
                end = (end[0] - x * ratio, end[1] - y * ratio)

                rotation = math.atan2(start[1]-end[1],
                    end[0]-start[0]) + (math.pi / 2)
                arrow_size = 25
                radians_dif = 2 * math.pi / 3

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
                pygame.draw.circle(screen, color,
                    (self.circle_a_ref.pos[0],
                    self.circle_a_ref.pos[1] - RADIUS),
                    RADIUS, 10)
                x = self.circle_a_ref.pos[0] - (rendered_font.get_width()/2)
                y = self.circle_a_ref.pos[1] - (RADIUS * 2) - 30
                screen.blit(rendered_font, (x, y))
        except:
            self.get_circle_refs()

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
            #return self.is_clicked(pos)

#Init game
pygame.init()
font = pygame.font.SysFont("monospace", 30)

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

graph_state = "DFA"
message = Message()
clock = pygame.time.Clock()
pygame.display.set_caption("Graphs v0.5")
screen = pygame.display.set_mode(SCREEN_SIZE)
change_button = pybutton.PygButton((50, 50, 100, 50), 'Change')

done = False
drag = False
selected = None
input_text = ""
last_clicks = []
circles = []

def lose_selection():
    global selected
    selected = None

def line_exists(circle_a, circle_b, value):
    for circle in circles:
        for line in circle.lines:
            if graph_state == "DFA":
                if line.circle_a == circle_a.text \
                and line.text == value:
                    return True
            elif graph_state == "NFA":
                if line.circle_a == circle_a.text \
                and line.circle_b == circle_b.text \
                and line.text == value:
                    return True
    return False

def circle_exists(text):
    for circle in circles:
        if circle.text == text:
            return True
    return False

def erase_circle(circle):
    tmp = []
    for circlex in circles:
        for line in circlex.lines:
            if (line.circle_a == circle.text) or (line.circle_b == circle.text):
                tmp.append(line)
    for circle in circles:
        for x in tmp:
            try:
                circle.lines.remove(x)
            except:
                continue

def get_finals():
    finals = []
    for circle in circles:
        for line in circle.lines:
            for transition in line.text.split("|"):
                if transition == '*':
                    if find_circle(line.circle_b).final:
                        finals.append(circle.text)
        if circle.final:
            finals.append(circle.text)
    return finals

def get_events():
    tmp_dict = dict()
    for circle in circles:
        if graph_state == "DFA":
            tmp = dict()
            for line in circle.lines:
                for x in line.text.split("|"):
                    tmp[x] = line.circle_b
            if tmp:
                tmp_dict[circle.text] = tmp
        elif graph_state == "NFA":
            tmp = dict()
            tmp_2 = dict()
            for line in circle.lines:
                for x in line.text.split("|"):
                    if x == '*':
                        for y, eps_circle in get_epsilon(find_circle(line.circle_b)):
                            tmp.setdefault(y,[]).append(eps_circle)
                    else:
                        tmp.setdefault(x,[]).append(line.circle_b)
            for key, val in tmp.items():
                tmp_2[key] = set(val)
            if tmp_2:
                tmp_dict[circle.text] = tmp_2
    return tmp_dict

def get_epsilon(circle):
    for line in circle.lines:
        for x in line.text.split("|"):
            if x == '*':
                for y, z in get_epsilon(find_circle(line.circle_b)):
                    yield y, z
            else:
                yield x, line.circle_b

def find_circle(name):
    for circle in circles:
        if circle.text == name:
            return circle
    return None

def get_circle_name(name):
    if len(name) > 1:
        tmp = ""
        for text in name:
            tmp += "|"
            tmp += text
        tmp += "|"
        return tmp
    else:
        x, = name
        return x

def add_node(pos, name, lines=None):
    cir = Circle(pos, name)
    if lines != None:
        cir.lines = lines
    circles.append(cir)
    return cir

#Main Loop
while not done:
    clock.tick(60) #Wut
    screen.fill(GREY)

    for event in pygame.event.get():
        done = event.type == pygame.QUIT
        pos = pygame.mouse.get_pos()
        clicks = pygame.mouse.get_pressed()

        if 'click' in change_button.handleEvent(event):
            if graph_state == "DFA":
                graph_state = "NFA"
            else:
                try:
                    N = automaton.NFA(get_events(), selected.text, get_finals())
                    M = automaton.convertNFAtoDFA(N)
                    circles = []
                    index = 1
                    """ Arranges nodes in a circle """
                    for node, data in M.delta.items():
                        circle_name = get_circle_name(node)
                        tmp_lines = []
                        for val, circle_b in data.items():
                            tmp_lines.append(
                                Line(circle_name, get_circle_name(circle_b),
                                    val))
                        add_node((int((math.cos((index * (2*math.pi))/len(M.delta))
                        * 500) + (SCREEN_SIZE[0]/2)),
                        int((math.sin((index * (2*math.pi))/len(M.delta))
                        * 500) + (SCREEN_SIZE[1]/2))), circle_name, tmp_lines)
                        index += 1
                    initialState, = M.q0
                    for circle in circles:
                        for final in M.F:
                            if get_circle_name(final) == circle.text:
                                circle.toggle_final()
                                break
                        if initialState == circle.text:
                            selected = circle
                    graph_state = "DFA"
                except AttributeError as e:
                    message.start("Starting node must be selected.")
                    print(e)
        else:
            if event.type == pygame.MOUSEBUTTONUP:
                if not drag:
                    #Right_click removes circle
                    if last_clicks[2]:
                        found = False
                        for circle in list(circles):
                            if circle.is_clicked(pos):
                                erase_circle(circle)
                                circles.remove(circle)
                            for line in list(circle.lines):
                                if line.is_clicked(pos):
                                    circle.lines.remove(line)
                            lose_selection()
                    #Middle_click adds transition
                    elif last_clicks[1]:
                        for index, circle in enumerate(list(circles)):
                            if circle.is_clicked(pos):
                                text = '%s' % input_text[:5]
                                if selected != None \
                                and len(input_text) > 0 \
                                and not line_exists(selected, circles[index], text):
                                    selected.lines.append(
                                        Line(
                                        selected.text, circles[index].text,
                                        text))
                                    input_text = ""
                                elif selected == None:
                                    circle.toggle_final()
                        lose_selection()
                    #Left_click creates circle
                    elif last_clicks[0]:
                        if len(input_text) > 0:
                            text = '%s' % input_text[:5]
                            if not circle_exists(text):
                                add_node(pos, text)
                                input_text = ""
                drag = False
                last_clicks = [0,0,0]

            if event.type == pygame.MOUSEBUTTONDOWN:
                last_clicks = clicks
                if last_clicks[0]:
                    for circle in circles:
                        if circle.is_clicked(pos):
                            selected = circle
                            drag = True
                            break
                        for line in circle.lines:
                            if line.is_clicked(pos):
                                selected = line
                                drag = True
                                break

            if event.type == pygame.MOUSEMOTION:
                if drag and isinstance(selected, Circle):
                    selected.update_pos(pos)

        #Write input_text
        if event.type == pygame.KEYDOWN:
            #Backspace
            if event.unicode == "\b":
                input_text = input_text[:-1]
            elif event.unicode == "\r":
                if "save" in input_text:
                    try:
                        f = open(input_text[5:], "wb")
                        pickle.dump(circles, f)
                        pickle.dump(graph_state, f)
                        f.close()
                    except Exception as e:
                        message.start("Error saving file.")
                        print("Error saving file.", e)
                    input_text = ""
                elif "load" in input_text:
                    try:
                        f = open(input_text[5:], "rb")
                        circles = pickle.load(f)
                        graph_state = pickle.load(f)
                        f.close()
                        for circle in circles:
                            if circle.color == RED:
                                selected = circle
                                break
                    except Exception as e:
                        message.start("Error loading file.")
                        print("Error loading file.", e)
                    input_text = ""
                elif "edit" in input_text:
                    try:
                        new_text = selected.text = input_text[5:10]
                        if isinstance(selected, Circle):
                            for circle in circles:
                                for line in lines:
                                    if line.circle_b == selected.text:
                                        line.circle_b = new_text
                                        line.get_circle_refs()
                                    if line.circle_a == selected.text:
                                        line.circle_a = new_text
                                        line.get_circle_refs()
                        else:
                            selected.text == new_text
                        input_text = ""
                    except Exception as e:
                        print("Couldn't rename.", e)
                elif selected != None:
                    try:
                        if graph_state == "DFA":
                            N = automaton.DFA(get_events(), selected.text, get_finals())
                        elif graph_state == "NFA":
                            N = automaton.NFA(get_events(), selected.text, get_finals())
                        message.start(str(N.inLanguage(input_text)))
                    except Exception as e:
                        message.start("False")
                        print("False.", e)
            else:
                input_text+=event.unicode

        #Drawing
        """Separating draws so the lines are below the circles"""
        for circle in circles:
            for line in circle.lines:
                line.draw()
        for circle in circles:
            circle.draw()

        label = font.render(input_text, 1, BLACK)
        screen.blit(label,
            (SCREEN_SIZE[0] - label.get_width(),
            SCREEN_SIZE[1] - label.get_height()))

        label = font.render(graph_state, 1, BLACK)
        screen.blit(label,
            (SCREEN_SIZE[0] - label.get_width(), 0))

        message.draw(screen, (SCREEN_SIZE[0] / 2, SCREEN_SIZE[1]))
        change_button.draw(screen)
        pygame.display.flip()

pygame.quit()
