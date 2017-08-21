import automaton, pickle, pygame, math, pybutton, pyperclip
import helpers as H

pygame.init()

font = pygame.font.SysFont("monospace", 30)
graph_state = "DFA"
clock = pygame.time.Clock()
pygame.display.set_caption("Graphs v0.6")
screen = pygame.display.set_mode(H.SCREEN_SIZE)
change_button = pybutton.PygButton((50, 50, 100, 50), 'Change')
message = H.Message()
graph_display = H.Graph_Display()
input_message = H.Input_Message()

done = False
drag = False
selected = None
input_text = ""
last_clicks = []

def lose_selection():
    global selected
    selected = None

def line_exists(circle_a, circle_b, value):
    for circle in H.circles:
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
    for circle in H.circles:
        if circle.text == text:
            return True
    return False

def erase_circle(circle):
    tmp = []
    for circlex in H.circles:
        for line in circlex.lines:
            if (line.circle_a == circle.text) or (line.circle_b == circle.text):
                tmp.append(line)
    for circle in H.circles:
        for x in tmp:
            try:
                circle.lines.remove(x)
            except:
                continue

def get_finals():
    finals = []
    for circle in H.circles:
        if circle.is_final():
            finals.append(circle.text)
    return finals

def get_events():
    tmp_dict = dict()
    for circle in H.circles:
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
            for y, eps_circle in get_epsilon(circle):
                tmp.setdefault(y,[]).append(eps_circle)
            for key, val in tmp.items():
                tmp_2[key] = set(val)
            if tmp_2:
                tmp_dict[circle.text] = tmp_2
    return tmp_dict

def get_epsilon(circle):
    for line in circle.lines:
        for x in line.text.split("|"):
            if x == '*':
                for y, z in get_epsilon(H.find_circle(line.circle_b)):
                    yield y, z
            else:
                yield x, line.circle_b

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

#Main Loop
while not done:
    clock.tick(60) #Does almost nothing
    screen.fill(H.GREY)

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
                    H.circles = []
                    index = 1
                    """ Arranges nodes in a circle """
                    for node, data in M.delta.items():
                        circle_name = get_circle_name(node)
                        tmp_lines = []
                        for val, circle_b in data.items():
                            tmp_lines.append(
                                H.Line(circle_name, get_circle_name(circle_b),
                                    val))
                        H.add_node(H.circle_arrange(index, len(M.delta)),
                            circle_name, tmp_lines)
                        index += 1
                    initialState, = M.q0
                    for circle in H.circles:
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
                        for circle in list(H.circles):
                            if circle.is_clicked(pos):
                                erase_circle(circle)
                                H.circles.remove(circle)
                            for line in list(circle.lines):
                                if line.is_clicked(pos):
                                    circle.lines.remove(line)
                            lose_selection()
                    #Middle_click adds transition
                    elif last_clicks[1]:
                        for index, circle in enumerate(list(H.circles)):
                            if circle.is_clicked(pos):
                                text = '%s' % input_text[:5]
                                if selected != None \
                                and len(input_text) > 0 \
                                and not line_exists(selected, H.circles[index], text):
                                    selected.lines.append(
                                        H.Line(
                                        selected.text, H.circles[index].text,
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
                                H.add_node(pos, text)
                                input_text = ""
                            else:
                                message.start("Circle already exists")
                        else:
                            lose_selection()
                drag = False
                last_clicks = [0,0,0]

            if event.type == pygame.MOUSEBUTTONDOWN:
                last_clicks = clicks
                if last_clicks[0]:
                    for circle in H.circles:
                        if circle.is_clicked(pos):
                            selected = circle
                            drag = True
                            break
                        for line in circle.lines:
                            if line.is_clicked(pos):
                                selected = line
                                drag = True
                                break

            if event.type == pygame.MOUSEMOTION and drag:
                selected.update_pos(pos)

        #Write input_text
        if event.type == pygame.KEYDOWN:
            #Backspace
            if event.unicode == "\b":
                input_text = input_text[:-1]
            #Ctrl-V
            elif event.unicode == "":
                input_text += pyperclip.paste()
            #Ctrl-C
            elif event.unicode == "":
                input_text = ""
            #Enter
            elif event.unicode == "\r":
                if "save" in input_text:
                    try:
                        f = open(input_text[5:], "wb")
                        pickle.dump(H.circles, f)
                        pickle.dump(graph_state, f)
                        f.close()
                    except Exception as e:
                        message.start("Error saving file.")
                        print(e)
                    input_text = ""
                elif "load" in input_text:
                    try:
                        f = open(input_text[5:], "rb")
                        H.circles = pickle.load(f)
                        graph_state = pickle.load(f)
                        f.close()
                        for circle in H.circles:
                            if circle.color == H.RED:
                                selected = circle
                                break
                    except Exception as e:
                        message.start("Error loading file.")
                        print(e)
                    input_text = ""
                elif "edit" in input_text:
                    try:
                        new_text = input_text[5:10]
                        selected.edit(new_text)
                        input_text = ""
                        message.start("Renamed succesfully.")
                    except Exception as e:
                        message.start(str(e))
                elif "regex" in input_text:
                    try:
                        graph_state = "NFA"
                        H.regex_to_nfa(input_text[5:])
                        selected = H.find_circle("Start")
                    except Exception as e:
                        message.start("Error parsing regex.")
                        raise e
                    input_text = ""
                elif selected != None:
                    try:
                        if graph_state == "DFA":
                            N = automaton.DFA(get_events(), selected.text, get_finals())
                        elif graph_state == "NFA":
                            N = automaton.NFA(get_events(), selected.text, get_finals())
                        message.start(str(N.inLanguage(input_text)))
                    except Exception as e:
                        message.start("False")
                        print(e)
                else:
                    message.start("Initial state not selected.")
            else:
                input_text+=event.unicode

        #Drawing
        """Separating draws so the lines are below the H.circles"""
        for circle in H.circles:
            for line in circle.lines:
                line.draw(screen, selected)
        for circle in H.circles:
            circle.draw(screen, selected)

        input_message.draw(screen, input_text)
        graph_display.draw(screen, graph_state);

        message.draw(screen, (H.SCREEN_SIZE[0] / 2, H.SCREEN_SIZE[1]))
        change_button.draw(screen)
        pygame.display.flip()

pygame.quit()
