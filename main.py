import pygame
import math

pygame.init()
pygame.mixer.init()

WIDTH, HEIGHT = 900, 650
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Cartoon Channel - Final")

clock = pygame.time.Clock()

# -------- SOUND --------
try:
    pygame.mixer.music.load("assets/bg_music.wav")
    pygame.mixer.music.set_volume(0.4)
    pygame.mixer.music.play(-1)
    click = pygame.mixer.Sound("assets/click.wav")
except:
    click = None

# -------- VIEWPORT --------
TV_X, TV_Y = 80, 90
TV_W, TV_H = 740, 420

font = pygame.font.SysFont(None, 28)
big_font = pygame.font.SysFont(None, 42)

# -------- SPRITE SYSTEM --------
class SpriteAnimation:
    def __init__(self, sheet, fw, fh, scale=2):
        self.frames = []
        self.index = 0
        self.timer = 0

        img = pygame.image.load(sheet).convert_alpha()
        cols = img.get_width() // fw
        rows = img.get_height() // fh

        for y in range(rows):
            for x in range(cols):
                frame = img.subsurface((x*fw, y*fh, fw, fh))
                frame = pygame.transform.scale(frame, (fw*scale, fh*scale))
                self.frames.append(frame)

    def update(self, speed):
        self.timer += speed
        if self.timer >= 1:
            self.timer = 0
            self.index = (self.index + 1) % len(self.frames)

    def get(self):
        return self.frames[self.index]

# -------- LOAD ASSETS --------
idle = SpriteAnimation("assets/thickIdleSheet.png", 64, 64)
run = SpriteAnimation("assets/thickRunSheet.png", 64, 64)
punch = SpriteAnimation("assets/thickPunchSheet.png", 64, 64)

ball_img = pygame.transform.scale(pygame.image.load("assets/ball.png"), (40,40))
car_img = pygame.transform.scale(pygame.image.load("assets/car.png"), (180,90))

# -------- STATE --------
channel = 0

player_x = 200
player_target = 200
player_dir = 1
player_state = "idle"

enemy_x = 600
enemy_health = 100
enemy_alive = True

ball_x, ball_y = 200, 150
ball_vx, ball_vy = 4, -5

car_x = -200

title_alpha = 0

# -------- PARALLAX --------
cloud_offset = 0
mountain_offset = 0
tree_offset = 0

# -------- UTILS --------
def lerp(a, b, t):
    return a + (b-a)*t

def draw_text(text, x, y, big=False):
    f = big_font if big else font
    screen.blit(f.render(text, True, (255,255,255)), (x,y))

# -------- BACKGROUND --------
def draw_basic_bg():
    pygame.draw.rect(screen, (135,206,235), (TV_X, TV_Y, TV_W, TV_H))
    pygame.draw.rect(screen, (70,180,80), (TV_X, TV_Y+300, TV_W, 120))

def draw_parallax():
    global cloud_offset, mountain_offset, tree_offset

    pygame.draw.rect(screen, (135,206,235), (TV_X, TV_Y, TV_W, TV_H))

    # clouds
    for i in range(-2, 6):
        x = (i*200 - cloud_offset) % (TV_W+200) - 100 + TV_X
        pygame.draw.ellipse(screen, (255,255,255), (x, TV_Y+40, 120, 60))

    # mountains
    for i in range(-2, 6):
        x = (i*250 - mountain_offset) % (TV_W+250) - 125 + TV_X
        pygame.draw.polygon(screen, (100,120,100), [
            (x, TV_Y+300),
            (x+125, TV_Y+150),
            (x+250, TV_Y+300)
        ])

    # trees
    for i in range(-3, 8):
        x = (i*120 - tree_offset) % (TV_W+120) - 60 + TV_X
        pygame.draw.rect(screen, (90,60,30), (x+20, TV_Y+260, 10, 40))
        pygame.draw.circle(screen, (40,140,60), (x+25, TV_Y+250), 20)

    pygame.draw.rect(screen, (70,180,80), (TV_X, TV_Y+300, TV_W, 120))

    cloud_offset += 0.3
    mountain_offset += 0.8
    tree_offset += 2

# -------- CHANNEL 1 --------
def draw_fight():
    global player_x, player_target, player_state, player_dir, enemy_health
    global enemy_alive, enemy_health

    keys = pygame.key.get_pressed()

    if keys[pygame.K_RIGHT]:
        player_target += 5
        player_state = "run"
        player_dir = 1
    elif keys[pygame.K_LEFT]:
        player_target -= 5
        player_state = "run"
        player_dir = -1
    elif keys[pygame.K_SPACE]:
        player_state = "punch"
    else:
        player_state = "idle"

    player_x = lerp(player_x, player_target, 0.2)

    draw_basic_bg()

    px = TV_X + player_x
    py = TV_Y + 240
    ex = TV_X + enemy_x

    if player_state == "idle":
        idle.update(0.15)
        frame = idle.get()
    elif player_state == "run":
        run.update(0.25)
        frame = run.get()
    else:
        punch.update(0.3)
        frame = punch.get()

    if player_dir == -1:
        frame = pygame.transform.flip(frame, True, False)

    screen.blit(frame, (px, py))

    if enemy_alive:
        idle.update(0.1)
        screen.blit(idle.get(), (ex, py))
    

    if enemy_alive and player_state == "punch" and abs(player_x - enemy_x) < 80:
        enemy_health -= 0.5
        if enemy_health <= 0:
            enemy_health = 0
            enemy_alive = False
        
    

    pygame.draw.rect(screen, (255,0,0), (TV_X+500, TV_Y+20, enemy_health*2, 10))

# -------- CHANNEL 2 --------
def draw_ball():
    global ball_x, ball_y, ball_vx, ball_vy

    draw_basic_bg()

    bx = TV_X + ball_x
    by = TV_Y + ball_y

    screen.blit(ball_img, (bx, by))

    ball_x += ball_vx
    ball_y += ball_vy
    ball_vy += 0.3

    if ball_x <= 0 or ball_x >= TV_W-40:
        ball_vx *= -1

    if ball_y >= 260:
        ball_y = 260
        ball_vy *= -0.85

# -------- CHANNEL 3 --------
def draw_car():
    global car_x

    draw_parallax()

    cx = TV_X + car_x
    cy = TV_Y + 255

    bob = math.sin(pygame.time.get_ticks()*0.005)*3
    screen.blit(car_img, (cx, cy + bob))

    car_x += 5
    if car_x > TV_W:
        car_x = -200

# -------- MAIN LOOP --------
running = True

while running:
    screen.fill((20,20,30))

    pygame.draw.rect(screen, (60,60,60),
        (TV_X-10, TV_Y-10, TV_W+20, TV_H+20), border_radius=12)

    screen.set_clip(pygame.Rect(TV_X, TV_Y, TV_W, TV_H))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_1:
                channel = 1
                if click: click.play()
            elif event.key == pygame.K_2:
                channel = 2
                if click: click.play()
            elif event.key == pygame.K_3:
                channel = 3
                if click: click.play()
            elif event.key == pygame.K_ESCAPE:
                running = False

    if channel == 0:
        draw_basic_bg()
        draw_text("CARTOON CHANNEL", 260, TV_Y+120, True)
        draw_text("Press 1 - Fight", 300, TV_Y+200)
        draw_text("Press 2 - Ball Physics", 300, TV_Y+240)
        draw_text("Press 3 - Car (Parallax)", 300, TV_Y+280)

    elif channel == 1:
        draw_fight()

    elif channel == 2:
        draw_ball()

    elif channel == 3:
        draw_car()

    screen.set_clip(None)

    # title fade
    if title_alpha < 255:
        title_alpha += 2

    title_surface = big_font.render("Cartoon Channel", True, (255,255,255))
    title_surface.set_alpha(title_alpha)
    screen.blit(title_surface, (260, 30))

    channel_names = {
        0: "Menu",
        1: "Fight Animation",
        2: "Ball Physics",
        3: "Car Parallax Demo"
    }

    draw_text(f"Now Playing: {channel_names[channel]}", 260, 65)

    pygame.display.update()
    clock.tick(60)

pygame.quit()