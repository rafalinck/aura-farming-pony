import pygame
import random
import os

pygame.init()

#configuração inicial (res, fps, etc)
WIDTH, HEIGHT = 800, 600
FPS = 60
pygame.display.set_caption("Space Escape")

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED   = (255, 60, 60)
BLUE  = (60, 100, 255)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

#configurações básicas dos assets (player, fundo, sons, etc) [se não souber fazer, é só colocar o arquivo dentro da mesma pasta do .py e copiar o url e colar entre as aspas ali]
ASSETS = {
    "background": "-",
    "player": "-",
    "meteor": "-",
    "sound_point": "-",
    "sound_hit": "-",
    "music": "-",
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
player_img  = load_image(ASSETS["player"], BLUE, (80, 60))
player2_img = player_img
meteor_img  = load_image(ASSETS["meteor"], RED, (40, 40))
METEOR_W, METEOR_H = meteor_img.get_width(), meteor_img.get_height()

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
font       = pygame.font.Font(None, 36)
big_font   = pygame.font.Font(None, 72)
small_font = pygame.font.Font(None, 28)

STATE_MENU    = "MENU"
STATE_PLAYING = "JOGANDO"
STATE_OVER    = "GAME_OVER"
STATE_WIN     = "VITORIA"
STATE_CREDITS = "CREDITOS"

game_state = STATE_MENU

#variáveis do jogo
score = 0
lives1 = 3
lives2 = 3
num_players = 1

phase_name = "Fase 1"
phase_alert_timer = 0

player_rect  = player_img.get_rect(center=(WIDTH // 2, HEIGHT - 60))
player2_rect = player2_img.get_rect(center=(WIDTH // 2 + 100, HEIGHT - 60))

meteor_list = []
NUM_METEORS = 6
meteor_speed = 3

def criar_meteoros():
    global meteor_list
    meteor_list = []
    for _ in range(NUM_METEORS):
        x = random.randint(0, WIDTH - METEOR_W)
        y = random.randint(-400, -METEOR_H)
        meteor_list.append(pygame.Rect(x, y, METEOR_W, METEOR_H))

def atualizar_fase(score):
    """Define fase, velocidade e dispara aviso se mudar."""
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
button_width  = 260
button_height = 60

start1_button = pygame.Rect(WIDTH//2 - button_width//2, HEIGHT//2 - 20,
                            button_width, button_height)
start2_button = pygame.Rect(WIDTH//2 - button_width//2, HEIGHT//2 + 60,
                            button_width, button_height)
credits_button = pygame.Rect(WIDTH//2 - button_width//2, HEIGHT//2 + 140,
                             button_width, button_height)

restart_button = pygame.Rect(WIDTH//2 - 100, HEIGHT//2,      200, 50)
quit_button    = pygame.Rect(WIDTH//2 - 100, HEIGHT//2 + 60, 200, 50)

back_button = pygame.Rect(20, HEIGHT - 70, 160, 40)

#código para reiniciar o jogo
def reset_game():
    global score, lives1, lives2, game_state, phase_name

    score = 0
    lives1 = 3
    lives2 = 3
    phase_name = "Fase 1"
    game_state = STATE_PLAYING

    if num_players == 1:
        player_rect.center  = (WIDTH // 2, HEIGHT - 60)
        player2_rect.center = (-200, -200)
    else:
        player_rect.center  = (WIDTH // 2 - 100, HEIGHT - 60)
        player2_rect.center = (WIDTH // 2 + 100, HEIGHT - 60)

    criar_meteoros()
    play_music()

#loop principal do jogo
running = True
while running:
    clock.tick(FPS)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos

            if game_state == STATE_MENU:
                if start1_button.collidepoint(mx, my):
                    num_players = 1
                    reset_game()
                elif start2_button.collidepoint(mx, my):
                    num_players = 2
                    reset_game()
                elif credits_button.collidepoint(mx, my):
                    game_state = STATE_CREDITS
                    pygame.mixer.music.stop()

            elif game_state in (STATE_OVER, STATE_WIN):
                if restart_button.collidepoint(mx, my):
                    reset_game()
                elif quit_button.collidepoint(mx, my):
                    running = False

            elif game_state == STATE_CREDITS:
                if back_button.collidepoint(mx, my):
                    game_state = STATE_MENU

    #menu do jogo e estados
    if game_state == STATE_MENU:
        screen.blit(background_img, (0, 0))

        box = pygame.Surface((500, 380))
        box.set_alpha(220)
        box.fill((240, 240, 240))
        screen.blit(box, box.get_rect(center=(WIDTH//2, HEIGHT//2)))

        title = big_font.render("SPACE ESCAPE", True, BLACK)
        screen.blit(title, title.get_rect(center=(WIDTH//2, HEIGHT//2 - 140)))

        subtitle = small_font.render("Escolha o modo:", True, BLACK)
        screen.blit(subtitle, subtitle.get_rect(center=(WIDTH//2, HEIGHT//2 - 60)))

        pygame.draw.rect(screen, WHITE, start1_button, border_radius=10)
        t1 = small_font.render("1 Jogador", True, BLACK)
        screen.blit(t1, t1.get_rect(center=start1_button.center))

        pygame.draw.rect(screen, WHITE, start2_button, border_radius=10)
        t2 = small_font.render("2 Jogadores (WASD + Setas)", True, BLACK)
        screen.blit(t2, t2.get_rect(center=start2_button.center))

        pygame.draw.rect(screen, WHITE, credits_button, border_radius=10)
        tc = small_font.render("Créditos", True, BLACK)
        screen.blit(tc, tc.get_rect(center=credits_button.center))

    elif game_state == STATE_PLAYING:
        screen.blit(background_img, (0, 0))

        atualizar_fase(score)

        keys = pygame.key.get_pressed()

        if keys[pygame.K_a] and player_rect.left > 0:
            player_rect.x -= 6
        if keys[pygame.K_d] and player_rect.right < WIDTH:
            player_rect.x += 6
        if keys[pygame.K_w] and player_rect.top > HEIGHT//2:
            player_rect.y -= 6
        if keys[pygame.K_s] and player_rect.bottom < HEIGHT:
            player_rect.y += 6

        if num_players == 2:
            if keys[pygame.K_LEFT] and player2_rect.left > 0:
                player2_rect.x -= 6
            if keys[pygame.K_RIGHT] and player2_rect.right < WIDTH:
                player2_rect.x += 6
            if keys[pygame.K_UP] and player2_rect.top > HEIGHT//2:
                player2_rect.y -= 6
            if keys[pygame.K_DOWN] and player2_rect.bottom < HEIGHT:
                player2_rect.y += 6

        for meteor in meteor_list:
            meteor.y += meteor_speed

            if meteor.y > HEIGHT:
                meteor.y = random.randint(-200, -METEOR_H)
                meteor.x = random.randint(0, WIDTH - METEOR_W)
                score += 1
                if sound_point:
                    sound_point.play()

            if meteor.colliderect(player_rect) and lives1 > 0:
                lives1 -= 1
                meteor.y = random.randint(-200, -METEOR_H)
                meteor.x = random.randint(0, WIDTH - METEOR_W)
                if sound_hit:
                    sound_hit.play()

            if num_players == 2 and meteor.colliderect(player2_rect) and lives2 > 0:
                lives2 -= 1
                meteor.y = random.randint(-200, -METEOR_H)
                meteor.x = random.randint(0, WIDTH - METEOR_W)
                if sound_hit:
                    sound_hit.play()

        if num_players == 1 and lives1 <= 0:
            game_state = STATE_OVER
            pygame.mixer.music.stop()
        if num_players == 2 and lives1 <= 0 and lives2 <= 0:
            game_state = STATE_OVER
            pygame.mixer.music.stop()

        if score >= 100:
            game_state = STATE_WIN
            pygame.mixer.music.stop()

        screen.blit(player_img, player_rect)
        if num_players == 2 and lives2 > 0:
            screen.blit(player2_img, player2_rect)

        for meteor in meteor_list:
            screen.blit(meteor_img, meteor)

        hud = pygame.Surface((650, 40))
        hud.set_alpha(180)
        hud.fill((230, 230, 230))
        screen.blit(hud, (10, 10))

        if num_players == 1:
            texto = f"Pontos: {score}   Vidas: {lives1}   {phase_name}"
        else:
            texto = f"Pontos: {score}   Vidas P1: {lives1}   Vidas P2: {lives2}   {phase_name}"

        screen.blit(font.render(texto, True, BLACK), (20, 15))

        if phase_alert_timer > 0:
            aviso = big_font.render(phase_name, True, BLACK)
            rect = aviso.get_rect(center=(WIDTH//2, HEIGHT//2))
            box = pygame.Surface((rect.width + 40, rect.height + 20))
            box.set_alpha(200)
            box.fill(WHITE)
            screen.blit(box, box.get_rect(center=rect.center))
            screen.blit(aviso, rect)
            phase_alert_timer -= 1

    elif game_state == STATE_OVER:
        screen.blit(background_img, (0, 0))

        box = pygame.Surface((500, 250))
        box.set_alpha(230)
        box.fill((240, 240, 240))
        screen.blit(box, box.get_rect(center=(WIDTH//2, HEIGHT//2)))

        t = big_font.render("GAME OVER", True, BLACK)
        screen.blit(t, t.get_rect(center=(WIDTH//2, HEIGHT//2 - 70)))

        tscore = font.render(f"Pontuação final: {score}", True, BLACK)
        screen.blit(tscore, tscore.get_rect(center=(WIDTH//2, HEIGHT//2 - 20)))

        pygame.draw.rect(screen, WHITE, restart_button, border_radius=10)
        tr = small_font.render("Reiniciar", True, BLACK)
        screen.blit(tr, tr.get_rect(center=restart_button.center))

        pygame.draw.rect(screen, WHITE, quit_button, border_radius=10)
        tq = small_font.render("Sair", True, BLACK)
        screen.blit(tq, tq.get_rect(center=quit_button.center))

    elif game_state == STATE_WIN:
        screen.blit(background_img, (0, 0))

        box = pygame.Surface((500, 250))
        box.set_alpha(230)
        box.fill((240, 240, 240))
        screen.blit(box, box.get_rect(center=(WIDTH//2, HEIGHT//2)))

        t = big_font.render("VOCÊ VENCEU!", True, BLACK)
        screen.blit(t, t.get_rect(center=(WIDTH//2, HEIGHT//2 - 70)))

        tscore = font.render(f"Pontuação: {score}", True, BLACK)
        screen.blit(tscore, tscore.get_rect(center=(WIDTH//2, HEIGHT//2 - 20)))

        pygame.draw.rect(screen, WHITE, restart_button, border_radius=10)
        tr = small_font.render("Reiniciar", True, BLACK)
        screen.blit(tr, tr.get_rect(center=restart_button.center))

        pygame.draw.rect(screen, WHITE, quit_button, border_radius=10)
        tq = small_font.render("Sair", True, BLACK)
        screen.blit(tq, tq.get_rect(center=quit_button.center))

    elif game_state == STATE_CREDITS:
        screen.blit(background_img, (0, 0))

        box = pygame.Surface((500, 300))
        box.set_alpha(230)
        box.fill((240, 240, 240))
        screen.blit(box, box.get_rect(center=(WIDTH//2, HEIGHT//2)))

        t = big_font.render("Créditos", True, BLACK)
        screen.blit(t, t.get_rect(center=(WIDTH//2, HEIGHT//2 - 80)))

        c = small_font.render("Criadores: Rafaela Linck e Miguel Matos", True, BLACK)
        screen.blit(c, c.get_rect(center=(WIDTH//2, HEIGHT//2 - 20)))

        pygame.draw.rect(screen, WHITE, back_button, border_radius=10)
        tb = small_font.render("Voltar", True, BLACK)
        screen.blit(tb, tb.get_rect(center=back_button.center))

    pygame.display.flip()

pygame.quit()
