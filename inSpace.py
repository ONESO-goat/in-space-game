import pygame
import random
import sys

pygame.init()
pygame.font.init()



SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1080
FPS = 60

# Colors
WHITE = (255, 255, 255)
GRAY = (100, 100, 100)
ORANGE = (255, 165, 0)
BLUE = (0, 0, 255)
RED = (200, 0, 0)
BLACK = (0, 0, 0)
YELLOW = (255, 255, 0)

# Fonts
UI_FONT = pygame.font.SysFont("Arial", 40, True)



class Player:
    def __init__(self):
        self.radius = 35
        self.pos = pygame.Vector2(SCREEN_WIDTH//2, SCREEN_HEIGHT - 100)
        self.speed = 400  # pixels per second
        self.invincible = False
        self.invincible_timer = 0

    def move(self, dt, keys):
        move_speed = self.speed
        if keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]:
            move_speed *= 2

        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            self.pos.x -= move_speed * dt
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            self.pos.x += move_speed * dt
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            self.pos.y -= move_speed * dt
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            self.pos.y += move_speed * dt

        # Clamp inside screen
        self.pos.x = max(self.radius, min(SCREEN_WIDTH - self.radius, self.pos.x))
        self.pos.y = max(self.radius, min(SCREEN_HEIGHT - self.radius, self.pos.y))

    def draw(self, surface):
        color = WHITE if not self.invincible else ORANGE
        pygame.draw.circle(surface, color, (int(self.pos.x), int(self.pos.y)), self.radius)

    def update_invincible(self, dt):
        if self.invincible:
            self.invincible_timer -= dt
            if self.invincible_timer <= 0:
                self.invincible = False

class Rock:
    def __init__(self, speed_multiplier=1.0):
        self.width = random.choice([200, 300, 400])
        self.height = random.choice([20, 30, 50, 80])
        self.pos = pygame.Vector2(random.randint(self.width//2, SCREEN_WIDTH - self.width//2), -self.height)
        self.speed = random.randint(100, 250) * speed_multiplier  # pixels per second

    def update(self, dt):
        self.pos.y += self.speed * dt

    def draw(self, surface):
        pygame.draw.rect(surface, GRAY, (self.pos.x - self.width//2, self.pos.y, self.width, self.height))

    def off_screen(self):
        return self.pos.y > SCREEN_HEIGHT + self.height

class Powerup:
    def __init__(self, kind):
        self.kind = kind
        self.pos = pygame.Vector2(random.randint(50, SCREEN_WIDTH - 50), -50)
        self.radius = 20 if kind != "wrench" else 30
        self.speed = 200  # falling speed

    def update(self, dt):
        self.pos.y += self.speed * dt

    def draw(self, surface):
        color = ORANGE if self.kind=="boost" else BLUE if self.kind=="wrench" else RED
        pygame.draw.circle(surface, color, (int(self.pos.x), int(self.pos.y)), self.radius)

    def off_screen(self):
        return self.pos.y > SCREEN_HEIGHT + self.radius

class Star:
    def __init__(self):
        self.pos = pygame.Vector2(random.randint(0, SCREEN_WIDTH), random.randint(0, SCREEN_HEIGHT))
        self.speed = random.uniform(20, 100)
        self.size = random.randint(1, 3)

    def update(self, dt):
        self.pos.y += self.speed * dt
        if self.pos.y > SCREEN_HEIGHT:
            self.pos.y = 0
            self.pos.x = random.randint(0, SCREEN_WIDTH)

    def draw(self, surface):
        pygame.draw.circle(surface, YELLOW, (int(self.pos.x), int(self.pos.y)), self.size)




screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Space Rock Dodger")
clock = pygame.time.Clock()

# Player
player = Player()

# Rocks
rocks = []
rock_spawn_timer = 0.0
rock_spawn_interval = 1.5  # seconds
max_rocks = 5

# Powerups
powerups = []
powerup_spawn_timer = 0.0
powerup_spawn_interval = 5.0  # seconds

# stars
stars = [Star() for _ in range(100)]


lives = 3
score = 0
lightyears = 0




running = True
while running:
    dt = clock.tick(FPS) / 1000  # Delta time in seconds

    # ----------------- EVENTS -----------------
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()
    if keys[pygame.K_ESCAPE]:
        running = False



    player.move(dt, keys)
    player.update_invincible(dt)



    for star in stars:
        star.update(dt)



    for rock in rocks:
        rock.update(dt)

    # remove off-screen rocks
    rocks = [r for r in rocks if not r.off_screen()]


    # spawn rocks
    rock_spawn_timer += dt
    if rock_spawn_timer >= rock_spawn_interval:
        rock_spawn_timer = 0
        if len(rocks) < max_rocks:
            rocks.append(Rock(speed_multiplier=1 + lightyears/500000))  # increase speed gradually

    # Update powerups
    for powerup in powerups:
        powerup.update(dt)
    # Remove off-screen powerups
    powerups = [p for p in powerups if not p.off_screen()]

    # powerups spawn
    powerup_spawn_timer += dt
    if powerup_spawn_timer >= powerup_spawn_interval:
        powerup_spawn_timer = 0
        powerups.append(Powerup(random.choice(["boost","wrench","invincible"])))

    # Collision detection
    for rock in rocks:
        rock_rect = pygame.Rect(rock.pos.x - rock.width//2, rock.pos.y, rock.width, rock.height)
        player_rect = pygame.Rect(player.pos.x - player.radius, player.pos.y - player.radius, player.radius*2, player.radius*2)
        if player_rect.colliderect(rock_rect) and not player.invincible:
            lives -= 1
            player.invincible = True
            player.invincible_timer = 1.5  # 1.5 seconds invincibility after hit

    for powerup in powerups[:]:
        if (player.pos - powerup.pos).length() < player.radius + powerup.radius:
            if powerup.kind == "boost":
                player.speed *= 2
                # boost lasts 3 seconds
                pygame.time.set_timer(pygame.USEREVENT + 1, 3000, True)
            elif powerup.kind == "wrench":
                lives += 1
            elif powerup.kind == "invincible":
                player.invincible = True
                player.invincible_timer = 3.0
            powerups.remove(powerup)

    # Score
    lightyears += int(1000 * dt)

    # Increase max rocks over time (difficulty)
    max_rocks = min(20, 5 + lightyears // 50000)



    screen.fill(BLACK)


    for star in stars:
        star.draw(screen)


    for rock in rocks:
        rock.draw(screen)


    for powerup in powerups:
        powerup.draw(screen)


    player.draw(screen)

    # Draw UI
    score_surface = UI_FONT.render(f"LIGHT-YEARS: {lightyears}", True, WHITE)
    screen.blit(score_surface, (50, 50))
    lives_surface = UI_FONT.render(f"LIVES: {lives}", True, WHITE)
    screen.blit(lives_surface, (SCREEN_WIDTH - 200, 50))

    pygame.display.flip()

    # game ends/over
    if lives <= 0:
        print("GAME OVER! Final Lightyears:", lightyears)
        running = False

pygame.quit()
sys.exit()
