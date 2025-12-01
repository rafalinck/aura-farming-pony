import pygame 
import random
import os
import json
import math

pygame.init()

#configuração inicial (res, fps, etc)
WIDTH, HEIGHT = 1200, 800
FPS = 60
pygame.display.set_caption("Aura Farming Pony")

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED   = (255, 60, 60)
BLUE  = (60, 100, 255)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

#configurações básicas dos assets (player, fundo, sons, etc) [se não souber fazer, é só colocar o arquivo dentro da mesma pasta do .py e copiar o url e colar entre as aspas ali]
ASSETS = {
    "background": "-",
    "background_fase1": "-",  
    "background_fase2": "-",  
    "background_fase3": "-",
    "background_gameover": "-",
    "background_win": "-",
    "player": "-",
    "player2": "-",
    "meteor": "-",
    "meteor_forte": "-",
    "sound_point": "-",
    "sound_hit": "-",
    "music": "-",
    "life": "-",
    "shield": "-",
    "speed": "-",
}

def load_image(filename, fallback_color, size):
    if os.path.exists(filename):
        img = pygame.image.load(filename).convert_alpha()
        img = pygame.transform.scale(img, size)
        return img
    surf = pygame.Surface(size)
    surf.fill(fallback_color)
    return surf

def load_sound(filename):
    if os.path.exists(filename):
        return pygame.mixer.Sound(filename)
    return None

background_img = load_image(ASSETS["background"], WHITE, (WIDTH, HEIGHT))
background_fase1  = load_image(ASSETS["background_fase1"], WHITE, (WIDTH, HEIGHT))
background_fase2  = load_image(ASSETS["background_fase2"], WHITE, (WIDTH, HEIGHT))
background_fase3  = load_image(ASSETS["background_fase3"], WHITE, (WIDTH, HEIGHT))
background_gameover = load_image(ASSETS["background_gameover"], WHITE, (WIDTH, HEIGHT))
background_win = load_image(ASSETS["background_win"], WHITE, (WIDTH, HEIGHT))
player_img  = load_image(ASSETS["player"], BLUE, (120, 90))
player2_img = load_image(ASSETS["player2"], BLUE, (120, 90))
meteor_img  = load_image(ASSETS["meteor"], RED, (60, 60))
METEOR_W, METEOR_H = meteor_img.get_width(), meteor_img.get_height()

life_img   = load_image(ASSETS["life"],   (0, 255, 0),   (45, 45))
shield_img = load_image(ASSETS["shield"], (255, 255, 0), (45, 45))
LIFE_W, LIFE_H = life_img.get_width(), life_img.get_height()
SHIELD_W, SHIELD_H = shield_img.get_width(), shield_img.get_height()

speed_img = load_image(ASSETS["speed"], (0, 150, 255), (45, 45))
SPEED_W, SPEED_H = speed_img.get_width(), speed_img.get_height()

meteor_strong_img = load_image(ASSETS["meteor_forte"], (150, 0, 0), (60, 60))
STR_METEOR_W, STR_METEOR_H = meteor_strong_img.get_width(), meteor_strong_img.get_height()

#efeito visual do escudo
shield_scale = 1.6
shield_w = int(player_img.get_width() * shield_scale)
shield_h = int(player_img.get_height() * shield_scale)
shield_surf = pygame.Surface((shield_w, shield_h), pygame.SRCALPHA)
pygame.draw.ellipse(shield_surf, (120, 200, 255, 110), shield_surf.get_rect(), 0)

try:
    pygame.mixer.init()
except pygame.error:
    print("Mixer não iniciado")

sound_point = load_sound(ASSETS["sound_point"])
sound_hit   = load_sound(ASSETS["sound_hit"])

music_file = ASSETS["music"] if os.path.exists(ASSETS["music"]) else None

def play_music():
    if music_file:
        try:
            pygame.mixer.music.load(music_file)
            pygame.mixer.music.set_volume(0.4)
            pygame.mixer.music.play(-1)
        except pygame.error:
            pass

#fontes (de texto msm) / estados do jogo (muda ao longo do jogo, representa a situação de um objeto, componente, tela e mais algumas outras coisas)
font       = pygame.font.Font(None, 54)
big_font   = pygame.font.Font(None, 108)
small_font = pygame.font.Font(None, 42)

STATE_MENU        = "MENU"
STATE_PLAYING     = "JOGANDO"
STATE_OVER        = "GAME_OVER"
STATE_WIN         = "VITORIA"
STATE_CREDITS     = "CREDITOS"
STATE_PAUSED      = "PAUSADO"
STATE_PVP_WIN     = "VITORIA_PVP"
STATE_LEADERBOARD = "LEADERBOARD"

game_state = STATE_MENU

#variáveis do jogo
score = 0
lives1 = 3
lives2 = 3
num_players = 1

phase_name = "Fase 1"
phase_alert_timer = 0

player_rect  = player_img.get_rect(center=(WIDTH // 2, HEIGHT - 90))
player2_rect = player2_img.get_rect(center=(WIDTH // 2 + 150, HEIGHT - 90))

meteor_list = []
NUM_METEORS = 6
meteor_speed = 3

strong_meteor_list = []
NUM_STRONG_METEORS = NUM_METEORS

bullets = []
BULLET_W, BULLET_H = 10, 25
bullet_speed = 12
bullet_cooldown_ms = 1500
last_shot_time = 0

life_list = []
shield_list = []
NUM_LIFE = 1
NUM_SHIELD = 1
shield1_active = False
shield2_active = False

speed_list = []
NUM_SPEED = 1
speed1_timer = 0
speed2_timer = 0
speed_boost_amount = 3

SAVE_FILE = "savegame.json"
has_saved_game = os.path.exists(SAVE_FILE)

winner_text = ""

#variáveis e funções utilizadas para o leaderboard
LEADERBOARD_FILE = "leaderboard.json"
leaderboard = []
name_input = ""
meteors_destroyed = 0

def save_leaderboard():
    try:
        with open(LEADERBOARD_FILE, "w") as f:
            json.dump(leaderboard, f)
    except:
        pass

def load_leaderboard():
    global leaderboard
    if os.path.exists(LEADERBOARD_FILE):
        try:
            with open(LEADERBOARD_FILE, "r") as f:
                data = json.load(f)
            if isinstance(data, list):
                leaderboard = data
            else:
                leaderboard = []
        except:
            leaderboard = []
    else:
        leaderboard = []

#registros do leaderboard
def add_leaderboard_entry(name, score_value, destroyed_value, lives_value):
    global leaderboard
    entry = {
        "name": name if name else "SemNome",
        "score": score_value,
        "destroyed": destroyed_value,
        "lives": lives_value
    }
    leaderboard.append(entry)
    #faz com que a lista fique em ordem de pontuação 
    leaderboard.sort(key=lambda e: e.get("score", 0), reverse=True)
    save_leaderboard()

def get_best_entry():
    if leaderboard:
        return leaderboard[0]
    return None

#carrega o leaderboard ao iniciar a partida
load_leaderboard()

#funções para salvar e carregar o estado atual do jogo em arquivo
def save_game():
    data = {
        "score": score,
        "lives1": lives1,
        "lives2": lives2,
        "num_players": num_players,
        "phase_name": phase_name,
        "phase_alert_timer": phase_alert_timer,
        "player_rect": [player_rect.x, player_rect.y],
        "player2_rect": [player2_rect.x, player2_rect.y],
        "meteor_speed": meteor_speed,
        "meteor_list": [[m.x, m.y] for m in meteor_list],
        "strong_meteor_list": [[m.x, m.y] for m in strong_meteor_list],
        "shield1_active": shield1_active,
        "shield2_active": shield2_active,
        "life_list": [[r.x, r.y] for r in life_list],
        "shield_list": [[r.x, r.y] for r in shield_list],
        "speed_list": [[r.x, r.y] for r in speed_list],
        "speed1_timer": speed1_timer,
        "speed2_timer": speed2_timer,
        "meteors_destroyed": meteors_destroyed,
    }
    with open(SAVE_FILE, "w") as f:
        json.dump(data, f)

def load_game():
    global score, lives1, lives2, num_players, phase_name, phase_alert_timer
    global player_rect, player2_rect, meteor_speed, meteor_list, game_state
    global life_list, shield_list, shield1_active, shield2_active
    global speed_list, speed1_timer, speed2_timer
    global strong_meteor_list, bullets, meteors_destroyed, name_input

    if not os.path.exists(SAVE_FILE):
        return False

    with open(SAVE_FILE, "r") as f:
        data = json.load(f)

    score = data["score"]
    lives1 = data["lives1"]
    lives2 = data["lives2"]
    num_players = data["num_players"]
    phase_name = data["phase_name"]
    phase_alert_timer = data["phase_alert_timer"]
    player_rect.x, player_rect.y = data["player_rect"]
    player2_rect.x, player2_rect.y = data["player2_rect"]
    meteor_speed = data["meteor_speed"]

    meteor_list = []
    for x, y in data["meteor_list"]:
        meteor_list.append(pygame.Rect(x, y, METEOR_W, METEOR_H))

    strong_meteor_list = []
    strong_coords = data.get("strong_meteor_list", [])
    for x, y in strong_coords:
        strong_meteor_list.append(pygame.Rect(x, y, STR_METEOR_W, STR_METEOR_H))

    shield1_active = data.get("shield1_active", False)
    shield2_active = data.get("shield2_active", False)

    life_list = []
    shield_list = []
    speed_list = []
    bullets = []

    life_coords = data.get("life_list")
    shield_coords = data.get("shield_list")
    speed_coords = data.get("speed_list")
    speed1_timer = data.get("speed1_timer", 0)
    speed2_timer = data.get("speed2_timer", 0)
    meteors_destroyed = data.get("meteors_destroyed", 0)
    name_input = ""

    if life_coords is not None:
        for x, y in life_coords:
            life_list.append(pygame.Rect(x, y, LIFE_W, LIFE_H))
    if shield_coords is not None:
        for x, y in shield_coords:
            shield_list.append(pygame.Rect(x, y, SHIELD_W, SHIELD_H))
    if speed_coords is not None:
        for x, y in speed_coords:
            speed_list.append(pygame.Rect(x, y, SPEED_W, SPEED_H))

    if life_coords is None or shield_coords is None or speed_coords is None or not strong_coords:
        criar_powerups()
        criar_meteoros_fortes()

    game_state = STATE_PLAYING
    play_music()
    return True

def criar_meteoros():
    global meteor_list
    meteor_list = []
    for _ in range(NUM_METEORS):
        x = random.randint(0, WIDTH - METEOR_W)
        y = random.randint(-600, -METEOR_H)
        meteor_list.append(pygame.Rect(x, y, METEOR_W, METEOR_H))

def criar_meteoros_fortes():
    global strong_meteor_list
    strong_meteor_list = []
    for _ in range(NUM_STRONG_METEORS):
        x = random.randint(0, WIDTH - STR_METEOR_W)
        y = random.randint(-6000, -STR_METEOR_H)
        strong_meteor_list.append(pygame.Rect(x, y, STR_METEOR_W, STR_METEOR_H))

def criar_powerups():
    global life_list, shield_list, speed_list
    life_list = []
    shield_list = []
    speed_list = []
    for _ in range(NUM_LIFE):
        x = random.randint(0, WIDTH - LIFE_W)
        y = random.randint(-4500, -LIFE_H)
        life_list.append(pygame.Rect(x, y, LIFE_W, LIFE_H))
    for _ in range(NUM_SHIELD):
        x = random.randint(0, WIDTH - SHIELD_W)
        y = random.randint(-4500, -SHIELD_H)
        shield_list.append(pygame.Rect(x, y, SHIELD_W, SHIELD_H))
    for _ in range(NUM_SPEED):
        x = random.randint(0, WIDTH - SPEED_W)
        y = random.randint(-6000, -SPEED_H)
        speed_list.append(pygame.Rect(x, y, SPEED_W, SPEED_H))

def atualizar_fase(score):
    #Define fase, velocidade e dispara aviso se mudar.
    global phase_name, meteor_speed, phase_alert_timer

    if score < 30:
        nova, vel = "Fase 1", 3
    elif score < 70:
        nova, vel = "Fase 2", 4
    else:
        nova, vel = "Fase 3", 5

    if nova != phase_name:
        phase_name = nova
        meteor_speed = vel
        phase_alert_timer = FPS * 2
    else:
        meteor_speed = vel

#botões do menu e telas
button_width  = 390
button_height = 90

continue_button = pygame.Rect(WIDTH//2 - button_width//2, HEIGHT//2 - 30,
                              button_width, button_height)
start1_button = pygame.Rect(WIDTH//2 - button_width//2, HEIGHT//2 + 90,
                            button_width, button_height)
start2_button = pygame.Rect(WIDTH//2 - button_width//2, HEIGHT//2 + 210,
                            button_width, button_height)
credits_button = pygame.Rect(WIDTH//2 - button_width//2, HEIGHT//2 + 330,
                             button_width, button_height)
leaderboard_menu_button = pygame.Rect(WIDTH//2 - button_width//2, HEIGHT//2 + 330,
                                      button_width, button_height)

restart_button = pygame.Rect(WIDTH//2 - 150, HEIGHT//2 - 10, 300, 60)
quit_button    = pygame.Rect(WIDTH//2 - 150, HEIGHT//2 + 60, 300, 60)
leaderboard_button = pygame.Rect(WIDTH//2 - 150, HEIGHT//2 + 130, 300, 60)

back_button = pygame.Rect(20, HEIGHT - 90, 240, 60)

pause_continue_button = pygame.Rect(WIDTH//2 - 150, HEIGHT//2,      300, 75)
pause_menu_button     = pygame.Rect(WIDTH//2 - 150, HEIGHT//2 + 90, 300, 75)

pvp_menu_button = pygame.Rect(WIDTH//2 - 150, HEIGHT//2 + 90, 300, 75)

def reset_game():
    global score, lives1, lives2, game_state, phase_name, has_saved_game
    global shield1_active, shield2_active, speed1_timer, speed2_timer
    global strong_meteor_list, bullets, last_shot_time, meteors_destroyed, name_input

    score = 0
    lives1 = 3
    lives2 = 3
    phase_name = "Fase 1"
    game_state = STATE_PLAYING
    shield1_active = False
    shield2_active = False
    speed1_timer = 0
    speed2_timer = 0
    strong_meteor_list = []
    bullets = []
    last_shot_time = 0
    meteors_destroyed = 0
    name_input = ""

    if num_players == 1:
        player_rect.center  = (WIDTH // 2, HEIGHT - 90)
        player2_rect.center = (-200, -200)
    else:
        player_rect.center  = (WIDTH // 2 - 150, HEIGHT - 90)
        player2_rect.center = (WIDTH // 2 + 150, HEIGHT - 90)

    criar_meteoros()
    criar_meteoros_fortes()
    criar_powerups()
    play_music()

    if os.path.exists(SAVE_FILE):
        os.remove(SAVE_FILE)
    has_saved_game = False

running = True
while running:
    clock.tick(FPS)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos

            if game_state == STATE_MENU:
                if has_saved_game and continue_button.collidepoint(mx, my):
                    if load_game():
                        has_saved_game = True
                elif start1_button.collidepoint(mx, my):
                    num_players = 1
                    reset_game()
                elif start2_button.collidepoint(mx, my):
                    num_players = 2
                    reset_game()
                elif leaderboard_menu_button.collidepoint(mx, my):
                    #para mostrar o leaderboard pelo menu principal
                    game_state = STATE_LEADERBOARD
                elif credits_button.collidepoint(mx, my):
                    game_state = STATE_CREDITS
                    pygame.mixer.music.stop()

            elif game_state == STATE_PLAYING and num_players == 1 and phase_name != "Fase 1":
                now = pygame.time.get_ticks()
                if now - last_shot_time >= bullet_cooldown_ms:
                    px, py = player_rect.center
                    dx = mx - px
                    dy = my - py
                    dist = math.hypot(dx, dy)
                    if dist != 0:
                        vx = dx / dist * bullet_speed
                        vy = dy / dist * bullet_speed
                    else:
                        vx = 0
                        vy = -bullet_speed
                    bullet_rect = pygame.Rect(px - BULLET_W // 2, py - BULLET_H // 2, BULLET_W, BULLET_H)
                    bullets.append({"rect": bullet_rect, "vx": vx, "vy": vy})
                    last_shot_time = now

            elif game_state in (STATE_OVER, STATE_WIN):
                if restart_button.collidepoint(mx, my):
                    reset_game()
                elif quit_button.collidepoint(mx, my):
                    running = False
                elif leaderboard_button.collidepoint(mx, my):
                    add_leaderboard_entry(name_input.strip(), score, meteors_destroyed, lives1)
                    load_leaderboard()
                    game_state = STATE_LEADERBOARD

            elif game_state == STATE_CREDITS:
                if back_button.collidepoint(mx, my):
                    game_state = STATE_MENU

            elif game_state == STATE_PAUSED:
                if pause_continue_button.collidepoint(mx, my):
                    game_state = STATE_PLAYING
                elif pause_menu_button.collidepoint(mx, my):
                    save_game()
                    has_saved_game = True
                    game_state = STATE_MENU
                    pygame.mixer.music.stop()

            elif game_state == STATE_PVP_WIN:
                if pvp_menu_button.collidepoint(mx, my):
                    game_state = STATE_MENU

            elif game_state == STATE_LEADERBOARD:
                if back_button.collidepoint(mx, my):
                    game_state = STATE_MENU

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE and game_state == STATE_PLAYING:
                game_state = STATE_PAUSED
            elif game_state in (STATE_OVER, STATE_WIN) and num_players == 1:
                #para digitar o nome no leaderboard e também registrar no mesmo
                if event.key == pygame.K_BACKSPACE:
                    name_input = name_input[:-1]
                elif event.key == pygame.K_RETURN:
                    add_leaderboard_entry(name_input.strip(), score, meteors_destroyed, lives1)
                    load_leaderboard()
                else:
                    if len(name_input) < 12 and event.unicode.isprintable() and event.unicode != "\r":
                        name_input += event.unicode

    if game_state == STATE_MENU:
        screen.blit(background_img, (0, 0))

        box = pygame.Surface((750, 570))
        box.set_alpha(220)
        box.fill((240, 240, 240))
        box_rect = box.get_rect(center=(WIDTH//2, HEIGHT//2))
        screen.blit(box, box_rect)

        center_x = box_rect.centerx

        title = big_font.render("Aura Farming Pony", True, BLACK)
        screen.blit(title, title.get_rect(center=(center_x, box_rect.top + 90)))

        subtitle = small_font.render("Escolha o modo:", True, BLACK)
        screen.blit(subtitle, subtitle.get_rect(center=(center_x, box_rect.top + 180)))

        if has_saved_game:
            continue_button.center        = (center_x, box_rect.top + 255)
            start1_button.center          = (center_x, box_rect.top + 315)
            start2_button.center          = (center_x, box_rect.top + 375)
            leaderboard_menu_button.center = (center_x, box_rect.top + 435)
            credits_button.center         = (center_x, box_rect.top + 495)

            pygame.draw.rect(screen, WHITE, continue_button, border_radius=10)
            tcont = small_font.render("Continuar", True, BLACK)
            screen.blit(tcont, tcont.get_rect(center=continue_button.center))
        else:
            start1_button.center          = (center_x, box_rect.top + 285)
            start2_button.center          = (center_x, box_rect.top + 345)
            leaderboard_menu_button.center = (center_x, box_rect.top + 405)
            credits_button.center         = (center_x, box_rect.top + 465)

        pygame.draw.rect(screen, WHITE, start1_button, border_radius=10)
        t1 = small_font.render("Novo jogo (1 Jogador)", True, BLACK)
        screen.blit(t1, t1.get_rect(center=start1_button.center))

        pygame.draw.rect(screen, WHITE, start2_button, border_radius=10)
        t2 = small_font.render("Novo jogo (2 Jogadores)", True, BLACK)
        screen.blit(t2, t2.get_rect(center=start2_button.center))

        pygame.draw.rect(screen, WHITE, leaderboard_menu_button, border_radius=10)
        tlm = small_font.render("Leaderboard", True, BLACK)
        screen.blit(tlm, tlm.get_rect(center=leaderboard_menu_button.center))

        pygame.draw.rect(screen, WHITE, credits_button, border_radius=10)
        tc = small_font.render("Créditos", True, BLACK)
        screen.blit(tc, tc.get_rect(center=credits_button.center))

    elif game_state == STATE_PLAYING:
        if phase_name == "Fase 1":
            screen.blit(background_fase1, (0, 0))
        elif phase_name == "Fase 2":
            screen.blit(background_fase2, (0, 0))
        else:
            screen.blit(background_fase3, (0, 0))

        atualizar_fase(score)

        keys = pygame.key.get_pressed()

        p1_speed = 6
        p2_speed = 6

        if speed1_timer > 0:
            p1_speed += speed_boost_amount
            speed1_timer -= 1

        if speed2_timer > 0:
            p2_speed += speed_boost_amount
            speed2_timer -= 1

        if keys[pygame.K_a] and player_rect.left > 0:
            player_rect.x -= p1_speed
        if keys[pygame.K_d] and player_rect.right < WIDTH:
            player_rect.x += p1_speed
        if keys[pygame.K_w] and player_rect.top > HEIGHT//2:
            player_rect.y -= p1_speed
        if keys[pygame.K_s] and player_rect.bottom < HEIGHT:
            player_rect.y += p1_speed

        if num_players == 2:
            if keys[pygame.K_LEFT] and player2_rect.left > 0:
                player2_rect.x -= p2_speed
            if keys[pygame.K_RIGHT] and player2_rect.right < WIDTH:
                player2_rect.x += p2_speed
            if keys[pygame.K_UP] and player2_rect.top > HEIGHT//2:
                player2_rect.y -= p2_speed
            if keys[pygame.K_DOWN] and player2_rect.bottom < HEIGHT:
                player2_rect.y += p2_speed

        for bullet in bullets[:]:
            rect = bullet["rect"]
            rect.x += bullet["vx"]
            rect.y += bullet["vy"]
            if rect.bottom < 0 or rect.top > HEIGHT or rect.right < 0 or rect.left > WIDTH:
                bullets.remove(bullet)
                continue
            hit = False
            if phase_name != "Fase 3":
                for meteor in meteor_list:
                    if meteor.colliderect(rect):
                        meteor.y = random.randint(-300, -METEOR_H)
                        meteor.x = random.randint(0, WIDTH - METEOR_W)
                        score += 1
                        meteors_destroyed += 1
                        if sound_point:
                            sound_point.play()
                        hit = True
                        break
            if not hit:
                for sm in strong_meteor_list:
                    if sm.colliderect(rect):
                        if phase_name == "Fase 3":
                            sm.y = random.randint(-600, -STR_METEOR_H)
                        else:
                            sm.y = random.randint(-6000, -STR_METEOR_H)
                        sm.x = random.randint(0, WIDTH - STR_METEOR_W)
                        score += 1
                        meteors_destroyed += 1
                        if sound_point:
                            sound_point.play()
                        hit = True
                        break
            if hit and bullet in bullets:
                bullets.remove(bullet)

        if phase_name != "Fase 3":
            for meteor in meteor_list:
                meteor.y += meteor_speed

                if meteor.y > HEIGHT:
                    meteor.y = random.randint(-300, -METEOR_H)
                    meteor.x = random.randint(0, WIDTH - METEOR_W)
                    score += 1
                    if sound_point:
                        sound_point.play()

                if meteor.colliderect(player_rect) and lives1 > 0:
                    if shield1_active:
                        shield1_active = False
                    else:
                        lives1 -= 1
                    meteor.y = random.randint(-300, -METEOR_H)
                    meteor.x = random.randint(0, WIDTH - METEOR_W)
                    if sound_hit:
                        sound_hit.play()

                if num_players == 2 and meteor.colliderect(player2_rect) and lives2 > 0:
                    if shield2_active:
                        shield2_active = False
                    else:
                        lives2 -= 1
                    meteor.y = random.randint(-300, -METEOR_H)
                    meteor.x = random.randint(0, WIDTH - METEOR_W)
                    if sound_hit:
                        sound_hit.play()

        for sm in strong_meteor_list:
            sm.y += int(meteor_speed * 1.5)

            if sm.y > HEIGHT:
                if phase_name == "Fase 3":
                    sm.y = random.randint(-600, -STR_METEOR_H)
                else:
                    sm.y = random.randint(-6000, -STR_METEOR_H)
                sm.x = random.randint(0, WIDTH - STR_METEOR_W)
                score += 1
                if sound_point:
                    sound_point.play()

            if sm.colliderect(player_rect) and lives1 > 0:
                if shield1_active:
                    shield1_active = False
                else:
                    lives1 -= 2
                    if lives1 < 0:
                        lives1 = 0
                if phase_name == "Fase 3":
                    sm.y = random.randint(-600, -STR_METEOR_H)
                else:
                    sm.y = random.randint(-6000, -STR_METEOR_H)
                sm.x = random.randint(0, WIDTH - STR_METEOR_W)
                if sound_hit:
                    sound_hit.play()

            if num_players == 2 and sm.colliderect(player2_rect) and lives2 > 0:
                if shield2_active:
                    shield2_active = False
                else:
                    lives2 -= 2
                    if lives2 < 0:
                        lives2 = 0
                if phase_name == "Fase 3":
                    sm.y = random.randint(-600, -STR_METEOR_H)
                else:
                    sm.y = random.randint(-6000, -STR_METEOR_H)
                sm.x = random.randint(0, WIDTH - STR_METEOR_W)
                if sound_hit:
                    sound_hit.play()

        for life in life_list:
            life.y += meteor_speed - 1
            if life.y > HEIGHT:
                life.y = random.randint(-4500, -LIFE_H)
                life.x = random.randint(0, WIDTH - LIFE_W)
            if life.colliderect(player_rect) and lives1 < 3:
                lives1 += 1
                life.y = random.randint(-4500, -LIFE_H)
                life.x = random.randint(0, WIDTH - LIFE_W)
            if num_players == 2 and life.colliderect(player2_rect) and lives2 < 3:
                lives2 += 1
                life.y = random.randint(-4500, -LIFE_H)
                life.x = random.randint(0, WIDTH - LIFE_W)

        for shield in shield_list:
            shield.y += meteor_speed - 1
            if shield.y > HEIGHT:
                shield.y = random.randint(-4500, -SHIELD_H)
                shield.x = random.randint(0, WIDTH - SHIELD_W)
            if shield.colliderect(player_rect):
                shield1_active = True
                shield.y = random.randint(-4500, -SHIELD_H)
                shield.x = random.randint(0, WIDTH - SHIELD_W)
            if num_players == 2 and shield.colliderect(player2_rect):
                shield2_active = True
                shield.y = random.randint(-4500, -SHIELD_H)
                shield.x = random.randint(0, WIDTH - SHIELD_W)

        for sp in speed_list:
            sp.y += meteor_speed - 1
            if sp.y > HEIGHT:
                sp.y = random.randint(-6000, -SPEED_H)
                sp.x = random.randint(0, WIDTH - SPEED_W)
            if sp.colliderect(player_rect):
                speed1_timer = FPS * 5
                sp.y = random.randint(-6000, -SPEED_H)
                sp.x = random.randint(0, WIDTH - SPEED_W)
            if num_players == 2 and sp.colliderect(player2_rect):
                speed2_timer = FPS * 5
                sp.y = random.randint(-6000, -SPEED_H)
                sp.x = random.randint(0, WIDTH - SPEED_W)

        if num_players == 1 and lives1 <= 0:
            game_state = STATE_OVER
            pygame.mixer.music.stop()

        if num_players == 2:
            if lives1 <= 0 and lives2 > 0:
                winner_text = "Jogador 2 venceu!"
                game_state = STATE_PVP_WIN
                pygame.mixer.music.stop()
            elif lives2 <= 0 and lives1 > 0:
                winner_text = "Jogador 1 venceu!"
                game_state = STATE_PVP_WIN
                pygame.mixer.music.stop()
            elif lives1 <= 0 and lives2 <= 0:
                game_state = STATE_OVER
                pygame.mixer.music.stop()

        if score >= 100:
            game_state = STATE_WIN
            pygame.mixer.music.stop()

        if shield1_active:
            sx = player_rect.centerx - shield_surf.get_width() // 2
            sy = player_rect.centery - shield_surf.get_height() // 2
            screen.blit(shield_surf, (sx, sy))

        screen.blit(player_img, player_rect)

        if num_players == 2 and lives2 > 0:
            if shield2_active:
                sx2 = player2_rect.centerx - shield_surf.get_width() // 2
                sy2 = player2_rect.centery - shield_surf.get_height() // 2
                screen.blit(shield_surf, (sx2, sy2))
            screen.blit(player2_img, player2_rect)

        for bullet in bullets:
            pygame.draw.rect(screen, RED, bullet["rect"])

        if phase_name != "Fase 3":
            for meteor in meteor_list:
                screen.blit(meteor_img, meteor)

        for sm in strong_meteor_list:
            screen.blit(meteor_strong_img, sm)

        for life in life_list:
            screen.blit(life_img, life)
        for shield in shield_list:
            screen.blit(shield_img, shield)
        for sp in speed_list:
            screen.blit(speed_img, sp)

        hud = pygame.Surface((975, 60))
        hud.set_alpha(180)
        hud.fill((230, 230, 230))
        screen.blit(hud, (10, 10))

        if num_players == 1:
            texto = f"Pontos: {score}   Vidas: {lives1}   {phase_name}"
        else:
            texto = f"Pontos: {score}   Vidas P1: {lives1}   Vidas P2: {lives2}   {phase_name}"

        screen.blit(font.render(texto, True, BLACK), (20, 20))

        if phase_alert_timer > 0:
            aviso = big_font.render(phase_name, True, BLACK)
            rect = aviso.get_rect(center=(WIDTH//2, HEIGHT//2))
            box = pygame.Surface((rect.width + 60, rect.height + 30))
            box.set_alpha(200)
            box.fill(WHITE)
            screen.blit(box, box.get_rect(center=rect.center))
            screen.blit(aviso, rect)
            phase_alert_timer -= 1

    elif game_state == STATE_OVER:
        screen.blit(background_gameover, (0, 0))

        box = pygame.Surface((750, 480))
        box.set_alpha(230)
        box.fill((240, 240, 240))
        box_rect = box.get_rect(center=(WIDTH//2, HEIGHT//2))
        screen.blit(box, box_rect)

        t = big_font.render("GAME OVER", True, BLACK)
        screen.blit(t, t.get_rect(center=(WIDTH//2, box_rect.top + 70)))

        tscore = font.render(f"Pontuação final: {score}", True, BLACK)
        screen.blit(tscore, tscore.get_rect(center=(WIDTH//2, box_rect.top + 130)))

        if num_players == 1:
            tstats = small_font.render(f"Meteoros destruídos: {meteors_destroyed}  Vidas finais: {lives1}", True, BLACK)
            screen.blit(tstats, tstats.get_rect(center=(WIDTH//2, box_rect.top + 170)))
            tname = small_font.render(f"Seu nome: {name_input}", True, BLACK)
            screen.blit(tname, tname.get_rect(center=(WIDTH//2, box_rect.top + 210)))
            best = get_best_entry()
            if best:
                trec = small_font.render(
                    f"Recorde: {best['name']} - {best['score']} pts, {best['destroyed']} meteoros, {best['lives']} vidas",
                    True, BLACK
                )
                screen.blit(trec, trec.get_rect(center=(WIDTH//2, box_rect.top + 250)))
            thint = small_font.render("Digite seu nome e clique em 'Salvar no Leaderboard'", True, BLACK)
            screen.blit(thint, thint.get_rect(center=(WIDTH//2, box_rect.top + 285)))

        restart_button.center     = (WIDTH//2, box_rect.top + 340)
        quit_button.center        = (WIDTH//2, box_rect.top + 395)
        leaderboard_button.center = (WIDTH//2, box_rect.top + 450)

        pygame.draw.rect(screen, WHITE, restart_button, border_radius=10)
        tr = small_font.render("Reiniciar", True, BLACK)
        screen.blit(tr, tr.get_rect(center=restart_button.center))

        pygame.draw.rect(screen, WHITE, quit_button, border_radius=10)
        tq = small_font.render("Sair", True, BLACK)
        screen.blit(tq, tq.get_rect(center=quit_button.center))

        pygame.draw.rect(screen, WHITE, leaderboard_button, border_radius=10)
        tl = small_font.render("Salvar no Leaderboard", True, BLACK)
        screen.blit(tl, tl.get_rect(center=leaderboard_button.center))

    elif game_state == STATE_WIN:
        screen.blit(background_win, (0, 0))

        box = pygame.Surface((750, 480))
        box.set_alpha(230)
        box.fill((240, 240, 240))
        box_rect = box.get_rect(center=(WIDTH//2, HEIGHT//2))
        screen.blit(box, box_rect)

        t = big_font.render("VOCÊ VENCEU!", True, BLACK)
        screen.blit(t, t.get_rect(center=(WIDTH//2, box_rect.top + 70)))

        tscore = font.render(f"Pontuação: {score}", True, BLACK)
        screen.blit(tscore, tscore.get_rect(center=(WIDTH//2, box_rect.top + 130)))

        if num_players == 1:
            tstats = small_font.render(f"Meteoros destruídos: {meteors_destroyidos}  Vidas finais: {lives1}", True, BLACK)
            screen.blit(tstats, tstats.get_rect(center=(WIDTH//2, box_rect.top + 170)))
            tname = small_font.render(f"Seu nome: {name_input}", True, BLACK)
            screen.blit(tname, tname.get_rect(center=(WIDTH//2, box_rect.top + 210)))
            best = get_best_entry()
            if best:
                trec = small_font.render(
                    f"Recorde: {best['name']} - {best['score']} pts, {best['destroyed']} meteoros, {best['lives']} vidas",
                    True, BLACK
                )
                screen.blit(trec, trec.get_rect(center=(WIDTH//2, box_rect.top + 250)))
            thint = small_font.render("Digite seu nome e clique em 'Salvar no Leaderboard'", True, BLACK)
            screen.blit(thint, thint.get_rect(center=(WIDTH//2, box_rect.top + 285)))

        restart_button.center     = (WIDTH//2, box_rect.top + 340)
        quit_button.center        = (WIDTH//2, box_rect.top + 395)
        leaderboard_button.center = (WIDTH//2, box_rect.top + 450)

        pygame.draw.rect(screen, WHITE, restart_button, border_radius=10)
        tr = small_font.render("Reiniciar", True, BLACK)
        screen.blit(tr, tr.get_rect(center=restart_button.center))

        pygame.draw.rect(screen, WHITE, quit_button, border_radius=10)
        tq = small_font.render("Sair", True, BLACK)
        screen.blit(tq, tq.get_rect(center=quit_button.center))

        pygame.draw.rect(screen, WHITE, leaderboard_button, border_radius=10)
        tl = small_font.render("Salvar no Leaderboard", True, BLACK)
        screen.blit(tl, tl.get_rect(center=leaderboard_button.center))

    elif game_state == STATE_CREDITS:
        screen.blit(background_img, (0, 0))

        box = pygame.Surface((750, 450))
        box.set_alpha(230)
        box.fill((240, 240, 240))
        screen.blit(box, box.get_rect(center=(WIDTH//2, HEIGHT//2)))

        t = big_font.render("Créditos", True, BLACK)
        screen.blit(t, t.get_rect(center=(WIDTH//2, HEIGHT//2 - 120)))

        c = small_font.render("Criadores: Rafaela Linck e Miguel Matos", True, BLACK)
        screen.blit(c, c.get_rect(center=(WIDTH//2, HEIGHT//2 - 30)))

        pygame.draw.rect(screen, WHITE, back_button, border_radius=10)
        tb = small_font.render("Voltar", True, BLACK)
        screen.blit(tb, tb.get_rect(center=back_button.center))

    elif game_state == STATE_PVP_WIN:
        screen.blit(background_win, (0, 0))

        box = pygame.Surface((750, 375))
        box.set_alpha(230)
        box.fill((240, 240, 240))
        screen.blit(box, box.get_rect(center=(WIDTH//2, HEIGHT//2)))

        t = big_font.render("FIM DE JOGO", True, BLACK)
        screen.blit(t, t.get_rect(center=(WIDTH//2, HEIGHT//2 - 105)))

        tw = font.render(winner_text, True, BLACK)
        screen.blit(tw, tw.get_rect(center=(WIDTH//2, HEIGHT//2 - 30)))

        pygame.draw.rect(screen, WHITE, pvp_menu_button, border_radius=10)
        tm = small_font.render("Menu principal", True, BLACK)
        screen.blit(tm, tm.get_rect(center=pvp_menu_button.center))

    elif game_state == STATE_PAUSED:
        screen.blit(background_img, (0, 0))

        box = pygame.Surface((750, 375))
        box.set_alpha(230)
        box.fill((240, 240, 240))
        screen.blit(box, box.get_rect(center=(WIDTH//2, HEIGHT//2)))

        t = big_font.render("PAUSADO", True, BLACK)
        screen.blit(t, t.get_rect(center=(WIDTH//2, HEIGHT//2 - 105)))

        pygame.draw.rect(screen, WHITE, pause_continue_button, border_radius=10)
        tp = small_font.render("Continuar jogando", True, BLACK)
        screen.blit(tp, tp.get_rect(center=pause_continue_button.center))

        pygame.draw.rect(screen, WHITE, pause_menu_button, border_radius=10)
        tm = small_font.render("Salvar e ir ao menu", True, BLACK)
        screen.blit(tm, tm.get_rect(center=pause_menu_button.center))

    elif game_state == STATE_LEADERBOARD:
        screen.blit(background_img, (0, 0))

        box = pygame.Surface((800, 500))
        box.set_alpha(230)
        box.fill((240, 240, 240))
        box_rect = box.get_rect(center=(WIDTH//2, HEIGHT//2))
        screen.blit(box, box_rect)

        t = big_font.render("Leaderboard", True, BLACK)
        screen.blit(t, t.get_rect(center=(WIDTH//2, box_rect.top + 80)))

        #vai mostrar o top 5 no leaderboard
        if leaderboard:
            start_y = box_rect.top + 150
            for i, entry in enumerate(leaderboard[:5]):
                line = f"{i+1}. {entry['name']} - {entry['score']} pts, {entry['destroyed']} meteoros, {entry['lives']} vidas"
                tl = small_font.render(line, True, BLACK)
                screen.blit(tl, tl.get_rect(center=(WIDTH//2, start_y + i*40)))
        else:
            tl = small_font.render("Nenhum registro ainda.", True, BLACK)
            screen.blit(tl, tl.get_rect(center=(WIDTH//2, box_rect.top + 180)))

        pygame.draw.rect(screen, WHITE, back_button, border_radius=10)
        tb = small_font.render("Voltar ao menu", True, BLACK)
        screen.blit(tb, tb.get_rect(center=back_button.center))

    pygame.display.flip()

pygame.quit()
