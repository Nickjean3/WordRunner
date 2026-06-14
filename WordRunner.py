#!/usr/bin/env python3
########################################################################
# Filename    : WordRunner.py
# Description : Nicholas Jean - Game Script
# modification: 2026/02/04
########################################################################

import pygame
import sys
import random
import string
from Controller import input_state, start_input_thread

# ----------------------------
# Initialize pygame
# ----------------------------
pygame.init()
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Word Runner")
clock = pygame.time.Clock()

# ----------------------------
# Player setup
# ----------------------------
PLAYER_SIZE = 30
player_pos = [SCREEN_WIDTH // 4, SCREEN_HEIGHT // 2]
PLAYER_SPEED = 5

# ----------------------------
# Letter setup
# ----------------------------
letters = []
LETTER_SIZE = 30
LETTER_SPEED = 3
SPAWN_INTERVAL = 1000
last_spawn_time = 0

# ----------------------------
# Letter categories & colors
# ----------------------------
VOWELS = list("AEIOU")
RARE_CONSONANTS = list("JKQVWXYZ")
ALL_CONSONANTS = [
    c for c in "BCDFGHLMNPRST"
]  # all consonants except rare ones

LETTER_COLORS = {
    "vowel": (80, 160, 255),      # blue
    "consonant": (220, 220, 220), # light gray
    "rare": (255, 140, 0),        # orange
}

# ----------------------------
# Projectile setup
# ----------------------------
projectiles = []
PROJECTILE_SPEED = 8
PROJECTILE_SIZE = 10

# ----------------------------
# Word bank
# ----------------------------
word_bank = ""
confirmed_words = []  # words successfully validated

# Load dictionary
with open("/usr/share/dict/words") as f:
    DICTIONARY = set(word.strip().upper() for word in f.readlines())

# Font
font = pygame.font.SysFont(None, 36)

# ----------------------------
# Starfield setup
# ----------------------------
def make_stars(count, speed, size_range):
    return [
        {
            "x": random.randint(0, SCREEN_WIDTH),
            "y": random.randint(0, SCREEN_HEIGHT),
            "size": random.randint(*size_range),
            "speed": speed,
            "brightness": random.randint(150, 255)
        }
        for _ in range(count)
    ]
def draw_stars(surface):
    for layer in star_layers:
        for star in layer:
            star["x"] -= star["speed"]
            if star["x"] < 0:
                star["x"] = SCREEN_WIDTH
                star["y"] = random.randint(0, SCREEN_HEIGHT)
            c = star["brightness"]
            if star["size"] == 1:
                surface.set_at((int(star["x"]), int(star["y"])), (c, c, c))
            else:
                pygame.draw.rect(surface, (c, c, c),
                                 (int(star["x"]), int(star["y"]), star["size"], star["size"]))

star_layers = [
    make_stars(80,  1, (1, 1)),   # distant: tiny, slow
    make_stars(50,  2, (1, 2)),   # mid:     small, medium
    make_stars(25,  3, (2, 3)),   # close:   larger, fast
]

# ----------------------------
# Scoring
# ----------------------------
score = 0
current_word_score = 0

# ----------------------------
# Start controller input
# ----------------------------
start_input_thread()

# ----------------------------
# Helper functions
# ----------------------------
def spawn_letter():
    roll = random.random()

    if roll < 0.45:  # vowels
        char = random.choice(VOWELS)
        letter_type = "vowel"
    elif roll < 0.85:  # normal consonants
        char = random.choice(ALL_CONSONANTS)
        letter_type = "consonant"
    else:  # rare consonants
        char = random.choice(RARE_CONSONANTS)
        letter_type = "rare"

    letters.append({
        "char": char,
        "x": SCREEN_WIDTH,
        "y": random.randint(0, SCREEN_HEIGHT - LETTER_SIZE),
        "type": letter_type
    })

def player_rect():
    return pygame.Rect(player_pos[0], player_pos[1], PLAYER_SIZE, PLAYER_SIZE)

def projectile_rect(proj):
    return pygame.Rect(proj["x"], proj["y"], PROJECTILE_SIZE, PROJECTILE_SIZE)

def letter_rect(letter):
    return pygame.Rect(letter["x"], letter["y"], LETTER_SIZE, LETTER_SIZE)

# Fridge magnet tile colors per letter type
MAGNET_TILE_COLORS = {
    "vowel":     (30,  90,  200),   # deep blue tile
    "consonant": (60,  60,  60),    # dark gray tile
    "rare":      (180, 80,  0),     # burnt orange tile
}
MAGNET_FONT = pygame.font.SysFont("Arial Rounded MT Bold", 26, bold=True)
# Fallback if Arial Rounded isn't available on your system:
# MAGNET_FONT = pygame.font.SysFont("freesansbold", 26)

TILE_PADDING = 6
TILE_RADIUS = 6  # corner rounding

def draw_magnet_letter(surface, letter):
    tile_color = MAGNET_TILE_COLORS[letter["type"]]
    text_color = (255, 255, 255)

    text_surf = MAGNET_FONT.render(letter["char"], True, text_color)
    tw, th = text_surf.get_size()

    tile_w = tw + TILE_PADDING * 2
    tile_h = th + TILE_PADDING * 2
    tile_x = int(letter["x"])
    tile_y = int(letter["y"])

    # Draw rounded tile
    tile_rect = pygame.Rect(tile_x, tile_y, tile_w, tile_h)
    pygame.draw.rect(surface, tile_color, tile_rect, border_radius=TILE_RADIUS)

    # Subtle highlight on top edge for a slight 3D feel
    highlight_rect = pygame.Rect(tile_x + 2, tile_y + 2, tile_w - 4, 3)
    highlight_color = tuple(min(255, c + 60) for c in tile_color)
    pygame.draw.rect(surface, highlight_color, highlight_rect, border_radius=2)

    # Draw letter centered on tile
    surface.blit(text_surf, (tile_x + TILE_PADDING, tile_y + TILE_PADDING))
    
def draw_rocket(surface, x, y):
    x, y = int(x), int(y)
    # --- Body (yellow) ---
    pygame.draw.rect(surface, (255, 220, 0), (x + 6, y + 8, 20, 14))

    # --- Nose cone (pointed right, yellow/white) ---
    nose = [
        (x + 26, y + 15),   # tip
        (x + 16, y + 8),    # top
        (x + 16, y + 22),   # bottom
    ]
    pygame.draw.polygon(surface, (255, 240, 80), nose)

    # --- Tail block (darker yellow) ---
    pygame.draw.rect(surface, (200, 160, 0), (x + 2, y + 9, 6, 12))

    # --- Top fin (red) ---
    top_fin = [
        (x + 2,  y + 9),
        (x + 10, y + 9),
        (x + 6,  y + 2),
    ]
    pygame.draw.polygon(surface, (220, 40, 40), top_fin)

    # --- Bottom fin (red) ---
    bot_fin = [
        (x + 2,  y + 21),
        (x + 10, y + 21),
        (x + 6,  y + 28),
    ]
    pygame.draw.polygon(surface, (220, 40, 40), bot_fin)

    # --- Window (cockpit) ---
    pygame.draw.circle(surface, (140, 220, 255), (x + 20, y + 15), 4)
    pygame.draw.circle(surface, (255, 255, 255), (x + 19, y + 14), 1)  # glint

    # --- Exhaust flame (animated flicker) ---
    flicker = random.randint(4, 10)
    flame = [
        (x + 2,  y + 12),
        (x - flicker, y + 15),
        (x + 2,  y + 18),
    ]
    pygame.draw.polygon(surface, (255, 120, 0), flame)
    inner_flame = [
        (x + 2,  y + 13),
        (x - flicker + 3, y + 15),
        (x + 2,  y + 17),
    ]
    pygame.draw.polygon(surface, (255, 230, 80), inner_flame)

def cash_word():
    global word_bank, confirmed_words, score, current_word_score

    word_length = len(word_bank)

    if word_bank.upper() in DICTIONARY and word_length >= 2:
        if word_length <= 4:
            multiplier = 1
        elif word_length <= 6:
            multiplier = 2
        elif word_length <= 8:
            multiplier = 3
        else:
            multiplier = 4

        gained = current_word_score * multiplier
        score += gained
        confirmed_words.append(word_bank.upper())

        print(f"Word: {word_bank}  +{gained} points")

    else:
        print("Invalid word:", word_bank)

    word_bank = ""
    current_word_score = 0
    
def draw_title_screen():
    screen.fill((5, 5, 20))
    draw_stars(screen)

    title_font = pygame.font.SysFont("Arial Rounded MT Bold", 96, bold=True)
    menu_font = pygame.font.SysFont("Arial Rounded MT Bold", 40, bold=True)

    title_surface = title_font.render("WORD RUNNER", True, (255, 255, 255))
    screen.blit(title_surface, (SCREEN_WIDTH//2 - title_surface.get_width()//2, 150))

    start_color = (0, 255, 0) if selected_option == 0 else (255, 255, 255)
    instr_color = (0, 255, 0) if selected_option == 1 else (255, 255, 255)

    start_surface = menu_font.render("Start Game", True, start_color)
    instr_surface = menu_font.render("Instructions", True, instr_color)

    screen.blit(start_surface, (SCREEN_WIDTH//2 - start_surface.get_width()//2, 320))
    screen.blit(instr_surface, (SCREEN_WIDTH//2 - instr_surface.get_width()//2, 380))

    pygame.display.flip()
    
def draw_instructions_screen():
    screen.fill((5, 5, 20))
    draw_stars(screen)
    font_small = pygame.font.SysFont("Arial Rounded MT Bold", 28)
    font_header = pygame.font.SysFont("Arial Rounded MT Bold", 48, bold=True)

    header = font_header.render("HOW TO PLAY", True, (255, 255, 255))
    screen.blit(header, (SCREEN_WIDTH//2 - header.get_width()//2, 60))

    lines = [
        "Move: Joystick",
        "Shoot Letter: Button 1",
        "Cash Word: Button 2",
        "",
        "Vowels (Blue): 1 point",
        "Consonants (White): 2 points",
        "Rare Letters (Orange): 4 points",
        "",
        "Word Multipliers:",
        "5-6 letters: 2x",
        "7-8 letters: 3x",
        "9+ letters: 4x",
        "",
        "Avoid letters — collision = GAME OVER",
        "Press Shoot to return"
    ]

    y = 140
    for line in lines:
        text = font_small.render(line, True, (200, 200, 200))
        screen.blit(text, (SCREEN_WIDTH//2 - text.get_width()//2, y))
        y += 30

    pygame.display.flip()



# ----------------------------
# Game state
# ----------------------------
running = True
player_dead = False
selected_option = 0  # for restart/exit menu
game_state = "title"  # title, instructions, game

# ----------------------------
# Main game loop
# ----------------------------
while running:
    dt = clock.tick(60)
    current_time = pygame.time.get_ticks()

    # --- Handle events ---
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    # ----------------------------
    # Title Screen
    # ----------------------------
    if game_state == "title":
        draw_title_screen()

        if input_state["y"] < 100:
            selected_option = 0
        elif input_state["y"] > 150:
            selected_option = 1

        if input_state["shoot"]:
            input_state["shoot"] = False
            if selected_option == 0:
                game_state = "game"
            else:
                game_state = "instructions"
        continue
        
    # ----------------------------
    # Instructions Screen
    # ----------------------------
    if game_state == "instructions":
        draw_instructions_screen()

        if input_state["shoot"]:
            input_state["shoot"] = False
            game_state = "title"
        continue

    # ----------------------------
    # GAME OVER Screen
    # ----------------------------
    if player_dead:
        screen.fill((5, 5, 20))
        draw_stars(screen)
        game_over_surface = font.render("GAME OVER", True, (255, 0, 0))
        screen.blit(game_over_surface, (SCREEN_WIDTH//2 - 100, SCREEN_HEIGHT//2 - 100))
        # Draw final score
        score_surface = font.render(f"Final Score: {score}", True, (255, 255, 255))
        screen.blit(score_surface,(SCREEN_WIDTH//2 - score_surface.get_width()//2,SCREEN_HEIGHT//2 - 60))
        restart_color = (0, 255, 0) if selected_option == 0 else (255, 255, 255)
        exit_color = (0, 255, 0) if selected_option == 1 else (255, 255, 255)
        restart_surface = font.render("Restart", True, restart_color)
        exit_surface = font.render("Exit", True, exit_color)
        screen.blit(restart_surface, (SCREEN_WIDTH//2 - 50, SCREEN_HEIGHT//2))
        screen.blit(exit_surface, (SCREEN_WIDTH//2 - 50, SCREEN_HEIGHT//2 + 50))
        pygame.display.flip()

        if input_state["y"] < 100:
            selected_option = 0
        elif input_state["y"] > 150:
            selected_option = 1
            
        # restart logic
        if input_state["shoot"]:
            input_state["shoot"] = False
            if selected_option == 0:
                letters.clear()
                projectiles.clear()
                word_bank = ""
                confirmed_words.clear()
                current_word_score = 0
                score = 0
                player_pos = [SCREEN_WIDTH // 4, SCREEN_HEIGHT // 2]
                player_dead = False
                game_state = "game"
            else:
                running = False
        continue  # skip game update while dead

    # --- Player movement ---
    dx = (input_state["x"] - 128) / 128 * PLAYER_SPEED
    dy = (input_state["y"] - 128) / 128 * PLAYER_SPEED
    player_pos[0] += dx
    player_pos[1] += dy
    player_pos[0] = max(0, min(SCREEN_WIDTH - PLAYER_SIZE, player_pos[0]))
    player_pos[1] = max(0, min(SCREEN_HEIGHT - PLAYER_SIZE, player_pos[1]))

    # --- Spawn letters ---
    if current_time - last_spawn_time > SPAWN_INTERVAL:
        spawn_letter()
        last_spawn_time = current_time

    # --- Update letters ---
    for letter in letters:
        letter["x"] -= LETTER_SPEED
    letters = [l for l in letters if l["x"] + LETTER_SIZE > 0]

    # --- Shooting letters ---
    if input_state["shoot"]:
        projectiles.append({
            "x": player_pos[0] + PLAYER_SIZE,
            "y": player_pos[1] + PLAYER_SIZE // 2 - PROJECTILE_SIZE // 2
        })
        input_state["shoot"] = False
    for proj in projectiles:
        proj["x"] += PROJECTILE_SPEED
    projectiles = [p for p in projectiles if p["x"] < SCREEN_WIDTH]

    # --- Projectile hits letters ---
    for proj in projectiles[:]:
        for letter in letters[:]:
            if projectile_rect(proj).colliderect(letter_rect(letter)):
                word_bank += letter["char"]

                # Add letter value to current word score
                if letter["type"] == "vowel":
                    current_word_score += 1
                elif letter["type"] == "consonant":
                    current_word_score += 2
                else:  # rare
                    current_word_score += 4

                projectiles.remove(proj)
                letters.remove(letter)
                break

    # --- Cash word button (Button 2 (special)) ---
    if input_state["special"]:
        input_state["special"] = False
        cash_word()

    # --- Player collision with letters ---
    for letter in letters:
        if player_rect().colliderect(letter_rect(letter)):
            player_dead = True
            break

    # --- Draw ---
    screen.fill((5, 5, 20))
    draw_stars(screen)
                             
    draw_rocket(screen, player_pos[0], player_pos[1])
    for letter in letters:
        draw_magnet_letter(screen, letter)
    for proj in projectiles:
        pygame.draw.rect(screen, (0, 255, 0), (proj["x"], proj["y"], PROJECTILE_SIZE, PROJECTILE_SIZE))

    # Draw word bank and confirmed words
    word_surface = font.render("Word Bank: " + word_bank, True, (255, 255, 0))
    screen.blit(word_surface, (10, 10))
    confirmed_surface = font.render("Confirmed Words: " + ", ".join(confirmed_words), True, (0, 255, 255))
    screen.blit(confirmed_surface, (10, 50))
    score_surface = font.render(f"Score: {score}", True, (0, 255, 0))
    screen.blit(score_surface, (10, 90))

    pygame.display.flip()

pygame.quit()
sys.exit()
