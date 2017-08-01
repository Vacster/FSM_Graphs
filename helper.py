font = pygame.font.SysFont("monospace", 30)

class Circle:
    def __init__(self, pos, text):
        self.pos = pos
        self.color = BLUE
        self.text = text
        self.final = False
        self.lines = []

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
    def draw(self):
        pygame.draw.circle(screen, circle.color, circle.pos, RADIUS)
        rendered_font = font.render(circle.text, 1, WHITE)
        screen.blit(rendered_font, (circle.pos[0] - rendered_font.get_width()/2,
                    circle.pos[1] - rendered_font.get_height()/2))

class Line:
    def __init__(self, circle_a, circle_b, text):
        self.circle_a = circle_a
        self.circle_b = circle_b
        self.text = text

    def draw(self):
        #TODO: Rendering the same font multiple times is slow
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
