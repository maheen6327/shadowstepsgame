import pygame
import sys
import tkinter as tk
from tkinter import messagebox

# --- Show intro using tkinter (before Pygame launches) ---
def show_intro():
    root = tk.Tk()
    root.withdraw()
    messagebox.showinfo(
        "Shadow Steps – The Silent Reflection",
        "🌌 WELCOME TO SHADOW STEPS 🌌\n\n"
        "🕹️ HOW TO PLAY:\n"
        "- Use Arrow Keys to move\n"
        "- Press SPACE to switch between Real and Shadow worlds\n"
        "- Explore and solve the puzzle using clues\n\n"
        "🔍 HINT:\n"
        "\"Numbers align in shadow and light,  \n"
        "Step with care, avoid the night.  \n"
        "Two times, five times, secrets unfold,  \n"
        "False paths shimmer, truth is bold.  \n"
        "Walk the pattern, break the spell,  \n"
        "Only the chosen tiles will tell.\"\n\n"
        "Good luck, wanderer of echoes..."
    )
    root.destroy()

# --- Initialize Pygame ---
pygame.init()
pygame.mixer.init()

# --- Constants ---
WIDTH, HEIGHT = 600, 600
ROWS, COLS = 10, 10
TILE_SIZE = WIDTH // COLS

# --- Colors ---
REAL_BG_TOP = (240, 240, 240)
REAL_BG_BOTTOM = (180, 180, 200)
SHADOW_BG_TOP = (30, 30, 60)
SHADOW_BG_BOTTOM = (50, 50, 90)

REAL_TILE = (180, 180, 180)
SHADOW_TILE = (70, 70, 120)
PLAYER_COLOR = (255, 80, 80)
SHADOW_COLOR = (140, 140, 255)
CORRECT_COLOR = (40, 180, 40)
WRONG_COLOR = (180, 40, 40)
GOAL_COLOR = (255, 215, 0)

TEXT_COLOR = (20, 20, 20)
SHADOW_TEXT_COLOR = (200, 200, 255)

MESSAGE_DURATION = 2000  # milliseconds

# --- Setup screen and fonts ---
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Shadow Steps – The Silent Reflection")

font = pygame.font.SysFont(None, 24)
big_font = pygame.font.SysFont(None, 40)
title_font = pygame.font.SysFont(None, 30)

clock = pygame.time.Clock()

# --- Load sounds ---
try:
    switch_sound = pygame.mixer.Sound("assets/sounds/switch.wav")
    success_sound = pygame.mixer.Sound("assets/sounds/success.wav")
    failure_sound = pygame.mixer.Sound("assets/sounds/failure.wav")
    pygame.mixer.music.load("assets/sounds/bg_music.mp3")
    pygame.mixer.music.set_volume(0.5)
    pygame.mixer.music.play(-1)  # Loop background music indefinitely
except Exception as e:
    print("Warning: Could not load sound files.", e)
    switch_sound = None
    success_sound = None
    failure_sound = None

# --- Tile data ---
real_tiles = {
    (1, 2): 'R2',
    (3, 1): 'R4',
    (5, 2): 'R5',
    (7, 1): 'R8',
    (2, 5): 'R12',
    (4, 7): 'R15',
    (6, 5): 'R18',
    (0, 0): 'Rx1', (9, 0): 'Rz2', (0, 9): 'Ry3', (9, 9): 'Rw4', (5, 5): 'Rv5',
}

shadow_tiles = {
    (2, 3): 'S6',
    (4, 2): 'S10',
    (6, 3): 'S14',
    (8, 2): 'S16',
    (1, 7): 'S20',
    (0, 1): 'Sx1', (9, 1): 'Sz2', (0, 8): 'Sy3', (9, 8): 'Sw4', (5, 4): 'Sv5',
}

goal_tile = (9, 7)

# Correct sequence of tiles to step on
sequence = [
    'R2', 'S6', 'R4', 'S10',
    'R5', 'S14', 'R8', 'S16',
    'R12', 'S20', 'R15', 'R18', 'GOAL'
]

# --- Game state variables ---
player_pos = [2, 2]
shadow_pos = [1, 6]
shadow_mode = False
progress = []
message = ""
message_timer = 0

# --- Helper Functions ---

def play_sound(sound):
    if sound:
        sound.play()

def draw_gradient():
    """Draw vertical gradient background based on current mode."""
    top_color = SHADOW_BG_TOP if shadow_mode else REAL_BG_TOP
    bottom_color = SHADOW_BG_BOTTOM if shadow_mode else REAL_BG_BOTTOM
    for y in range(HEIGHT):
        ratio = y / HEIGHT
        color = tuple(
            int(top_color[i] * (1 - ratio) + bottom_color[i] * ratio)
            for i in range(3)
        )
        pygame.draw.line(screen, color, (0, y), (WIDTH, y))

def draw_grid():
    """Draw grid tiles and labels for real or shadow tiles."""
    for row in range(ROWS):
        for col in range(COLS):
            rect = pygame.Rect(col * TILE_SIZE, row * TILE_SIZE, TILE_SIZE, TILE_SIZE)
            if not shadow_mode and (col, row) in real_tiles:
                pygame.draw.rect(screen, REAL_TILE, rect)
                label = font.render(real_tiles[(col, row)], True, TEXT_COLOR)
                screen.blit(label, (col * TILE_SIZE + 4, row * TILE_SIZE + 4))
            elif shadow_mode and (col, row) in shadow_tiles:
                pygame.draw.rect(screen, SHADOW_TILE, rect)
                label = font.render(shadow_tiles[(col, row)], True, SHADOW_TEXT_COLOR)
                screen.blit(label, (col * TILE_SIZE + 4, row * TILE_SIZE + 4))

            if (col, row) == goal_tile:
                pygame.draw.rect(screen, GOAL_COLOR, rect)
                label = font.render("GOAL", True, (0, 0, 0))
                screen.blit(label, (col * TILE_SIZE + 5, row * TILE_SIZE + 5))

            pygame.draw.rect(screen, (100, 100, 100), rect, 1)  # Grid lines

def draw_player():
    """Draw player or shadow circle with glow effect."""
    pos = shadow_pos if shadow_mode else player_pos
    color = SHADOW_COLOR if shadow_mode else PLAYER_COLOR
    x = pos[0] * TILE_SIZE + TILE_SIZE // 2
    y = pos[1] * TILE_SIZE + TILE_SIZE // 2

    # Glow effect
    glow_radius = TILE_SIZE // 3 + 6
    glow_surf = pygame.Surface((glow_radius*2, glow_radius*2), pygame.SRCALPHA)
    pygame.draw.circle(glow_surf, (color[0], color[1], color[2], 60), (glow_radius, glow_radius), glow_radius)
    screen.blit(glow_surf, (x - glow_radius, y - glow_radius))

    # Main circle
    pygame.draw.circle(screen, color, (x, y), TILE_SIZE // 3)

def check_tile(pos):
    """Check if player/ shadow stepped on the correct tile in sequence."""
    global progress, message, message_timer
    tile_code = shadow_tiles.get(tuple(pos)) if shadow_mode else real_tiles.get(tuple(pos))

    if tuple(pos) == goal_tile:
        tile_code = 'GOAL'

    if tile_code:
        expected = sequence[len(progress)]
        if tile_code == expected:
            progress.append(tile_code)
            message = f"Correct Step: {tile_code}" if tile_code != 'GOAL' else "GOAL REACHED – Door Opened!"
            play_sound(success_sound)
        else:
            progress = []
            message = "Wrong Step – Sequence Reset!"
            play_sound(failure_sound)
        message_timer = pygame.time.get_ticks()

def move_player(dx, dy):
    """Move player or shadow if inside grid boundaries."""
    pos = shadow_pos if shadow_mode else player_pos
    new_x, new_y = pos[0] + dx, pos[1] + dy

    if 0 <= new_x < COLS and 0 <= new_y < ROWS:
        if shadow_mode:
            shadow_pos[0], shadow_pos[1] = new_x, new_y
        else:
            player_pos[0], player_pos[1] = new_x, new_y
        check_tile([new_x, new_y])

def switch_mode():
    """Toggle between real and shadow modes with sound effect."""
    global shadow_mode
    shadow_mode = not shadow_mode
    play_sound(switch_sound)

def draw_message():
    """Show fading message on the bottom left of screen."""
    global message, message_timer
    if message:
        elapsed = pygame.time.get_ticks() - message_timer
        if elapsed < MESSAGE_DURATION:
            alpha = 255 * (1 - elapsed / MESSAGE_DURATION)
            msg_surf = font.render(message, True, (255, 255, 255))
            fade_surf = pygame.Surface(msg_surf.get_size(), pygame.SRCALPHA)
            fade_surf.fill((0, 0, 0, int(alpha * 0.8)))
            fade_surf.blit(msg_surf, (0, 0))
            screen.blit(fade_surf, (10, HEIGHT - 40))
        else:
            message = ""

def draw_progress():
    """Draw sequence progress on top-right corner."""
    txt = "Progress: " + " > ".join(progress)
    label = font.render(txt, True, (255, 255, 255) if shadow_mode else (0, 0, 0))
    screen.blit(label, (10, 10))

def draw_mode_label():
    """Draw mode label on top center."""
    mode_text = "SHADOW WORLD" if shadow_mode else "REAL WORLD"
    label = title_font.render(mode_text, True, (200, 200, 255) if shadow_mode else (50, 50, 50))
    screen.blit(label, (WIDTH // 2 - label.get_width() // 2, 10))

# --- Main Menu ---
def main_menu():
    menu = True
    title_text = big_font.render("Shadow Steps – The Silent Reflection", True, PLAYER_COLOR)
    start_text = font.render("Press ENTER to Start", True, (100, 100, 100))

    while menu:
        screen.fill((20, 20, 20))
        screen.blit(title_text, (WIDTH//2 - title_text.get_width()//2, HEIGHT//3))
        screen.blit(start_text, (WIDTH//2 - start_text.get_width()//2, HEIGHT//2))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    menu = False

        pygame.display.flip()
        clock.tick(60)

# --- Main Game Loop ---
def main():
    show_intro()
    main_menu()

    running = True
    while running:
        clock.tick(60)
        draw_gradient()
        draw_grid()
        draw_player()
        draw_progress()
        draw_mode_label()
        draw_message()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    switch_mode()
                if event.key == pygame.K_UP:
                    move_player(0, -1)
                if event.key == pygame.K_DOWN:
                    move_player(0, 1)
                if event.key == pygame.K_LEFT:
                    move_player(-1, 0)
                if event.key == pygame.K_RIGHT:
                    move_player(1, 0)

        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()


