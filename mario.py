import pygame
import sys

# --- CONFIGURATION & CONSTANTS ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 440
FPS = 60

# NES Color Palette Constants
COLOR_SKY = (107, 140, 255)
COLOR_MARIO = (228, 0, 88)
COLOR_GROUND = (228, 92, 16)
COLOR_BRICK = (184, 72, 0)
COLOR_BLOCK = (252, 156, 18)

# Physics Constants (Tuned to feel like Super Mario Bros.)
GRAVITY = 0.5
ACCEL = 0.3
FRICTION = 0.85
MAX_SPEED = 4.5
JUMP_FORCE = -10.5

# Level Map (1-1 Style Layout Snippet)
# G = Ground, B = Brick, ? = Question Block
LEVEL_MAP = [
    "                                                                                ",
    "                                                                                ",
    "                                                                                ",
    "                                                                                ",
    "                                                                                ",
    "                                                                                ",
    "                                                                                ",
    "                                                                                ",
    "                                    ?  B?B?B                                    ",
    "                                                                                ",
    "                                                                                ",
    "                   ?   B?B?B                                                    ",
    "                                                                                ",
    "                                                                                ",
    "GGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG   GGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG",
    "GGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG   GGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG",
]

TILE_SIZE = SCREEN_HEIGHT // len(LEVEL_MAP)  # 27px per tile


class Block(pygame.sprite.Sprite):
    def __init__(self, x, y, block_type):
        super().__init__()
        self.block_type = block_type
        self.image = pygame.Surface((TILE_SIZE, TILE_SIZE))
        
        if block_type == 'G':
            self.image.fill(COLOR_GROUND)
        elif block_type == 'B':
            self.image.fill(COLOR_BRICK)
        elif block_type == '?':
            self.image.fill(COLOR_BLOCK)
            
        pygame.draw.rect(self.image, (0, 0, 0), self.image.get_rect(), 1)  # Border
        self.rect = self.image.get_rect(topleft=(x, y))


class Mario(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((TILE_SIZE - 4, TILE_SIZE * 1.2))
        self.image.fill(COLOR_MARIO)
        self.rect = self.image.get_rect(topleft=(x, y))
        
        self.vx = 0
        self.vy = 0
        self.on_ground = False

    def update(self, tiles):
        # --- Horizontal Movement ---
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.vx -= ACCEL
        elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.vx += ACCEL
        else:
            self.vx *= FRICTION

        # Speed Clamp
        self.vx = max(-MAX_SPEED, min(MAX_SPEED, self.vx))
        if abs(self.vx) < 0.1:
            self.vx = 0

        # Move X & Check Collision
        self.rect.x += self.vx
        self.collide(self.vx, 0, tiles)

        # --- Vertical Movement & Gravity ---
        self.vy += GRAVITY
        if self.vy > 12:  # Terminal Velocity
            self.vy = 12

        # Move Y & Check Collision
        self.rect.y += self.vy
        self.on_ground = False
        self.collide(0, self.vy, tiles)

    def jump(self):
        if self.on_ground:
            self.vy = JUMP_FORCE

    def collide(self, vx, vy, tiles):
        for tile in tiles:
            if self.rect.colliderect(tile.rect):
                if vx > 0:  # Moving Right
                    self.rect.right = tile.rect.left
                    self.vx = 0
                if vx < 0:  # Moving Left
                    self.rect.left = tile.rect.right
                    self.vx = 0
                if vy > 0:  # Falling
                    self.rect.bottom = tile.rect.top
                    self.vy = 0
                    self.on_ground = True
                if vy < 0:  # Jumping into block
                    self.rect.top = tile.rect.bottom
                    self.vy = 0


def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Super Mario Bros. - Replica Engine")
    clock = pygame.time.Clock()

    # Create Level Tiles
    tiles = pygame.sprite.Group()
    for row_idx, row in enumerate(LEVEL_MAP):
        for col_idx, tile_char in enumerate(row):
            if tile_char in ['G', 'B', '?']:
                block = Block(col_idx * TILE_SIZE, row_idx * TILE_SIZE, tile_char)
                tiles.add(block)

    # Create Player
    mario = Mario(100, 100)
    all_sprites = pygame.sprite.Group(tiles, mario)

    camera_x = 0

    # Main Game Loop
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_SPACE, pygame.K_UP, pygame.K_w):
                    mario.jump()

        # Update Game Objects
        mario.update(tiles)

        # Camera Following Mario (Scrolls Right like original NES)
        if mario.rect.x - camera_x > SCREEN_WIDTH // 2:
            camera_x = mario.rect.x - SCREEN_WIDTH // 2

        # Draw Frame
        screen.fill(COLOR_SKY)

        for sprite in all_sprites:
            # Shift rendering relative to Camera Offset
            screen.blit(sprite.image, (sprite.rect.x - camera_x, sprite.rect.y))

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()