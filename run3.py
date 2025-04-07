import pygame
import random
import math

# Initialize Pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 800, 600
FPS = 60
GRAVITY = 0.5
JUMP_FORCE = -12
MOVE_SPEED = 5
ROTATION_SPEED = 5
SCROLL_SPEED = 3
DASH_FORCE = 15
DASH_COOLDOWN = 60
COMBO_TIMER = 120  # 2 seconds at 60 FPS
SCREEN_SHAKE_DURATION = 10
SCREEN_SHAKE_INTENSITY = 5
COMBO_DECAY = 1
COMBO_MULTIPLIER = 0.2

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 120, 255)
RED = (255, 50, 50)
GREEN = (50, 200, 50)
YELLOW = (255, 200, 0)
PURPLE = (150, 50, 255)
DARK_BLUE = (0, 0, 100)
LIGHT_BLUE = (100, 200, 255)
ORANGE = (255, 150, 50)
CYAN = (0, 255, 255)
MAGENTA = (255, 0, 255)

# Create the game window
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Run 3")
clock = pygame.time.Clock()

class Projectile:
    def __init__(self, x, y, target_x, target_y):
        self.x = x
        self.y = y
        self.radius = 5
        self.color = ORANGE
        self.speed = 7
        
        # Calculate direction
        dx = target_x - x
        dy = target_y - y
        distance = math.sqrt(dx * dx + dy * dy)
        self.vx = (dx / distance) * self.speed
        self.vy = (dy / distance) * self.speed

    def update(self):
        self.x += self.vx
        self.y += self.vy

    def draw(self, surface):
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.radius)
        # Add glow effect
        glow_surface = pygame.Surface((self.radius * 4, self.radius * 4), pygame.SRCALPHA)
        pygame.draw.circle(glow_surface, (*self.color[:3], 100), (self.radius * 2, self.radius * 2), self.radius * 2)
        surface.blit(glow_surface, (int(self.x) - self.radius * 2, int(self.y) - self.radius * 2))

class Monster:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 30
        self.height = 30
        self.color = PURPLE
        self.shoot_cooldown = 0
        self.shoot_delay = 120  # Increased from 60 to 120 frames between shots
        self.projectiles = []

    def update(self, player_x, player_y):
        self.x -= SCROLL_SPEED
        self.shoot_cooldown = max(0, self.shoot_cooldown - 1)
        
        # Shoot at player
        if self.shoot_cooldown == 0:
            self.shoot(player_x, player_y)
            self.shoot_cooldown = self.shoot_delay

        # Update projectiles
        for projectile in self.projectiles:
            projectile.update()

        # Remove projectiles that are off screen
        self.projectiles = [p for p in self.projectiles if 0 <= p.x <= WIDTH and 0 <= p.y <= HEIGHT]

    def shoot(self, target_x, target_y):
        self.projectiles.append(Projectile(self.x + self.width/2, self.y + self.height/2, target_x, target_y))

    def draw(self, surface):
        # Draw monster
        monster_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        pygame.draw.rect(monster_surface, self.color, (0, 0, self.width, self.height))
        
        # Add eyes
        pygame.draw.circle(monster_surface, RED, (self.width//3, self.height//3), 4)
        pygame.draw.circle(monster_surface, RED, (2*self.width//3, self.height//3), 4)
        
        surface.blit(monster_surface, (self.x, self.y))

        # Draw projectiles
        for projectile in self.projectiles:
            projectile.draw(surface)

class Powerup:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 20
        self.height = 20
        self.color = CYAN
        self.collected = False
        self.float_offset = 0
        self.float_speed = 0.1
        self.glow_radius = 0
        self.glow_direction = 1

    def update(self):
        self.x -= SCROLL_SPEED
        # Floating animation
        self.float_offset = math.sin(pygame.time.get_ticks() * self.float_speed) * 5
        # Glow effect
        self.glow_radius += 0.2 * self.glow_direction
        if self.glow_radius > 5 or self.glow_radius < 0:
            self.glow_direction *= -1

    def draw(self, surface):
        # Draw glow effect
        glow_surface = pygame.Surface((self.width + 20, self.height + 20), pygame.SRCALPHA)
        glow_color = (*self.color[:3], 100)
        pygame.draw.rect(glow_surface, glow_color, 
                        (10, 10, self.width, self.height), border_radius=5)
        surface.blit(glow_surface, (self.x - 10, self.y - 10 + self.float_offset))

        # Draw powerup
        powerup_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        pygame.draw.rect(powerup_surface, self.color, 
                        (0, 0, self.width, self.height), border_radius=5)
        
        # Add shine effect
        pygame.draw.line(powerup_surface, (255, 255, 255, 150), 
                        (0, 0), (self.width, 0), 2)
        pygame.draw.line(powerup_surface, (255, 255, 255, 150), 
                        (0, 0), (0, self.height), 2)
        
        surface.blit(powerup_surface, (self.x, self.y + self.float_offset))

class Player:
    def __init__(self):
        self.width = 30
        self.height = 30
        self.x = WIDTH // 4
        self.y = HEIGHT // 2
        self.vel_y = 0
        self.rotation = 0
        self.is_jumping = False
        self.can_double_jump = True
        self.is_wall_running = False
        self.wall_run_direction = 0
        self.color = BLUE
        self.is_alive = True
        self.trail = []
        self.max_trail = 15
        self.jump_particles = []
        self.max_jump_particles = 30
        self.glow_radius = 0
        self.glow_direction = 1
        self.powerup_timer = 0
        self.has_jump_powerup = False
        # New attributes
        self.dash_cooldown = 0
        self.dash_direction = 0
        self.combo = 0
        self.combo_timer = 0
        self.landing_particles = []
        self.score_multiplier = 1
        self.is_dashing = False
        self.dash_trail = []
        self.dash_speed = 15
        self.dash_duration = 10
        self.dash_timer = 0
        self.dash_particles = []
        self.max_dash_particles = 20
        self.in_spaceship = False
        self.current_spaceship = None
        self.powerup_timers = {'shield': 0}
        self.shield_radius = 0
        self.shield_direction = 1

    def update(self, platforms, spikes, monsters, powerups):
        if not self.is_alive:
            return

        # If player is in a spaceship, update position with the spaceship
        if self.in_spaceship and self.current_spaceship:
            self.x = self.current_spaceship.x + self.current_spaceship.width // 2 - self.width // 2
            self.y = self.current_spaceship.y + self.current_spaceship.height // 2 - self.height // 2
            return

        # Update combo
        if self.combo > 0:
            self.combo_timer -= 1
            if self.combo_timer <= 0:
                self.combo = max(0, self.combo - COMBO_DECAY)
                self.score_multiplier = 1 + (self.combo * COMBO_MULTIPLIER)

        # Update powerups
        for powerup_type in self.powerup_timers:
            if self.powerup_timers[powerup_type] > 0:
                self.powerup_timers[powerup_type] -= 1
                if self.powerup_timers[powerup_type] <= 0:
                    self.powerups[powerup_type] = False

        # Update shield effect
        if self.powerups['shield']:
            self.shield_radius += 0.2 * self.shield_direction
            if self.shield_radius > 5 or self.shield_radius < 0:
                self.shield_direction *= -1

        # Update dash cooldown
        if self.dash_cooldown > 0:
            self.dash_cooldown -= 1

        # Update dash trail
        if self.is_dashing:
            self.dash_trail.append((self.x, self.y))
            if len(self.dash_trail) > 10:
                self.dash_trail.pop(0)

        # Update landing particles
        self.landing_particles = [(x, y, life - 1) for x, y, life in self.landing_particles if life > 0]

        # Update powerup timer
        if self.powerup_timer > 0:
            self.powerup_timer -= 1
            if self.powerup_timer == 0:
                self.has_jump_powerup = False

        # Check for powerup collection
        for powerup in powerups:
            if not powerup.collected and self.check_powerup_collision(powerup):
                powerup.collected = True
                self.has_jump_powerup = True
                self.powerup_timer = 300  # 5 seconds at 60 FPS

        # Update trail
        self.trail.append((self.x, self.y))
        if len(self.trail) > self.max_trail:
            self.trail.pop(0)

        # Update jump particles
        self.jump_particles = [(x, y, life - 1) for x, y, life in self.jump_particles if life > 0]

        # Update dash state
        if self.is_dashing:
            self.dash_timer -= 1
            if self.dash_timer <= 0:
                self.is_dashing = False
            else:
                self.x += self.dash_speed * self.dash_direction
                # Create more dash particles
                if random.random() < 0.3:
                    self.dash_particles.append((
                        self.x + random.randint(-5, 5),
                        self.y + random.randint(-5, 5),
                        random.randint(10, 20)
                    ))

        # Update dash particles
        self.dash_particles = [(x, y, life - 1) for x, y, life in self.dash_particles if life > 0]

        # Apply gravity
        if not self.is_wall_running:
            self.vel_y += GRAVITY
            self.y += self.vel_y

        # Wall running mechanics
        if self.is_wall_running:
            self.vel_y = 0
            self.y += self.wall_run_direction * 2
            self.rotation = 90 if self.wall_run_direction == 1 else -90
            self.can_double_jump = True

        # Check for platform collisions
        for platform in platforms:
            if self.check_collision(platform):
                if self.vel_y > 0:  # Falling
                    self.y = platform.y - self.height
                    self.vel_y = 0
                    self.is_jumping = False
                    self.is_wall_running = False
                    self.rotation = 0
                    self.can_double_jump = True
                    # Create landing particles
                    for _ in range(10):
                        self.landing_particles.append((
                            self.x + random.randint(-10, 10),
                            self.y + self.height,
                            random.randint(10, 20)
                        ))
                elif self.vel_y < 0:  # Jumping
                    self.y = platform.y + platform.height
                    self.vel_y = 0

        # Check for wall collisions
        for platform in platforms:
            if self.check_wall_collision(platform):
                if not self.is_wall_running and self.vel_y > 0:
                    self.is_wall_running = True
                    self.wall_run_direction = 1 if self.x < platform.x else -1
                    self.vel_y = 0
                    self.can_double_jump = True

        # Check for spike collisions
        for spike in spikes:
            if self.check_spike_collision(spike):
                self.is_alive = False
                return

        # Check for projectile collisions
        for monster in monsters:
            for projectile in monster.projectiles:
                if self.check_projectile_collision(projectile):
                    self.is_alive = False
                    return

        # Keep player in horizontal bounds
        if self.x < 0:
            self.x = 0
        elif self.x > WIDTH - self.width:
            self.x = WIDTH - self.width

    def check_collision(self, platform):
        return (self.x < platform.x + platform.width and
                self.x + self.width > platform.x and
                self.y + self.height > platform.y and
                self.y < platform.y + platform.height)

    def check_wall_collision(self, platform):
        return (self.y < platform.y + platform.height and
                self.y + self.height > platform.y and
                (self.x + self.width > platform.x and self.x < platform.x or
                 self.x < platform.x + platform.width and self.x + self.width > platform.x + platform.width))

    def check_spike_collision(self, spike):
        return (self.x < spike.x + spike.width and
                self.x + self.width > spike.x and
                self.y + self.height > spike.y and
                self.y < spike.y + spike.height)

    def check_projectile_collision(self, projectile):
        return (self.x < projectile.x + projectile.radius and
                self.x + self.width > projectile.x - projectile.radius and
                self.y < projectile.y + projectile.radius and
                self.y + self.height > projectile.y - projectile.radius)

    def check_powerup_collision(self, powerup):
        return (self.x < powerup.x + powerup.width and
                self.x + self.width > powerup.x and
                self.y + self.height > powerup.y and
                self.y < powerup.y + powerup.height)

    def jump(self):
        if not self.is_jumping and self.is_alive:
            jump_force = JUMP_FORCE * 1.5 if self.has_jump_powerup else JUMP_FORCE
            self.vel_y = jump_force
            self.is_jumping = True
            self.is_wall_running = False
            self.combo += 1
            self.combo_timer = COMBO_TIMER
            self.score_multiplier = min(5, 1 + self.combo * 0.2)
            
            # Create jump particles
            particle_count = 10 if self.has_jump_powerup else 5
            for _ in range(particle_count):
                self.jump_particles.append((
                    self.x + random.randint(-5, 5),
                    self.y + self.height,
                    random.randint(10, 20)
                ))

    def dash(self):
        if self.dash_cooldown == 0 and self.is_alive:
            self.is_dashing = True
            self.dash_cooldown = DASH_COOLDOWN
            self.dash_timer = self.dash_duration
            self.dash_direction = 1 if self.x < WIDTH // 2 else -1
            self.vel_y = 0
            
            # Create dash particles
            for _ in range(10):
                self.dash_particles.append((
                    self.x + random.randint(-5, 5),
                    self.y + random.randint(-5, 5),
                    random.randint(10, 20)
                ))

    def move_left(self):
        self.x -= MOVE_SPEED

    def move_right(self):
        self.x += MOVE_SPEED

    def stop_moving(self):
        pass

    def draw(self, surface):
        if not self.is_alive:
            return

        # Draw dash particles
        for x, y, life in self.dash_particles:
            alpha = int(255 * (life / 20))
            particle_color = (*self.color[:3], alpha)
            particle_surface = pygame.Surface((8, 8), pygame.SRCALPHA)
            pygame.draw.circle(particle_surface, particle_color, (4, 4), 4)
            surface.blit(particle_surface, (int(x), int(y)))

        # Draw dash trail
        if self.is_dashing:
            for i in range(5):
                alpha = int(255 * (1 - i/5))
                trail_color = (*self.color[:3], alpha)
                trail_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
                pygame.draw.rect(trail_surface, trail_color, (0, 0, self.width, self.height), border_radius=5)
                offset = -i * 10 * self.dash_direction
                surface.blit(trail_surface, (self.x + offset, self.y))

        # Draw landing particles
        for x, y, life in self.landing_particles:
            alpha = int(255 * (life / 20))
            particle_color = (*self.color[:3], alpha)
            particle_surface = pygame.Surface((6, 6), pygame.SRCALPHA)
            pygame.draw.circle(particle_surface, particle_color, (3, 3), 3)
            surface.blit(particle_surface, (int(x), int(y)))

        # Update glow effect
        self.glow_radius += 0.2 * self.glow_direction
        if self.glow_radius > 5 or self.glow_radius < 0:
            self.glow_direction *= -1

        # Draw trail with gradient
        for i, (trail_x, trail_y) in enumerate(self.trail):
            alpha = int(255 * (i / len(self.trail)))
            trail_color = (*self.color[:3], alpha)
            trail_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            
            # Draw trail with glow
            glow_surface = pygame.Surface((self.width + 10, self.height + 10), pygame.SRCALPHA)
            pygame.draw.rect(glow_surface, (*self.color[:3], alpha//2), 
                           (5, 5, self.width, self.height), border_radius=5)
            surface.blit(glow_surface, (trail_x - 5, trail_y - 5))
            
            # Draw trail cube
            pygame.draw.rect(trail_surface, trail_color, (0, 0, self.width, self.height), border_radius=5)
            surface.blit(trail_surface, (trail_x, trail_y))

        # Draw jump particles
        for x, y, life in self.jump_particles:
            alpha = int(255 * (life / 20))
            particle_color = (*self.color[:3], alpha)
            particle_surface = pygame.Surface((6, 6), pygame.SRCALPHA)
            pygame.draw.circle(particle_surface, particle_color, (3, 3), 3)
            surface.blit(particle_surface, (int(x), int(y)))

        # Draw player with enhanced effects
        player_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        
        # Enhanced glow effect when powered up
        glow_color = CYAN if self.has_jump_powerup else self.color
        glow_alpha = 150 if self.has_jump_powerup else 100
        glow_size = 15 if self.has_jump_powerup else 10
        
        # Draw outer glow
        glow_surface = pygame.Surface((self.width + glow_size, self.height + glow_size), pygame.SRCALPHA)
        pygame.draw.rect(glow_surface, (*glow_color[:3], glow_alpha), 
                        (glow_size//2, glow_size//2, self.width, self.height), border_radius=5)
        surface.blit(glow_surface, (self.x - glow_size//2, self.y - glow_size//2))
        
        # Draw main cube with gradient
        for i in range(self.height):
            alpha = int(255 * (1 - i / self.height))
            color = CYAN if self.has_jump_powerup else self.color
            color = (*color[:3], alpha)
            pygame.draw.line(player_surface, color, (0, i), (self.width, i))
        
        # Add highlight
        highlight = pygame.Surface((self.width//2, self.height//2), pygame.SRCALPHA)
        highlight.fill((255, 255, 255, 100))
        player_surface.blit(highlight, (self.width//4, self.height//4))
        
        # Add corner highlights
        corner_size = 5
        highlight_color = (255, 255, 255, 150)
        pygame.draw.rect(player_surface, highlight_color, 
                        (0, 0, corner_size, corner_size))
        pygame.draw.rect(player_surface, highlight_color, 
                        (self.width - corner_size, 0, corner_size, corner_size))
        pygame.draw.rect(player_surface, highlight_color, 
                        (0, self.height - corner_size, corner_size, corner_size))
        pygame.draw.rect(player_surface, highlight_color, 
                        (self.width - corner_size, self.height - corner_size, corner_size, corner_size))

        # Add powerup effects
        if self.has_jump_powerup:
            # Add pulsing effect
            pulse_size = int(5 * math.sin(pygame.time.get_ticks() * 0.01))
            pulse_surface = pygame.Surface((self.width + pulse_size*2, self.height + pulse_size*2), pygame.SRCALPHA)
            pygame.draw.rect(pulse_surface, (*CYAN[:3], 50), 
                           (pulse_size, pulse_size, self.width, self.height), border_radius=5)
            surface.blit(pulse_surface, (self.x - pulse_size, self.y - pulse_size))
            
            # Add sparkle effect
            if random.random() < 0.3:
                sparkle_x = self.x + random.randint(0, self.width)
                sparkle_y = self.y + random.randint(0, self.height)
                sparkle_surface = pygame.Surface((4, 4), pygame.SRCALPHA)
                pygame.draw.circle(sparkle_surface, (255, 255, 255, 200), (2, 2), 2)
                surface.blit(sparkle_surface, (sparkle_x, sparkle_y))

        # Rotate and draw the player
        rotated_surface = pygame.transform.rotate(player_surface, self.rotation)
        surface.blit(rotated_surface, (self.x, self.y))

        # Draw combo counter
        if self.combo > 1:
            font = pygame.font.Font(None, 24)
            combo_text = font.render(f"{self.combo}x COMBO!", True, YELLOW)
            combo_rect = combo_text.get_rect(center=(self.x + self.width//2, self.y - 20))
            surface.blit(combo_text, combo_rect)

class Platform:
    def __init__(self, x, y, width, height, is_wall=False):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.is_wall = is_wall
        self.color = GREEN  # Always green, no more red walls
        self.particles = []

    def update(self):
        self.x -= SCROLL_SPEED
        # Update particles
        self.particles = [p for p in self.particles if p[2] > 0]
        self.particles = [(x, y, life - 1) for x, y, life in self.particles]

    def draw(self, surface):
        # Draw platform with gradient
        platform_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        for i in range(self.height):
            alpha = int(255 * (1 - i / self.height))
            color = (*self.color[:3], alpha)
            pygame.draw.line(platform_surface, color, (0, i), (self.width, i))
        
        # Add highlight
        highlight = pygame.Surface((self.width, self.height//3), pygame.SRCALPHA)
        highlight.fill((255, 255, 255, 50))
        platform_surface.blit(highlight, (0, 0))

        surface.blit(platform_surface, (self.x, self.y))

        # Draw particles
        for x, y, life in self.particles:
            alpha = int(255 * (life / 10))
            particle_color = (*self.color[:3], alpha)
            pygame.draw.circle(surface, particle_color, (int(x), int(y)), 2)

class Spike:
    def __init__(self, x, y, width=20, height=20):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = YELLOW
        self.glow_radius = 0
        self.glow_direction = 1

    def update(self):
        self.x -= SCROLL_SPEED
        # Update glow effect
        self.glow_radius += 0.2 * self.glow_direction
        if self.glow_radius > 5 or self.glow_radius < 0:
            self.glow_direction *= -1

    def draw(self, surface):
        # Draw glow
        glow_surface = pygame.Surface((self.width + self.glow_radius*2, self.height + self.glow_radius*2), pygame.SRCALPHA)
        pygame.draw.polygon(glow_surface, (*self.color[:3], 100), [
            (self.width/2 + self.glow_radius, self.glow_radius),
            (self.glow_radius, self.height + self.glow_radius),
            (self.width + self.glow_radius, self.height + self.glow_radius)
        ])
        surface.blit(glow_surface, (self.x - self.glow_radius, self.y - self.glow_radius))

        # Draw spike
        points = [
            (self.x + self.width/2, self.y),
            (self.x, self.y + self.height),
            (self.x + self.width, self.y + self.height)
        ]
        pygame.draw.polygon(surface, self.color, points)

class Meteorite:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.size = random.randint(5, 10)  # Increased size
        self.speed = random.uniform(3, 7)  # Increased speed
        self.angle = random.uniform(-30, 30)  # Angle in degrees
        self.trail_length = random.randint(15, 25)  # Longer trail
        self.trail = []
        self.core_color = (255, 100, 0)  # Orange core
        self.outer_color = (255, 200, 0)  # Yellow outer glow
        self.life = 150  # Increased lifetime
        self.pulse_size = 0
        self.pulse_direction = 1

    def update(self):
        # Update position based on angle
        self.x += self.speed * math.cos(math.radians(self.angle))
        self.y += self.speed * math.sin(math.radians(self.angle))
        
        # Update trail
        self.trail.append((self.x, self.y))
        if len(self.trail) > self.trail_length:
            self.trail.pop(0)
        
        # Update pulse effect
        self.pulse_size += 0.1 * self.pulse_direction
        if self.pulse_size > 2 or self.pulse_size < 0:
            self.pulse_direction *= -1
        
        self.life -= 1

    def draw(self, surface):
        # Draw trail with enhanced fiery effect
        for i, (trail_x, trail_y) in enumerate(self.trail):
            alpha = int(255 * (i / len(self.trail)))
            # Create gradient from yellow to orange
            trail_color = (
                int(self.outer_color[0] * (i / len(self.trail)) + self.core_color[0] * (1 - i / len(self.trail))),
                int(self.outer_color[1] * (i / len(self.trail)) + self.core_color[1] * (1 - i / len(self.trail))),
                int(self.outer_color[2] * (i / len(self.trail)) + self.core_color[2] * (1 - i / len(self.trail))),
                alpha
            )
            trail_size = int(self.size * (i / len(self.trail)))
            
            # Draw trail glow with multiple layers
            for glow_size in range(3, 0, -1):
                glow_surface = pygame.Surface((trail_size * (glow_size + 1) * 2, trail_size * (glow_size + 1) * 2), pygame.SRCALPHA)
                glow_alpha = int(alpha * (0.3 / glow_size))
                glow_color = (*trail_color[:3], glow_alpha)
                pygame.draw.circle(glow_surface, glow_color, 
                                 (trail_size * (glow_size + 1), trail_size * (glow_size + 1)), 
                                 trail_size * (glow_size + 1))
                surface.blit(glow_surface, (int(trail_x) - trail_size * (glow_size + 1), 
                                          int(trail_y) - trail_size * (glow_size + 1)))
            
            # Draw trail
            pygame.draw.circle(surface, trail_color, (int(trail_x), int(trail_y)), trail_size)
        
        # Draw meteorite with enhanced fiery effect
        # Outer glow
        for glow_size in range(4, 0, -1):
            glow_surface = pygame.Surface((self.size * (glow_size + 1) * 2, self.size * (glow_size + 1) * 2), pygame.SRCALPHA)
            glow_alpha = int(150 * (0.3 / glow_size))
            glow_color = (*self.outer_color, glow_alpha)
            pygame.draw.circle(glow_surface, glow_color, 
                             (self.size * (glow_size + 1), self.size * (glow_size + 1)), 
                             self.size * (glow_size + 1))
            surface.blit(glow_surface, (int(self.x) - self.size * (glow_size + 1), 
                                      int(self.y) - self.size * (glow_size + 1)))
        
        # Core with pulse effect
        core_size = self.size + self.pulse_size
        pygame.draw.circle(surface, self.core_color, (int(self.x), int(self.y)), int(core_size))
        
        # Add sparkle effect occasionally
        if random.random() < 0.1:
            sparkle_size = random.randint(2, 4)
            sparkle_surface = pygame.Surface((sparkle_size * 4, sparkle_size * 4), pygame.SRCALPHA)
            pygame.draw.circle(sparkle_surface, (255, 255, 255, 200), 
                             (sparkle_size * 2, sparkle_size * 2), sparkle_size)
            surface.blit(sparkle_surface, (int(self.x) - sparkle_size * 2, int(self.y) - sparkle_size * 2))

class ShootingStar:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.speed = random.uniform(8, 12)  # Faster than meteorites
        self.angle = random.uniform(30, 60)  # Changed to positive angles for downward movement
        self.trail_length = random.randint(20, 30)  # Longer trail
        self.trail = []
        self.color = (255, 255, 255)  # White color
        self.life = 100  # Frames until removal
        self.size = random.randint(2, 4)  # Smaller than meteorites

    def update(self):
        # Update position based on angle
        self.x += self.speed * math.cos(math.radians(self.angle))
        self.y += self.speed * math.sin(math.radians(self.angle))
        
        # Update trail
        self.trail.append((self.x, self.y))
        if len(self.trail) > self.trail_length:
            self.trail.pop(0)
        
        self.life -= 1

    def draw(self, surface):
        # Draw trail with enhanced glow
        for i, (trail_x, trail_y) in enumerate(self.trail):
            alpha = int(255 * (i / len(self.trail)))
            trail_color = (*self.color, alpha)
            trail_size = int(self.size * (i / len(self.trail)))
            
            # Draw trail glow
            glow_surface = pygame.Surface((trail_size * 4, trail_size * 4), pygame.SRCALPHA)
            pygame.draw.circle(glow_surface, (*self.color, alpha//2), 
                             (trail_size * 2, trail_size * 2), trail_size * 2)
            surface.blit(glow_surface, (int(trail_x) - trail_size * 2, int(trail_y) - trail_size * 2))
            
            # Draw trail
            pygame.draw.circle(surface, trail_color, (int(trail_x), int(trail_y)), trail_size)
        
        # Draw star with enhanced glow
        glow_surface = pygame.Surface((self.size * 6, self.size * 6), pygame.SRCALPHA)
        pygame.draw.circle(glow_surface, (*self.color, 150), 
                         (self.size * 3, self.size * 3), self.size * 3)
        surface.blit(glow_surface, (int(self.x) - self.size * 3, int(self.y) - self.size * 3))
        
        # Draw star
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.size)

class Spaceship:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 60
        self.height = 30
        self.color = (100, 200, 255)
        self.engine_color = (255, 200, 100)
        self.engine_particles = []
        self.max_engine_particles = 20
        self.is_active = False
        self.travel_distance = 500  # Distance to skip
        self.travel_speed = 10
        self.travel_progress = 0
        self.glow_radius = 0
        self.glow_direction = 1
        self.pulse_size = 0
        self.pulse_direction = 1
        self.player_aboard = False
        self.boarding_timer = 0
        self.max_boarding_time = 180  # 3 seconds at 60 FPS
        self.boarding_particles = []

    def update(self):
        # Update glow effect
        self.glow_radius += 0.2 * self.glow_direction
        if self.glow_radius > 5 or self.glow_radius < 0:
            self.glow_direction *= -1

        # Update pulse effect
        self.pulse_size += 0.1 * self.pulse_direction
        if self.pulse_size > 2 or self.pulse_size < 0:
            self.pulse_direction *= -1

        # Update engine particles
        if self.is_active or self.player_aboard:
            # Create new engine particles
            if random.random() < 0.3:
                self.engine_particles.append((
                    self.x - 10,
                    self.y + random.randint(0, self.height),
                    random.randint(10, 20)
                ))
            # Move forward
            self.x += self.travel_speed
            self.travel_progress += self.travel_speed

        # Update boarding particles
        if self.player_aboard:
            self.boarding_timer += 1
            if random.random() < 0.2:
                self.boarding_particles.append((
                    self.x + random.randint(0, self.width),
                    self.y + random.randint(0, self.height),
                    random.randint(10, 20)
                ))

        # Update existing particles
        self.engine_particles = [(x - 5, y, life - 1) for x, y, life in self.engine_particles if life > 0]
        self.boarding_particles = [(x, y, life - 1) for x, y, life in self.boarding_particles if life > 0]

    def draw(self, surface):
        # Draw engine particles
        for x, y, life in self.engine_particles:
            alpha = int(255 * (life / 20))
            particle_color = (*self.engine_color[:3], alpha)
            particle_surface = pygame.Surface((8, 8), pygame.SRCALPHA)
            pygame.draw.circle(particle_surface, particle_color, (4, 4), 4)
            surface.blit(particle_surface, (int(x), int(y)))

        # Draw boarding particles
        for x, y, life in self.boarding_particles:
            alpha = int(255 * (life / 20))
            particle_color = (255, 255, 255, alpha)
            particle_surface = pygame.Surface((6, 6), pygame.SRCALPHA)
            pygame.draw.circle(particle_surface, particle_color, (3, 3), 3)
            surface.blit(particle_surface, (int(x), int(y)))

        # Draw glow
        glow_surface = pygame.Surface((self.width + 20, self.height + 20), pygame.SRCALPHA)
        glow_color = (*self.color[:3], 100)
        pygame.draw.rect(glow_surface, glow_color, (10, 10, self.width, self.height), border_radius=10)
        surface.blit(glow_surface, (self.x - 10, self.y - 10))

        # Draw main body
        ship_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        pygame.draw.rect(ship_surface, self.color, (0, 0, self.width, self.height), border_radius=5)
        
        # Add cockpit
        pygame.draw.ellipse(ship_surface, (200, 230, 255), (self.width//4, 5, self.width//2, self.height - 10))
        
        # Add wings
        wing_color = (*self.color[:3], 200)
        pygame.draw.polygon(ship_surface, wing_color, [
            (0, self.height//2),
            (self.width//4, self.height//2),
            (self.width//4, self.height)
        ])
        pygame.draw.polygon(ship_surface, wing_color, [
            (self.width, self.height//2),
            (3*self.width//4, self.height//2),
            (3*self.width//4, self.height)
        ])

        # Add pulse effect
        if not self.is_active and not self.player_aboard:
            pulse_surface = pygame.Surface((self.width + self.pulse_size*2, self.height + self.pulse_size*2), pygame.SRCALPHA)
            pygame.draw.rect(pulse_surface, (*self.color[:3], 50), 
                           (self.pulse_size, self.pulse_size, self.width, self.height), border_radius=5)
            surface.blit(pulse_surface, (self.x - self.pulse_size, self.y - self.pulse_size))

        surface.blit(ship_surface, (self.x, self.y))

        # Draw boarding progress if player is aboard
        if self.player_aboard:
            progress = self.boarding_timer / self.max_boarding_time
            bar_width = 40
            bar_height = 5
            bar_x = self.x + (self.width - bar_width) // 2
            bar_y = self.y - 10
            
            # Draw background
            pygame.draw.rect(surface, (50, 50, 50), (bar_x, bar_y, bar_width, bar_height))
            # Draw progress
            pygame.draw.rect(surface, CYAN, (bar_x, bar_y, int(bar_width * progress), bar_height))

class Game:
    def __init__(self):
        self.player = Player()
        self.platforms = []
        self.spikes = []
        self.monsters = []
        self.powerups = []
        self.score = 0
        self.game_over = False
        self.background = pygame.Surface((WIDTH, HEIGHT))
        self.generate_background()
        self.generate_initial_platforms()
        self.particles = []
        self.max_particles = 100
        self.meteorites = []
        self.last_meteorite_time = 0
        self.meteorite_delay = 1000
        self.shooting_stars = []  # Add shooting stars list
        self.last_shooting_star_time = 0
        self.shooting_star_delay = 2000  # Reduced from 3000 to 2000 (2 seconds between shooting stars)
        self.screen_shake = 0
        self.high_score = 0
        self.is_paused = False
        self.tutorial_step = 0
        self.tutorial_timer = 0
        self.tutorial_messages = [
            "Use LEFT and RIGHT to move",
            "Press SPACE to jump",
            "Press SHIFT to dash",
            "Collect powerups for higher jumps",
            "Avoid spikes and monsters",
            "Chain jumps for combos!"
        ]
        self.particle_system = []
        self.max_particles = 200
        self.background_particles = []
        self.max_background_particles = 100
        self.spaceships = []
        self.spaceship_delay = 10000  # 10 seconds between spaceships
        self.last_spaceship_time = 0

    def generate_background(self):
        # Create gradient background
        for y in range(HEIGHT):
            # Create a more interesting gradient
            r = int(10 + (y / HEIGHT) * 20)  # Dark blue to slightly lighter
            g = int(20 + (y / HEIGHT) * 30)
            b = int(40 + (y / HEIGHT) * 60)
            pygame.draw.line(self.background, (r, g, b), (0, y), (WIDTH, y))

        # Add more stars with varying brightness
        for _ in range(200):  # More stars
            x = random.randint(0, WIDTH)
            y = random.randint(0, HEIGHT)
            size = random.randint(1, 3)
            brightness = random.randint(50, 255)
            pygame.draw.circle(self.background, (brightness, brightness, brightness), (x, y), size)
            
            # Add some twinkling stars
            if random.random() < 0.3:
                glow_size = size + 2
                pygame.draw.circle(self.background, (brightness, brightness, brightness, 100), (x, y), glow_size)

    def generate_initial_platforms(self):
        # Start with a ground platform
        self.platforms.append(Platform(0, HEIGHT - 50, WIDTH, 50))
        
        # Create a series of platforms at different elevations
        current_height = HEIGHT - 150  # Start at a reasonable height
        for i in range(5):
            x = 200 + i * 200
            # Gradually increase height with smaller steps
            if i > 0:
                height_change = random.choice([-50, 0, 50])  # Smaller height changes
                current_height = max(HEIGHT - 350, min(HEIGHT - 100, current_height + height_change))
            
            width = 150
            self.platforms.append(Platform(x, current_height, width, 30))
            
            # Add some spikes occasionally, but not in the first few platforms
            if i >= 2 and i % 3 == 0:  # Only add spikes after the first 2 platforms
                spike_x = x + width//2 - 10
                self.spikes.append(Spike(spike_x, current_height - 20))

            # Add monsters only after the first few platforms
            if i >= 3 and i % 4 == 0:  # Only add monsters after platform 3
                monster_x = x + width + 50
                self.monsters.append(Monster(monster_x, current_height - 50))

    def generate_new_platform(self):
        # Generate new platforms with more predictable patterns
        last_platform = self.platforms[-1]
        if last_platform.x < WIDTH + 200:
            # Create a new platform
            x = last_platform.x + random.randint(150, 200)
            
            # Calculate new height based on last platform with smaller changes
            height_change = random.choice([-50, 0, 50])  # Smaller height changes
            current_height = max(HEIGHT - 350, min(HEIGHT - 100, last_platform.y + height_change))
            
            width = random.randint(120, 180)
            
            # Add the platform
            self.platforms.append(Platform(x, current_height, width, 30))
            
            # Add monsters first (if any)
            monster_x = None
            if self.score > 300 and random.random() < 0.25:  # Increased monster frequency to 25% and lowered score threshold
                monster_x = x + width + 50
                self.monsters.append(Monster(monster_x, current_height - 50))
            
            # Add powerups (15% chance) but not near monsters
            if random.random() < 0.15 and (monster_x is None or x + width//2 < monster_x - 100):
                powerup_x = x + width//2 - 10  # Center on platform
                self.powerups.append(Powerup(powerup_x, current_height - 40))  # Place above platform
            
            # Sometimes add spikes (less frequently)
            if random.random() < 0.15:  # Reduced spike frequency
                spike_x = x + random.randint(20, width - 40)
                self.spikes.append(Spike(spike_x, current_height - 20))

            # Add spaceship occasionally
            current_time = pygame.time.get_ticks()
            if current_time - self.last_spaceship_time > self.spaceship_delay:
                if random.random() < 0.3:  # 30% chance to spawn a spaceship
                    spaceship_x = x + width + 100
                    self.spaceships.append(Spaceship(spaceship_x, current_height - 50))
                    self.last_spaceship_time = current_time

    def update(self):
        if self.is_paused:
            return

        # Update screen shake
        if self.screen_shake > 0:
            self.screen_shake -= 1

        if not self.game_over and self.player.is_alive:
            # Update all game objects
            for platform in self.platforms:
                platform.update()
            for spike in self.spikes:
                spike.update()
            for monster in self.monsters:
                monster.update(self.player.x + self.player.width/2, self.player.y + self.player.height/2)
            for powerup in self.powerups:
                powerup.update()

            # Update background particles
            self.particles = [(x - 1, y, life - 1) for x, y, life in self.particles if life > 0]
            
            # Add new particles occasionally
            if random.random() < 0.1 and len(self.particles) < self.max_particles:
                self.particles.append((
                    WIDTH,
                    random.randint(0, HEIGHT),
                    random.randint(30, 60)
                ))

            # Update meteorites
            current_time = pygame.time.get_ticks()
            if current_time - self.last_meteorite_time > self.meteorite_delay:
                # Create new meteorite with wider spawn area
                start_x = random.randint(WIDTH, WIDTH + 200)  # Increased spawn area
                start_y = random.randint(-50, HEIGHT//2)  # Allow spawning above screen
                self.meteorites.append(Meteorite(start_x, start_y))
                self.last_meteorite_time = current_time
            
            # Update existing meteorites
            for meteorite in self.meteorites:
                meteorite.update()
            
            # Remove meteorites that are off screen or expired
            self.meteorites = [m for m in self.meteorites if m.x > -100 and m.y < HEIGHT + 100 and m.life > 0]

            # Update shooting stars
            if current_time - self.last_shooting_star_time > self.shooting_star_delay:
                # Create new shooting star from top of screen
                start_x = random.randint(0, WIDTH)
                start_y = -50  # Start above screen
                self.shooting_stars.append(ShootingStar(start_x, start_y))
                self.last_shooting_star_time = current_time
            
            # Update existing shooting stars
            for star in self.shooting_stars:
                star.update()
            
            # Remove shooting stars that are off screen or expired
            self.shooting_stars = [s for s in self.shooting_stars if s.y < HEIGHT + 50 and s.x < WIDTH + 50 and s.life > 0]

            # Remove objects that are off screen
            self.platforms = [p for p in self.platforms if p.x + p.width > 0]
            self.spikes = [s for s in self.spikes if s.x + s.width > 0]
            self.monsters = [m for m in self.monsters if m.x + m.width > 0]
            self.powerups = [p for p in self.powerups if not p.collected and p.x + p.width > 0]

            self.player.update(self.platforms, self.spikes, self.monsters, self.powerups)
            self.generate_new_platform()
            
            # Update score
            self.score += 1

            # Update tutorial timer
            if self.tutorial_step < len(self.tutorial_messages):
                self.tutorial_timer += 1
                if self.tutorial_timer >= 300:  # 5 seconds at 60 FPS
                    self.tutorial_step += 1
                    self.tutorial_timer = 0

            # Update particle system
            self.particle_system = [(x, y, size, life - 1, color) for x, y, size, life, color in self.particle_system if life > 0]
            
            # Add new background particles
            if len(self.background_particles) < self.max_background_particles:
                self.background_particles.append((
                    random.randint(0, WIDTH),
                    random.randint(0, HEIGHT),
                    random.randint(1, 3),
                    random.randint(30, 60),
                    (random.randint(100, 255), random.randint(100, 255), random.randint(100, 255))
                ))

            # Update background particles
            self.background_particles = [(x, y, size, life - 1, color) for x, y, size, life, color in self.background_particles if life > 0]

            # Update spaceships
            for spaceship in self.spaceships:
                spaceship.update()
                if spaceship.is_active and spaceship.travel_progress >= spaceship.travel_distance:
                    self.spaceships.remove(spaceship)
                elif spaceship.x + spaceship.width < 0:
                    self.spaceships.remove(spaceship)

    def draw(self, surface):
        # Apply screen shake
        shake_offset = (random.randint(-self.screen_shake, self.screen_shake),
                       random.randint(-self.screen_shake, self.screen_shake)) if self.screen_shake > 0 else (0, 0)
        
        # Create a temporary surface for all game elements
        game_surface = pygame.Surface((WIDTH, HEIGHT))
        game_surface.blit(self.background, (0, 0))
        
        # Draw all game elements on the temporary surface
        # Draw background particles
        for x, y, life in self.particles:
            alpha = int(255 * (life / 60))
            particle_color = (255, 255, 255, alpha)
            particle_surface = pygame.Surface((3, 3), pygame.SRCALPHA)
            pygame.draw.circle(particle_surface, particle_color, (1, 1), 1)
            game_surface.blit(particle_surface, (int(x) - shake_offset[0], int(y) - shake_offset[1]))
        
        # Draw shooting stars
        for star in self.shooting_stars:
            star.draw(game_surface)
        
        # Draw meteorites
        for meteorite in self.meteorites:
            meteorite.draw(game_surface)
        
        # Draw platforms
        for platform in self.platforms:
            platform.draw(game_surface)
        
        # Draw spikes
        for spike in self.spikes:
            spike.draw(game_surface)
        
        # Draw monsters
        for monster in self.monsters:
            monster.draw(game_surface)

        # Draw powerups
        for powerup in self.powerups:
            powerup.draw(game_surface)
        
        # Draw player
        self.player.draw(game_surface)
        
        # Draw score with enhanced glow effect
        font = pygame.font.Font(None, 36)
        score_text = font.render(f"Score: {self.score}", True, WHITE)
        score_rect = score_text.get_rect(topleft=(10, 10))
        
        # Add multiple layers of glow
        for i in range(3, 0, -1):
            glow_surface = pygame.Surface((score_rect.width + i*4, score_rect.height + i*4), pygame.SRCALPHA)
            glow_surface.blit(score_text, (i*2, i*2))
            game_surface.blit(glow_surface, (10 - i*2, 10 - i*2))
        game_surface.blit(score_text, (10, 10))

        # Draw powerup timer if active
        if self.player.has_jump_powerup:
            powerup_time = self.player.powerup_timer // 60  # Convert frames to seconds
            powerup_text = font.render(f"Jump Boost: {powerup_time}s", True, CYAN)
            powerup_rect = powerup_text.get_rect(topleft=(10, 50))
            
            # Add glow to powerup timer
            for i in range(3, 0, -1):
                glow_surface = pygame.Surface((powerup_rect.width + i*4, powerup_rect.height + i*4), pygame.SRCALPHA)
                glow_surface.blit(powerup_text, (i*2, i*2))
                game_surface.blit(glow_surface, (10 - i*2, 50 - i*2))
            game_surface.blit(powerup_text, (10, 50))

        # Draw game over message with enhanced animation
        if not self.player.is_alive:
            game_over_font = pygame.font.Font(None, 72)
            game_over_text = game_over_font.render("GAME OVER", True, RED)
            game_over_rect = game_over_text.get_rect(center=(WIDTH//2, HEIGHT//2 - 36))
            
            # Add multiple layers of glow to game over text
            for i in range(5, 0, -1):
                glow_surface = pygame.Surface((game_over_rect.width + i*4, game_over_rect.height + i*4), pygame.SRCALPHA)
                glow_surface.blit(game_over_text, (i*2, i*2))
                game_surface.blit(glow_surface, (game_over_rect.x - i*2, game_over_rect.y - i*2))
            game_surface.blit(game_over_text, game_over_rect)

            restart_font = pygame.font.Font(None, 36)
            restart_text = restart_font.render("Press R to restart", True, WHITE)
            restart_rect = restart_text.get_rect(center=(WIDTH//2, HEIGHT//2 + 36))
            game_surface.blit(restart_text, restart_rect)

        # Draw tutorial message with fade out
        if self.tutorial_step < len(self.tutorial_messages):
            # Calculate alpha based on time remaining
            alpha = min(255, max(0, 255 - (self.tutorial_timer - 240) * 2))  # Fade out in last second
            font = pygame.font.Font(None, 36)
            tutorial_text = font.render(self.tutorial_messages[self.tutorial_step], True, WHITE)
            tutorial_rect = tutorial_text.get_rect(center=(WIDTH//2, HEIGHT - 50))
            
            # Create a surface with alpha
            tutorial_surface = pygame.Surface((tutorial_rect.width, tutorial_rect.height), pygame.SRCALPHA)
            tutorial_surface.blit(tutorial_text, (0, 0))
            tutorial_surface.set_alpha(alpha)
            
            game_surface.blit(tutorial_surface, tutorial_rect)

        # Draw pause menu
        if self.is_paused:
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 128))
            game_surface.blit(overlay, (0, 0))
            
            font = pygame.font.Font(None, 72)
            pause_text = font.render("PAUSED", True, WHITE)
            pause_rect = pause_text.get_rect(center=(WIDTH//2, HEIGHT//2 - 50))
            game_surface.blit(pause_text, pause_rect)
            
            font = pygame.font.Font(None, 36)
            resume_text = font.render("Press P to resume", True, WHITE)
            resume_rect = resume_text.get_rect(center=(WIDTH//2, HEIGHT//2 + 50))
            game_surface.blit(resume_text, resume_rect)

        # Draw particle system
        for x, y, size, life, color in self.particle_system:
            alpha = int(255 * (life / 30))
            particle_color = (*color, alpha)
            particle_surface = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
            pygame.draw.circle(particle_surface, particle_color, (size, size), size)
            game_surface.blit(particle_surface, (int(x), int(y)))

        # Draw background particles
        for x, y, size, life, color in self.background_particles:
            alpha = int(255 * (life / 60))
            particle_color = (*color, alpha)
            particle_surface = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
            pygame.draw.circle(particle_surface, particle_color, (size, size), size)
            game_surface.blit(particle_surface, (int(x), int(y)))

        # Draw spaceships
        for spaceship in self.spaceships:
            spaceship.draw(game_surface)

        # Blit the game surface to the main surface with shake offset
        surface.blit(game_surface, shake_offset)

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_p:
                self.is_paused = not self.is_paused
            elif event.key == pygame.K_LSHIFT and not self.is_paused:
                self.player.dash()
                # Add screen shake for dash
                self.screen_shake = 5
            elif event.key == pygame.K_SPACE and not self.is_paused:
                # Check for spaceship interaction
                for spaceship in self.spaceships:
                    if (not spaceship.is_active and 
                        self.player.x < spaceship.x + spaceship.width and
                        self.player.x + self.player.width > spaceship.x and
                        self.player.y < spaceship.y + spaceship.height and
                        self.player.y + self.player.height > spaceship.y):
                        spaceship.is_active = True
                        self.player.x = spaceship.x + spaceship.width//2
                        self.player.y = spaceship.y + spaceship.height//2
                        self.player.vel_y = 0
                        self.player.is_jumping = False
                        self.player.can_double_jump = True
                        break
                else:
                    self.player.jump()
            elif event.key == pygame.K_r and not self.player.is_alive:
                self.restart()

    def restart(self):
        self.player = Player()
        self.platforms = []
        self.spikes = []
        self.monsters = []
        self.powerups = []  # Reset powerups
        self.score = 0
        self.game_over = False
        self.generate_initial_platforms()
        self.spaceships = []
        self.last_spaceship_time = 0

def main():
    game = Game()
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            game.handle_event(event)

        if not game.is_paused:
            # Get keyboard input
            keys = pygame.key.get_pressed()
            if game.player.is_alive:
                if keys[pygame.K_LEFT]:
                    game.player.move_left()
                elif keys[pygame.K_RIGHT]:
                    game.player.move_right()
                else:
                    game.player.stop_moving()

        # Update and draw
        game.update()
        screen.fill(BLACK)
        game.draw(screen)
        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()

if __name__ == "__main__":
    main() 