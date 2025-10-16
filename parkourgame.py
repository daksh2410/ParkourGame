import pygame
import random
import os

# --- Constants ---
WIDTH = 800
HEIGHT = 600
FPS = 60

# Player properties
PLAYER_ACC = 0.8
PLAYER_FRICTION = -0.12
PLAYER_GRAVITY = 0.7
PLAYER_JUMP = -16
PLAYER_WALL_JUMP_POWER = 12
PLAYER_FLY_SPEED = 5

# Game properties
INITIAL_SCROLL_SPEED = 4.0
SCROLL_SPEED_INCREMENT = 0.005

# Generation properties
MAX_JUMP_DISTANCE = 260
MIN_GAP = 50
POWERUP_SPAWN_CHANCE = 0.1

# Colors
WHITE = (255, 255, 255); BLACK = (0, 0, 0); RED = (255, 0, 0)
GREEN = (40, 180, 99); BROWN = (133, 87, 35); STONE_GREY = (128, 128, 128)
SKY_TOP = (135, 206, 250); SKY_BOTTOM = (210, 240, 255)
COOLDOWN_BAR_BG = (50, 50, 50)
COOLDOWN_BAR_FILL = (60, 180, 255)
FLIGHT_BAR_FILL = (255, 215, 0)

# Asset paths
HIGHSCORE_FILE = "parkour_highscore.txt"

# --- Procedural Asset Creation ---
def create_player_image():
    image = pygame.Surface((30, 40), pygame.SRCALPHA)
    body_color = (52, 152, 219); head_color = (46, 204, 113)
    pygame.draw.rect(image, body_color, (0, 10, 30, 30))
    pygame.draw.rect(image, head_color, (5, 0, 20, 15))
    return image

def create_player_image_with_cape():
    image = create_player_image()
    cape_points = [(5, 15), (-15, 25), (5, 35)]
    pygame.draw.polygon(image, RED, cape_points)
    return image

def create_platform_image(width, height, p_type):
    image = pygame.Surface((width, height), pygame.SRCALPHA)
    if p_type == "floor":
        pygame.draw.rect(image, BROWN, (0, 0, width, height))
        pygame.draw.rect(image, GREEN, (0, 0, width, 10))
        pygame.draw.rect(image, BLACK, (0, 0, width, height), 2)
    else: # "wall"
        pygame.draw.rect(image, STONE_GREY, (0, 0, width, height))
        for _ in range(15):
            crack_x, crack_y = random.randint(5, width - 5), random.randint(5, height - 5)
            crack_len = random.randint(5, 10)
            pygame.draw.line(image, (0,0,0,50), (crack_x, crack_y), (crack_x + crack_len, crack_y + crack_len), 1)
        pygame.draw.rect(image, BLACK, (0, 0, width, height), 2)
    return image

def create_powerup_image():
    image = pygame.Surface((30, 30), pygame.SRCALPHA)
    pygame.draw.ellipse(image, WHITE, (0, 0, 20, 30))
    pygame.draw.line(image, STONE_GREY, (10, 0), (10, 30), 2)
    return image

def create_background_image():
    image = pygame.Surface((WIDTH, HEIGHT)).convert()
    for y in range(HEIGHT):
        c = SKY_TOP[0] + (SKY_BOTTOM[0] - SKY_TOP[0]) * y // HEIGHT
        color = (c, c + 20, c + 30)
        pygame.draw.line(image, color, (0, y), (WIDTH, y))
    for _ in range(15):
        cx, cy = random.randint(0, WIDTH), random.randint(50, HEIGHT // 2)
        cw, ch = random.randint(50, 150), random.randint(20, 40)
        cloud_surface = pygame.Surface((cw, ch), pygame.SRCALPHA)
        pygame.draw.ellipse(cloud_surface, (255, 255, 255, random.randint(100, 180)), (0, 0, cw, ch))
        image.blit(cloud_surface, (cx, cy))
    return image

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Horizontal Parkour Runner")
        self.clock = pygame.time.Clock()
        self.running = True
        self.font_name = pygame.font.match_font('arial')
        self.load_data()

    def load_data(self):
        self.dir = os.path.dirname(__file__)
        hs_file_path = os.path.join(self.dir, HIGHSCORE_FILE)
        try:
            with open(hs_file_path, 'r') as f: self.highscore = int(f.read())
        except (IOError, ValueError): self.highscore = 0
        self.background_img = create_background_image()
        self.bg_x = 0

    def save_highscore(self):
        hs_file_path = os.path.join(self.dir, HIGHSCORE_FILE)
        with open(hs_file_path, 'w') as f: f.write(str(self.highscore))

    def new(self):
        self.jumps_made = 0; self.score = 0
        self.scroll_speed = INITIAL_SCROLL_SPEED
        self.double_jump_timer = 0
        self.is_flying = False; self.flight_timer = 0
        self.all_sprites = pygame.sprite.Group()
        self.platforms = pygame.sprite.Group()
        self.powerups = pygame.sprite.Group()
        self.player = Player(self)
        self.all_sprites.add(self.player)
        p1 = Platform(self, 0, HEIGHT - 40, WIDTH, 40, "floor")
        self.all_sprites.add(p1)
        self.platforms.add(p1)
        self.rightmost_edge = p1.rect.right
        self.run()

    def start_double_jump_cooldown(self):
        self.double_jump_timer = FPS

    def activate_flight(self):
        self.is_flying = True
        self.flight_timer = 5 * FPS

    def run(self):
        self.playing = True
        while self.playing:
            self.clock.tick(FPS)
            self.events()
            self.update()
            self.draw()

    def update(self):
        if self.double_jump_timer > 0: self.double_jump_timer -= 1
        if self.is_flying:
            self.flight_timer -= 1
            if self.flight_timer <= 0:
                self.is_flying = False
        
        self.all_sprites.update()
        
        self.score += int(self.scroll_speed)

        # Stateless Generation Logic
        while self.rightmost_edge < WIDTH * 2:
            anchor_platform = None
            rightmost_floor_x = -float('inf')
            for plat in self.platforms:
                if plat.p_type == "floor" and plat.rect.right > rightmost_floor_x:
                    rightmost_floor_x = plat.rect.right
                    anchor_platform = plat
            if anchor_platform is None:
                anchor_platform = Platform(self, self.rightmost_edge, HEIGHT - 40, 100, 40, "floor")

            anchor_width = anchor_platform.rect.width; anchor_x = anchor_platform.rect.right; anchor_y = anchor_platform.rect.y
            y_change = random.randrange(-100, 100)
            adjusted_max_jump = MAX_JUMP_DISTANCE - (abs(y_change) * 0.4)
            max_gap = max(MIN_GAP + 1, adjusted_max_jump - anchor_width)
            gap = random.randrange(MIN_GAP, int(max_gap))
            plat_y = anchor_y + y_change
            plat_y = max(150, min(HEIGHT - 40, plat_y))
            if random.random() < 0.75:
                plat_width, p_type = random.randrange(100, 200), "floor"; plat_height = 40
            else:
                plat_width, p_type = 40, "wall"; plat_height = random.randrange(150, 300)
            new_plat = Platform(self, anchor_x + gap, plat_y, plat_width, plat_height, p_type)
            self.platforms.add(new_plat)
            self.all_sprites.add(new_plat)
            self.rightmost_edge = max(self.rightmost_edge, new_plat.rect.right)
            if new_plat.p_type == 'floor' and random.random() < POWERUP_SPAWN_CHANCE:
                powerup = Powerup(self, new_plat)
                self.all_sprites.add(powerup)
                self.powerups.add(powerup)

        new_rightmost_edge = 0
        for plat in list(self.platforms):
            if plat.rect.right < -100: plat.kill()
            else: new_rightmost_edge = max(new_rightmost_edge, plat.rect.right)
        self.rightmost_edge = new_rightmost_edge

        self.scroll_speed += SCROLL_SPEED_INCREMENT
        if self.player.rect.right < 0 or self.player.rect.top > HEIGHT:
            self.playing = False

    def events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                if self.playing: self.playing = False
                self.running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE or event.key == pygame.K_UP:
                    self.player.jump()

    def draw(self):
        self.bg_x -= self.scroll_speed * 0.25
        if self.bg_x < -WIDTH: self.bg_x = 0
        self.screen.blit(self.background_img, (self.bg_x, 0))
        self.screen.blit(self.background_img, (self.bg_x + WIDTH, 0))
        self.all_sprites.draw(self.screen)
        self.draw_text(f"Best: {self.highscore // 10}", 20, BLACK, 15, 10, align="topleft")
        self.draw_text(f"Distance: {self.score // 10}", 22, BLACK, WIDTH / 2, 15)
        self.draw_text(f"Jumps: {self.jumps_made}", 20, BLACK, WIDTH - 15, 10, align="topright")
        self.draw_cooldown_bar()
        if self.is_flying: self.draw_flight_bar()
        pygame.display.flip()

    def draw_cooldown_bar(self):
        bar_w, bar_h, bar_y = 150, 25, HEIGHT - 40
        bar_x = WIDTH / 2 - bar_w / 2
        if self.is_flying: bar_x -= (bar_w / 2 + 10)
        fill_ratio = (FPS - self.double_jump_timer) / FPS
        fill_w = bar_w * fill_ratio
        pygame.draw.rect(self.screen, COOLDOWN_BAR_BG, (bar_x, bar_y, bar_w, bar_h))
        pygame.draw.rect(self.screen, COOLDOWN_BAR_FILL, (bar_x, bar_y, fill_w, bar_h))
        pygame.draw.rect(self.screen, BLACK, (bar_x, bar_y, bar_w, bar_h), 2)
        label_color = WHITE if fill_ratio < 0.5 else BLACK
        self.draw_text("Double Jump", 16, label_color, bar_x + bar_w / 2, bar_y + bar_h / 2)

    def draw_flight_bar(self):
        bar_w, bar_h, bar_y = 150, 25, HEIGHT - 40
        bar_x = WIDTH / 2 + 10
        fill_ratio = self.flight_timer / (5 * FPS)
        fill_w = bar_w * fill_ratio
        pygame.draw.rect(self.screen, COOLDOWN_BAR_BG, (bar_x, bar_y, bar_w, bar_h))
        pygame.draw.rect(self.screen, FLIGHT_BAR_FILL, (bar_x, bar_y, fill_w, bar_h))
        pygame.draw.rect(self.screen, BLACK, (bar_x, bar_y, bar_w, bar_h), 2)
        self.draw_text("Flight", 16, BLACK, bar_x + bar_w / 2, bar_y + bar_h / 2)

    def show_start_screen(self):
        self.screen.blit(self.background_img, (0, 0))
        self.draw_text("PARKOUR RUNNER", 48, BLACK, WIDTH / 2, HEIGHT / 4)
        self.draw_text("A/D to move, SPACE to Jump/Double Jump", 22, BLACK, WIDTH / 2, HEIGHT / 2 - 15)
        self.draw_text("W/S or UP/DOWN to fly with powerup", 22, BLACK, WIDTH / 2, HEIGHT / 2 + 15)
        self.draw_text("Press any key to start", 22, BLACK, WIDTH / 2, HEIGHT * 3 / 4)
        self.draw_text(f"High Score: {self.highscore // 10}", 22, BLACK, WIDTH / 2, HEIGHT * 3 / 4 + 40)
        pygame.display.flip()
        self.wait_for_key()

    def show_go_screen(self):
        if not self.running: return
        self.screen.blit(self.background_img, (0, 0))
        is_new_highscore = self.score > self.highscore
        if is_new_highscore:
            self.highscore = self.score; self.save_highscore()
        final_score_display = self.score // 10; highscore_display = self.highscore // 10
        self.draw_text("GAME OVER", 48, BLACK, WIDTH / 2, HEIGHT / 4)
        y_pos = HEIGHT / 2 - 20
        self.draw_text(f"Score: {final_score_display}", 22, BLACK, WIDTH / 2, y_pos)
        self.draw_text(f"Jumps: {self.jumps_made}", 22, BLACK, WIDTH / 2, y_pos + 40)
        self.draw_text(f"Best: {highscore_display}", 22, BLACK, WIDTH / 2, y_pos + 80)
        if is_new_highscore:
            self.draw_text("New High Score!", 22, RED, WIDTH / 2, y_pos + 120)
        self.draw_text("Press any key to return to menu", 22, BLACK, WIDTH / 2, HEIGHT * 3 / 4 + 20)
        pygame.display.flip()
        self.wait_for_key()
    
    def wait_for_key(self):
        waiting = True
        while waiting:
            self.clock.tick(FPS)
            for event in pygame.event.get():
                if event.type == pygame.QUIT: waiting = False; self.running = False
                if event.type == pygame.KEYUP: waiting = False

    def draw_text(self, text, size, color, x, y, align="center"):
        font = pygame.font.Font(self.font_name, size)
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect()
        if align == "center": text_rect.center = (x, y)
        elif align == "topleft": text_rect.topleft = (x, y)
        elif align == "topright": text_rect.topright = (x, y)
        self.screen.blit(text_surface, text_rect)

class Player(pygame.sprite.Sprite):
    def __init__(self, game):
        super().__init__()
        self.game = game
        self.image_normal = create_player_image()
        self.image_flying = create_player_image_with_cape()
        self.image = self.image_normal
        self.rect = self.image.get_rect(center=(WIDTH / 4, HEIGHT - 80))
        self.vel = pygame.math.Vector2(0, 0)
        self.on_ground = False
        self.touching_wall = 0
        self.can_double_jump = True

    def jump(self):
        if self.game.is_flying: return
        if self.on_ground or self.touching_wall:
            self.vel.y = PLAYER_JUMP; self.game.jumps_made += 1; self.can_double_jump = True
        elif self.can_double_jump and self.game.double_jump_timer <= 0:
            self.vel.y = PLAYER_JUMP; self.game.jumps_made += 1
            self.can_double_jump = False; self.game.start_double_jump_cooldown()

    def update(self):
        # 1. Determine acceleration and velocity based on input and state
        keys = pygame.key.get_pressed()
        acc = pygame.math.Vector2(0, 0)
        if keys[pygame.K_LEFT] or keys[pygame.K_a]: acc.x = -PLAYER_ACC
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]: acc.x = PLAYER_ACC

        if self.game.is_flying:
            self.image = self.image_flying
            self.vel.y = 0
            if keys[pygame.K_UP] or keys[pygame.K_w]: self.vel.y = -PLAYER_FLY_SPEED
            if keys[pygame.K_DOWN] or keys[pygame.K_s]: self.vel.y = PLAYER_FLY_SPEED
        else:
            self.image = self.image_normal
            acc.y = PLAYER_GRAVITY

        # 2. Apply physics
        acc.x += self.vel.x * PLAYER_FRICTION
        self.vel += acc
        if not self.game.is_flying:
            if self.vel.y > 15: self.vel.y = 15

        # 3. Collision-aware movement using the rect as the single source of truth
        # Move horizontally
        self.rect.x += self.vel.x
        if self.on_ground and not self.game.is_flying:
             self.rect.x -= self.game.scroll_speed
        
        hits = pygame.sprite.spritecollide(self, self.game.platforms, False)
        for hit in hits:
            if self.vel.x > 0: self.rect.right = hit.rect.left
            elif self.vel.x < 0: self.rect.left = hit.rect.right
            self.vel.x = 0
        
        # Move vertically
        self.rect.y += self.vel.y
        self.on_ground = False
        
        hits = pygame.sprite.spritecollide(self, self.game.platforms, False)
        for hit in hits:
            if self.vel.y > 0:
                self.rect.bottom = hit.rect.top
                if not self.game.is_flying:
                    self.on_ground = True
                    self.can_double_jump = True
            elif self.vel.y < 0:
                self.rect.top = hit.rect.bottom
            self.vel.y = 0
        
        # 4. Check for powerup collection
        powerup_hits = pygame.sprite.spritecollide(self, self.game.powerups, True)
        if powerup_hits:
            self.game.activate_flight()

class Powerup(pygame.sprite.Sprite):
    def __init__(self, game, platform):
        super().__init__()
        self.game = game
        self.platform = platform
        self.image = create_powerup_image()
        self.rect = self.image.get_rect()
        self.rect.centerx = self.platform.rect.centerx
        self.rect.bottom = self.platform.rect.top - 5

    def update(self):
        if not self.platform.alive():
            self.kill()
            return
        # Stay on top of the parent platform, which is scrolled by its own update method
        self.rect.centerx = self.platform.rect.centerx

class Platform(pygame.sprite.Sprite):
    def __init__(self, game, x, y, w, h, p_type):
        super().__init__()
        self.game = game
        self.p_type = p_type
        self.image = create_platform_image(w, h, p_type)
        self.rect = self.image.get_rect(topleft=(x, y))

    # --- FIX: Restore the scrolling logic here ---
    def update(self):
        self.rect.x -= self.game.scroll_speed

def main():
    game = Game()
    while game.running:
        game.show_start_screen()
        if not game.running: break
        game.new()
        if not game.running: break
        game.show_go_screen()

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\nAN ERROR OCCURRED: {e}")
        import traceback
        traceback.print_exc()
        input("\nPress Enter to exit.")
    finally:
        pygame.quit()