# cartoon_snake_menu.py
# Cartoonish Snake Game with Menu (Made by Ishika)
# Requirements: pygame
# Install: pip install pygame

import pygame
import random
import sys

pygame.init()
pygame.mixer.init()

# Animation variables
title_offset = 0
title_direction = 1
bounce_scale = 1.0
bounce_direction = 0

# ---------- Constants ----------
WIDTH, HEIGHT = 720, 480
BLOCK = 20

# FINAL THEMES (only 3)
BG_THEMES = [
    ("Classic Black", (15, 15, 30)),
    ("Sky Blue", (135, 206, 235)),
    ("Pink Pastel", (255, 192, 203))
]

# FINAL SNAKE COLORS (only 3)
SNAKE_COLORS = [
    ("Green", (46, 204, 113)),
    ("Yellow", (241, 196, 15)),
    ("Pink", (255, 105, 180))
]

DIFFICULTY = {
    "Easy": 6,
    "Medium": 10,
    "Hard": 14
}

# default selections
selected_bg = 0
selected_snake = 0
selected_diff = "Medium"

# ---------- Pygame Setup ----------
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("🐍 Cartoon Snake — Made by Ishika")
clock = pygame.time.Clock()

# Fonts
TITLE_FONT = pygame.font.SysFont("comicsansms", 48)
BIG_FONT = pygame.font.SysFont("comicsansms", 36)
MED_FONT = pygame.font.SysFont("comicsansms", 24)
SMALL_FONT = pygame.font.SysFont("comicsansms", 18)


# ---------- UI Helpers ----------
class Button:
    def __init__(self, rect, text, base_color, hover_color, font=MED_FONT, radius=12):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.base = base_color
        self.hover = hover_color
        self.font = font
        self.radius = radius
        self.is_hover = False

    def draw(self, surf):
        color = self.hover if self.is_hover else self.base
        # shadow
        shadow = self.rect.move(4, 6)
        pygame.draw.rect(surf, (0,0,0,40), shadow, border_radius=self.radius)
        pygame.draw.rect(surf, color, self.rect, border_radius=self.radius)

        txt = self.font.render(self.text, True, (255,255,255))
        surf.blit(txt, txt.get_rect(center=self.rect.center))

    def clicked(self, event):
        return event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.rect.collidepoint(pygame.mouse.get_pos())


# ---------- Game Classes ----------
class Snake:
    def __init__(self, color):
        self.color = color
        self.head_color = tuple(max(0,c-30) for c in color)
        self.reset()

    def reset(self):
        self.length = 3
        self.positions = [(WIDTH//2//BLOCK * BLOCK, HEIGHT//2//BLOCK * BLOCK)]
        self.direction = random.choice(["UP","DOWN","LEFT","RIGHT"])
        self.score = 0

    def get_head(self):
        return self.positions[0]

    def turn(self, dirc):
        if (dirc, self.direction) not in [
            ("UP","DOWN"),("DOWN","UP"),("LEFT","RIGHT"),("RIGHT","LEFT")
        ]:
            self.direction = dirc

    def move(self):
        x, y = self.get_head()

        if self.direction == "UP": y -= BLOCK
        elif self.direction == "DOWN": y += BLOCK
        elif self.direction == "LEFT": x -= BLOCK
        else: x += BLOCK

        x %= WIDTH
        y %= HEIGHT

        new = (x, y)
        self.positions.insert(0, new)
        if len(self.positions) > self.length:
            self.positions.pop()

    def check_self_collision(self):
        return self.get_head() in self.positions[1:]

    def draw(self, surf):
        for i, p in enumerate(self.positions):
            cx = p[0] + BLOCK//2
            cy = p[1] + BLOCK//2

            if i == 0:
                pygame.draw.circle(surf, self.head_color, (cx,cy), BLOCK//2)
                # Eyes
                eye_offset = 6
                pupil = 2
                if self.direction == "UP":
                    e1 = (cx-eye_offset, cy-6)
                    e2 = (cx+eye_offset, cy-6)
                elif self.direction == "DOWN":
                    e1 = (cx-eye_offset, cy+6)
                    e2 = (cx+eye_offset, cy+6)
                elif self.direction == "LEFT":
                    e1 = (cx-6, cy-eye_offset)
                    e2 = (cx-6, cy+eye_offset)
                else:
                    e1 = (cx+6, cy-eye_offset)
                    e2 = (cx+6, cy+eye_offset)

                pygame.draw.circle(surf, (255,255,255), e1, 4)
                pygame.draw.circle(surf, (255,255,255), e2, 4)
                pygame.draw.circle(surf, (20,20,20), e1, pupil)
                pygame.draw.circle(surf, (20,20,20), e2, pupil)

            else:
                pygame.draw.circle(surf, self.color, (cx,cy), BLOCK//2 - 2)


class Food:
    def __init__(self):
        self.randomize()

    def randomize(self):
        self.x = random.randint(0, (WIDTH - BLOCK)//BLOCK) * BLOCK
        self.y = random.randint(0, (HEIGHT - BLOCK)//BLOCK) * BLOCK

    def draw(self, surf):
        center = (self.x + BLOCK//2, self.y + BLOCK//2)
        pygame.draw.circle(surf, (231,76,60), center, BLOCK//2 - 3)
        pygame.draw.circle(surf, (255,150,150), center, 4)


# ---------- MENU ----------

def menu_screen():
    global selected_bg, selected_snake, selected_diff
    global title_offset, title_direction, bounce_scale, bounce_direction

    start_btn = Button(
        (WIDTH // 2 - 110,
         HEIGHT - 70,
         220, 60),
        "START",
        (255, 120, 160),
        (255, 150, 190)
    )

    base_x = 50
    gap = 220

    bg_buttons = [
        ((base_x + i*gap, 150, 180, 45), name, col)
        for i, (name, col) in enumerate(BG_THEMES)
    ]

    snake_buttons = [
        ((base_x + i*gap, 250, 180, 45), name, col)
        for i, (name, col) in enumerate(SNAKE_COLORS)
    ]

    diff_buttons = [
        ((base_x + i*gap, 350, 180, 45), lvl)
        for i, lvl in enumerate(["Easy", "Medium", "Hard"])
    ]

    rule_font = pygame.font.SysFont("comicsansms", 14)
    rule_text = rule_font.render("• Snake dies with self-collision.", True, (255,255,255))

    while True:
        screen.fill(BG_THEMES[selected_bg][1])
        mx, my = pygame.mouse.get_pos()

        # FLOATING TITLE ANIMATION
        title_offset += title_direction * 0.35
        if title_offset > 8 or title_offset < -8:
            title_direction *= -1

        # TITLE
        title = TITLE_FONT.render(" Cartoon Snake", True, (255,255,255))
        screen.blit(title, title.get_rect(center=(WIDTH//2, 50 + title_offset)))
        subtitle = SMALL_FONT.render("Made by Ishika ", True, (255,230,230))
        screen.blit(subtitle, subtitle.get_rect(center=(WIDTH//2, 90 + title_offset)))

        # BACKGROUND THEME
        screen.blit(MED_FONT.render("Background Theme:", True, (255,255,255)), (base_x, 120))
        for i, (rect, name, col) in enumerate(bg_buttons):
            r = pygame.Rect(rect)
            pygame.draw.rect(screen, col, (r.x+5, r.y+8, 35, 28), border_radius=8)
            screen.blit(SMALL_FONT.render(name, True, (255,255,255)), (r.x+50, r.y+10))
            if i == selected_bg:
                pygame.draw.rect(screen, (255,255,255), r.inflate(6,6), 3, border_radius=10)

        # SNAKE COLOR
        screen.blit(MED_FONT.render("Snake Color:", True, (255,255,255)), (base_x, 220))
        for i, (rect, name, col) in enumerate(snake_buttons):
            r = pygame.Rect(rect)
            pygame.draw.circle(screen, col, (r.x+20, r.y+23), 12)
            screen.blit(SMALL_FONT.render(name, True, (255,255,255)), (r.x+50, r.y+10))
            if i == selected_snake:
                pygame.draw.rect(screen, (255,255,255), r.inflate(6,6), 3, border_radius=10)

        # DIFFICULTY
        screen.blit(MED_FONT.render("Difficulty:", True, (255,255,255)), (base_x, 320))
        for i, (rect, lvl) in enumerate(diff_buttons):
            r = pygame.Rect(rect)
            base = (80,80,160) if selected_diff == lvl else (40,40,110)
            hov  = (100,100,200)
            btn = Button(rect, lvl, base, hov)
            btn.is_hover = r.collidepoint((mx,my))
            btn.draw(screen)
            if btn.is_hover and pygame.mouse.get_pressed()[0]:
                selected_diff = lvl

        # RULE (right bottom)
        screen.blit(rule_text, (WIDTH - rule_text.get_width() - 20, HEIGHT - 40))

        # START BUTTON ANIMATION
        start_btn.is_hover = start_btn.rect.collidepoint((mx,my))

        # Scale animation when clicked
        scaled_rect = pygame.Rect(
            start_btn.rect.x - (bounce_scale - 1) * 10,
            start_btn.rect.y - (bounce_scale - 1) * 5,
            start_btn.rect.w * bounce_scale,
            start_btn.rect.h * bounce_scale
        )

        pygame.draw.rect(
            screen,
            start_btn.base if not start_btn.is_hover else start_btn.hover,
            scaled_rect,
            border_radius=12
        )

        txt = start_btn.font.render(start_btn.text, True, (255,255,255))
        screen.blit(txt, txt.get_rect(center=scaled_rect.center))

        # EVENTS
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = pygame.mouse.get_pos()

                for i, (rect, _, _) in enumerate(bg_buttons):
                    if pygame.Rect(rect).collidepoint((mx,my)):
                        selected_bg = i

                for i, (rect, _, _) in enumerate(snake_buttons):
                    if pygame.Rect(rect).collidepoint((mx,my)):
                        selected_snake = i

                for rect, lvl in diff_buttons:
                    if pygame.Rect(rect).collidepoint((mx,my)):
                        selected_diff = lvl

                if start_btn.clicked(event):
                    bounce_direction = 1
                    return

        # UPDATE BOUNCE ANIMATION
        if bounce_direction == 1:
            bounce_scale += 0.08
            if bounce_scale >= 1.15:
                bounce_direction = -1
        elif bounce_direction == -1:
            bounce_scale -= 0.08
            if bounce_scale <= 1.0:
                bounce_direction = 0

        pygame.display.flip()
        clock.tick(30)


# ---------- Gameplay ----------
def play_game():
    bg = BG_THEMES[selected_bg][1]
    snake_color = SNAKE_COLORS[selected_snake][1]
    fps = DIFFICULTY[selected_diff]

    snake = Snake(snake_color)
    food = Food()

    # Back to Menu Button (top-right corner)
    back_btn = Button(
        (WIDTH - 120, 10, 110, 35),
        "MENU",
        (200, 80, 80),
        (230, 110, 110),
        font=SMALL_FONT
    )

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            # Check Back Button Click
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if back_btn.rect.collidepoint(pygame.mouse.get_pos()):
                    return  # ← goes back to menu
            if event.type == pygame.KEYDOWN:
                if   event.key == pygame.K_UP:    snake.turn("UP")
                elif event.key == pygame.K_DOWN:  snake.turn("DOWN")
                elif event.key == pygame.K_LEFT:  snake.turn("LEFT")
                elif event.key == pygame.K_RIGHT: snake.turn("RIGHT")
                elif event.key == pygame.K_ESCAPE: return

        snake.move()

        if snake.get_head() == (food.x, food.y):
            snake.length += 1
            snake.score += 10
            food.randomize()

        if snake.check_self_collision():
            show_game_over(snake.score, bg)
            return

        screen.fill(bg)
        snake.draw(screen)
        food.draw(screen)

        screen.blit(SMALL_FONT.render(f"Score: {snake.score}", True, (255,255,255)), (10,10))

        # Draw Back to Menu Button
        back_btn.is_hover = back_btn.rect.collidepoint(pygame.mouse.get_pos())
        back_btn.draw(screen)

        pygame.display.flip()
        clock.tick(fps)


def show_game_over(score, bg):
    for _ in range(50):
        screen.fill(bg)
        text = BIG_FONT.render("GAME OVER", True, (255,90,120))
        screen.blit(text, text.get_rect(center=(WIDTH//2, HEIGHT//2 - 30)))
        sc = MED_FONT.render(f"Score: {score}", True, (255,255,255))
        screen.blit(sc, sc.get_rect(center=(WIDTH//2, HEIGHT//2 + 20)))
        pygame.display.flip()
        clock.tick(30)


# ---------- MAIN ----------
def main():
    while True:
        menu_screen()
        play_game()

if __name__ == "__main__":
    main()
