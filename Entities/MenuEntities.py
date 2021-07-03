from Constants import *


class Button:
    def __init__(self, text, x_pos, y_pos, width, height, function=None):
        self.x_pos = x_pos
        self.y_pos = y_pos
        self.width = width
        self.height = height
        self.color = LIGHT_GREY
        self.function = function
        self.text_rect = pygame.Rect(x_pos, y_pos, width, height)
        self.text = text
        self.font = pygame.font.SysFont('courier new', 12, bold=True)
        self.text_surf = self.font.render(text, False, GREEN)

    def set_pos(self, x, y):
        self.x_pos = x
        self.y_pos = y

    def check_click(self):
        mouse = pygame.mouse.get_pos()
        click = pygame.mouse.get_pressed()
        if self.x_pos < mouse[0] < self.x_pos + self.width and self.y_pos < mouse[1] < self.y_pos + self.height:
            self.color = GREY
            if click[0] == 1 and self.function is not None:
                self.function()
        else:
            self.color = LIGHT_GREY

    def draw_button(self, screen):
        pygame.draw.rect(screen, self.color, (self.x_pos, self.y_pos, self.width, self.height))
        button_surf, button_rect = text_setup(self.text, self.font)
        button_rect.center = (self.x_pos + self.width / 2, self.y_pos + self.height / 2)
        screen.blit(button_surf, button_rect)


class InputBox:
    def __init__(self, in_text, title_text, x_pos, y_pos, width, height):
        self.text_rect = pygame.Rect(x_pos + width, y_pos, width, height)
        self.width = width
        self.in_text = in_text
        self.font = pygame.font.SysFont('courier new', 12, bold=True)
        self.text_surf = self.font.render(in_text, False, GREEN)
        self.input_active = False
        self.title_rect = pygame.Rect(x_pos - width, y_pos, width, height)
        self.title_surf = self.font.render(title_text, False, GREEN)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            # noinspection PyArgumentList
            if self.text_rect.collidepoint(event.pos) and not self.input_active:
                self.input_active = True
            else:
                self.input_active = False

        if event.type == pygame.KEYDOWN:
            if self.input_active:
                if event.key == pygame.K_RETURN:
                    self.input_active = False
                elif event.key == pygame.K_BACKSPACE:
                    self.in_text = self.in_text[:-1]
                elif event.key in ENTRY_KEYS:
                    self.in_text += event.unicode
                self.text_surf = self.font.render(self.in_text, True, GREEN)

    def set_pos(self, x, y):
        self.title_rect.centerx = x - self.width
        self.title_rect.centery = y
        self.text_rect.centerx = x + self.width
        self.text_rect.centery = y

    def draw_box(self, screen):
        screen.blit(self.text_surf, self.text_rect)
        screen.blit(self.title_surf, self.title_rect)
        pygame.draw.rect(screen, GREY, self.title_rect, 2)
        pygame.draw.rect(screen, LIGHT_GREY, self.text_rect, 2)