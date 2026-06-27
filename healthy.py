import pygame
import random
import math
import json
from datetime import datetime
import os
import sys

# Initialize pygame
pygame.init()
pygame.mixer.init()

# Screen dimensions
WIDTH, HEIGHT = 1000, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Healthy Snake Adventure")
clock = pygame.time.Clock()

# Colors
BACKGROUND = (20, 30, 40)
GRID_COLOR = (40, 50, 60)
SNAKE_HEAD = (86, 214, 110)
SNAKE_BODY = (66, 184, 90)
TEXT_COLOR = (240, 240, 240)
HEALTH_BAR_GOOD = (76, 175, 80)
HEALTH_BAR_BAD = (244, 67, 54)

# Game constants
CELL_SIZE = 40
GRID_WIDTH = WIDTH // CELL_SIZE
GRID_HEIGHT = HEIGHT // CELL_SIZE
GAME_SPEED = 8
MAX_FOODS = 8
FOOD_SPAWN_RATE = 0.3

# Load fonts
try:
    title_font = pygame.font.Font(None, 72)
    large_font = pygame.font.Font(None, 48)
    medium_font = pygame.font.Font(None, 32)
    small_font = pygame.font.Font(None, 24)
except:
    title_font = pygame.font.SysFont('arial', 72)
    large_font = pygame.font.SysFont('arial', 48)
    medium_font = pygame.font.SysFont('arial', 32)
    small_font = pygame.font.SysFont('arial', 24)

# Food types with points and health impact
FOOD_DATA = {
    # Healthy foods (positive health impact)
    "apple": {"points": 10, "health": 2, "color": (237, 67, 55), "rarity": 1},
    "carrot": {"points": 8, "health": 1, "color": (255, 152, 0), "rarity": 1},
    "broccoli": {"points": 12, "health": 3, "color": (76, 175, 80), "rarity": 1},
    "blueberry": {"points": 15, "health": 2, "color": (63, 81, 181), "rarity": 2},
    "avocado": {"points": 20, "health": 4, "color": (104, 159, 56), "rarity": 2},
    "orange": {"points": 12, "health": 2, "color": (255, 152, 0), "rarity": 1},
    "tomato": {"points": 9, "health": 1, "color": (244, 67, 54), "rarity": 1},
    "spinach": {"points": 14, "health": 3, "color": (56, 142, 60), "rarity": 2},
    
    # Unhealthy foods (negative health impact)
    "burger": {"points": 5, "health": -3, "color": (141, 110, 99), "rarity": 1},
    "soda": {"points": 3, "health": -4, "color": (233, 30, 99), "rarity": 1},
    "donut": {"points": 6, "health": -2, "color": (255, 193, 7), "rarity": 1},
    "pizza": {"points": 7, "health": -3, "color": (255, 87, 34), "rarity": 2},
    "icecream": {"points": 8, "health": -2, "color": (224, 247, 250), "rarity": 2},
    "fries": {"points": 4, "health": -2, "color": (237, 187, 81), "rarity": 1},
    "cake": {"points": 9, "health": -4, "color": (255, 138, 191), "rarity": 2},
    "candy": {"points": 2, "health": -1, "color": (255, 82, 82), "rarity": 1},
}

# Power-ups
POWER_UPS = {
    "speed_boost": {"duration": 5, "color": (33, 150, 243), "effect": "speed"},
    "health_boost": {"duration": 0, "color": (0, 200, 83), "effect": "health"},
    "double_points": {"duration": 8, "color": (255, 193, 7), "effect": "points"},
    "magnet": {"duration": 6, "color": (156, 39, 176), "effect": "magnet"},
}

# Image paths for each food type
FOOD_IMAGE_PATHS = {
    "apple": "images/apple.png",
    "carrot": "images/carrot.png", 
    "broccoli": "images/broccoli.png",
    "blueberry": "images/blueberry.png",
    "avocado": "images/avocado.png",
    "orange": "images/orange.png",
    "tomato": "images/tomato.png",
    "spinach": "images/spinach.png",
    "burger": "images/burger.png",
    "soda": "images/soda.png",
    "donut": "images/donut.png",
    "pizza": "images/pizza.png",
    "icecream": "images/icecream.png",
    "fries": "images/fries.png",
    "cake": "images/cake.png",
    "candy": "images/candy.png"
}

# Load food images
def load_food_images():
    food_images = {}
    
    # Create a simple function to generate placeholder images if real images aren't available
    def create_placeholder_image(color, name):
        surf = pygame.Surface((CELL_SIZE-5, CELL_SIZE-5), pygame.SRCALPHA)
        
        # Draw different shapes based on food type for variety
        if name in ["apple", "orange", "tomato", "blueberry"]:
            pygame.draw.circle(surf, color, (CELL_SIZE//2-2, CELL_SIZE//2-2), CELL_SIZE//2-5)
        elif name in ["carrot", "broccoli"]:
            points = [
                (5, CELL_SIZE-10),
                (CELL_SIZE//2-2, 5),
                (CELL_SIZE-10, CELL_SIZE-10)
            ]
            pygame.draw.polygon(surf, color, points)
        else:
            pygame.draw.rect(surf, color, (5, 5, CELL_SIZE-10, CELL_SIZE-10), border_radius=8)
        
        # Add text for food type
        text = small_font.render(name[0].upper(), True, (255, 255, 255))
        text_rect = text.get_rect(center=(CELL_SIZE//2-2, CELL_SIZE//2-2))
        surf.blit(text, text_rect)
        
        return surf
    
    # Check if images directory exists and load images
    if os.path.exists("images"):
        for food_type, path in FOOD_IMAGE_PATHS.items():
            try:
                if os.path.exists(path):
                    img = pygame.image.load(path)
                    food_images[food_type] = pygame.transform.scale(img, (CELL_SIZE-5, CELL_SIZE-5))
                    print(f"Loaded image for {food_type}")
                else:
                    # Create placeholder if image doesn't exist
                    food_images[food_type] = create_placeholder_image(FOOD_DATA[food_type]["color"], food_type)
                    print(f"Created placeholder for {food_type} (image not found: {path})")
            except Exception as e:
                print(f"Error loading image for {food_type}: {e}")
                food_images[food_type] = create_placeholder_image(FOOD_DATA[food_type]["color"], food_type)
    else:
        # Create all placeholders if images directory doesn't exist
        print("Images directory not found. Creating placeholder images...")
        for food_type in FOOD_DATA.keys():
            food_images[food_type] = create_placeholder_image(FOOD_DATA[food_type]["color"], food_type)
    
    return food_images

# Particle system for visual effects
class Particle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        self.size = random.randint(2, 6)
        self.speed_x = random.uniform(-2, 2)
        self.speed_y = random.uniform(-2, 2)
        self.life = random.randint(20, 40)
    
    def update(self):
        self.x += self.speed_x
        self.y += self.speed_y
        self.life -= 1
        self.size = max(0, self.size - 0.1)
        return self.life > 0
    
    def draw(self, surface):
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), int(self.size))

class ParticleSystem:
    def __init__(self):
        self.particles = []
    
    def add_particles(self, x, y, color, count=10):
        for _ in range(count):
            self.particles.append(Particle(x, y, color))
    
    def update(self):
        self.particles = [p for p in self.particles if p.update()]
    
    def draw(self, surface):
        for particle in self.particles:
            particle.draw(surface)

# Food Manager to handle multiple foods
class FoodManager:
    def __init__(self, food_images):
        self.food_images = food_images
        self.foods = []
        
    def update(self, snake_positions):
        # Update all foods
        for food in self.foods:
            food.update()
        
        # Try to spawn new food
        if len(self.foods) < MAX_FOODS and random.random() < FOOD_SPAWN_RATE:
            self.spawn_food(snake_positions)
    
    def spawn_food(self, snake_positions):
        # Try to find a valid position
        for _ in range(20):  # Try up to 20 times
            position = (random.randint(1, GRID_WIDTH - 2), 
                       random.randint(1, GRID_HEIGHT - 2))
            
            # Check if position is not on snake and not on existing food
            if (position not in snake_positions and 
                not any(food.position == position for food in self.foods)):
                
                # Weighted random selection based on rarity
                choices = []
                weights = []
                for food_type, data in FOOD_DATA.items():
                    choices.append(food_type)
                    weights.append(data["rarity"])
                
                food_type = random.choices(choices, weights=weights)[0]
                new_food = Food(position, food_type, self.food_images)
                self.foods.append(new_food)
                break
    
    def remove_food(self, position):
        self.foods = [food for food in self.foods if food.position != position]
    
    def draw(self, surface):
        for food in self.foods:
            food.draw(surface)
    
    def get_food_at_position(self, position):
        for food in self.foods:
            if food.position == position:
                return food
        return None

# Animated food item with images
class Food:
    def __init__(self, position, food_type, food_images):
        self.position = position
        self.type = food_type
        self.animation_offset = random.uniform(0, 5)
        self.pulse_direction = 1
        self.rotation = random.uniform(0, 360)
        self.rotation_speed = random.uniform(-2, 2)
        self.food_images = food_images
        self.spawn_particles()
    
    def spawn_particles(self):
        self.particles = ParticleSystem()
        x = self.position[0] * CELL_SIZE + CELL_SIZE // 2
        y = self.position[1] * CELL_SIZE + CELL_SIZE // 2
        color = FOOD_DATA[self.type]["color"]
        self.particles.add_particles(x, y, color, 3)
    
    def update(self):
        # Floating animation
        self.animation_offset += 0.05 * self.pulse_direction
        if abs(self.animation_offset) > 2:
            self.pulse_direction *= -1
        
        # Rotation animation
        self.rotation += self.rotation_speed
        if self.rotation >= 360:
            self.rotation = 0
        
        self.particles.update()
        return True
    
    def draw(self, surface):
        x, y = self.position
        center_x = x * CELL_SIZE + CELL_SIZE // 2
        center_y = y * CELL_SIZE + CELL_SIZE // 2
        
        # Calculate floating effect
        float_offset = self.animation_offset
        
        # Rotate and draw food image with floating effect
        original_image = self.food_images[self.type]
        rotated_image = pygame.transform.rotate(original_image, self.rotation)
        rotated_rect = rotated_image.get_rect(center=(center_x, center_y + float_offset))
        surface.blit(rotated_image, rotated_rect)
        
        # Draw glow effect for rare foods
        if FOOD_DATA[self.type]["rarity"] > 1:
            glow_surf = pygame.Surface((CELL_SIZE+10, CELL_SIZE+10), pygame.SRCALPHA)
            pygame.draw.circle(glow_surf, (*FOOD_DATA[self.type]["color"], 100), 
                             (CELL_SIZE//2+5, CELL_SIZE//2+5), CELL_SIZE//2+2)
            glow_rect = glow_surf.get_rect(center=(center_x, center_y + float_offset))
            surface.blit(glow_surf, glow_rect)
        
        # Draw particles
        self.particles.draw(surface)

# Power-up item
class PowerUp:
    def __init__(self):
        self.position = (0, 0)
        self.type = None
        self.active = False
        self.spawn_timer = 0
        self.animation_angle = 0
        self.float_offset = 0
        self.float_direction = 1
    
    def try_spawn(self, snake_positions, foods):
        if not self.active and self.spawn_timer <= 0:
            # 5% chance to spawn a power-up
            if random.random() < 0.05:
                # Try to find a valid position
                for _ in range(20):
                    position = (random.randint(1, GRID_WIDTH - 2), 
                               random.randint(1, GRID_HEIGHT - 2))
                    
                    # Check if position is not on snake and not on food
                    if (position not in snake_positions and 
                        not any(food.position == position for food in foods)):
                        
                        self.position = position
                        self.type = random.choice(list(POWER_UPS.keys()))
                        self.active = True
                        self.animation_angle = 0
                        self.float_offset = 0
                        break
                self.spawn_timer = 20  # Try again in 20 seconds
        else:
            self.spawn_timer -= 1/60
    
    def update(self):
        self.animation_angle += 3
        if self.animation_angle >= 360:
            self.animation_angle = 0
            
        # Floating animation
        self.float_offset += 0.05 * self.float_direction
        if abs(self.float_offset) > 3:
            self.float_direction *= -1
    
    def draw(self, surface):
        if not self.active:
            return
            
        x, y = self.position
        center_x = x * CELL_SIZE + CELL_SIZE // 2
        center_y = y * CELL_SIZE + CELL_SIZE // 2 + self.float_offset
        
        # Draw rotating power-up
        radius = CELL_SIZE // 3 + 2
        points = []
        for i in range(5):
            angle = math.radians(self.animation_angle + i * 72)
            px = center_x + radius * math.cos(angle)
            py = center_y + radius * math.sin(angle)
            points.append((px, py))
        
        pygame.draw.polygon(surface, POWER_UPS[self.type]["color"], points)
        
        # Draw glow effect
        glow_surf = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
        pygame.draw.circle(glow_surf, (*POWER_UPS[self.type]["color"], 100), 
                         (CELL_SIZE//2, CELL_SIZE//2), CELL_SIZE//2)
        surface.blit(glow_surf, (center_x - CELL_SIZE//2, center_y - CELL_SIZE//2))
        
        # Draw power-up icon
        icon_text = small_font.render("P", True, (255, 255, 255))
        icon_rect = icon_text.get_rect(center=(center_x, center_y))
        surface.blit(icon_text, icon_rect)

# Snake class with smooth movement
class Snake:
    def __init__(self):
        self.reset()
    
    def reset(self):
        self.positions = [(GRID_WIDTH // 2, GRID_HEIGHT // 2)]
        self.direction = (1, 0)
        self.next_direction = (1, 0)
        self.length = 3
        self.score = 0
        self.health = 10
        self.max_health = 20
        self.alive = True
        self.growth_pending = 0
        self.speed_multiplier = 1.0
        self.power_up_timers = {}
        self.particles = ParticleSystem()
        self.magnet_range = 0
    
    def get_head_position(self):
        return self.positions[0]
    
    def update(self):
        if not self.alive:
            return
            
        # Update power-up timers
        for power_up in list(self.power_up_timers.keys()):
            self.power_up_timers[power_up] -= 1/60
            if self.power_up_timers[power_up] <= 0:
                del self.power_up_timers[power_up]
                if power_up == "speed_boost":
                    self.speed_multiplier = 1.0
                elif power_up == "magnet":
                    self.magnet_range = 0
        
        # Change direction
        self.direction = self.next_direction
        
        # Move snake
        head_x, head_y = self.get_head_position()
        dir_x, dir_y = self.direction
        new_x = (head_x + dir_x) % GRID_WIDTH
        new_y = (head_y + dir_y) % GRID_HEIGHT
        
        # Check for collision with self
        if (new_x, new_y) in self.positions[1:]:
            self.alive = False
            # Create death particles
            center_x = new_x * CELL_SIZE + CELL_SIZE // 2
            center_y = new_y * CELL_SIZE + CELL_SIZE // 2
            self.particles.add_particles(center_x, center_y, (255, 50, 50), 30)
            return
        
        # Move snake
        self.positions.insert(0, (new_x, new_y))
        
        # Handle growth
        if self.growth_pending > 0:
            self.growth_pending -= 1
        else:
            if len(self.positions) > self.length:
                self.positions.pop()
        
        # Update particles
        self.particles.update()
    
    def change_direction(self, new_direction):
        # Prevent 180-degree turns
        if (new_direction[0] * -1, new_direction[1] * -1) != self.direction:
            self.next_direction = new_direction
    
    def eat_food(self, food_type):
        food_data = FOOD_DATA[food_type]
        
        # Apply double points if active
        points_multiplier = 2 if self.has_power_up("double_points") else 1
        actual_points = food_data["points"] * points_multiplier
        
        self.score += actual_points
        self.health += food_data["health"]
        
        # Cap health at max_health
        self.health = min(self.health, self.max_health)
        
        # Add growth
        self.growth_pending += 1
        self.length += 1
        
        # Create eating particles
        head_x, head_y = self.get_head_position()
        center_x = head_x * CELL_SIZE + CELL_SIZE // 2
        center_y = head_y * CELL_SIZE + CELL_SIZE // 2
        self.particles.add_particles(center_x, center_y, food_data["color"], 15)
        
        # Check if snake died from bad health
        if self.health <= 0:
            self.alive = False
    
    def activate_power_up(self, power_up_type):
        power_up_data = POWER_UPS[power_up_type]
        
        if power_up_data["effect"] == "speed":
            self.speed_multiplier = 1.5
            self.power_up_timers[power_up_type] = power_up_data["duration"]
        elif power_up_data["effect"] == "health":
            self.health = min(self.health + 5, self.max_health)
        elif power_up_data["effect"] == "points":
            self.power_up_timers[power_up_type] = power_up_data["duration"]
        elif power_up_data["effect"] == "magnet":
            self.magnet_range = 3
            self.power_up_timers[power_up_type] = power_up_data["duration"]
    
    def has_power_up(self, power_up_type):
        return power_up_type in self.power_up_timers
    
    def get_magnet_range(self):
        return self.magnet_range if self.has_power_up("magnet") else 0
    
    def draw(self, surface):
        # Draw snake body with gradient
        for i, (x, y) in enumerate(self.positions):
            # Calculate color intensity based on position in snake
            intensity = max(0.5, 1.0 - (i / len(self.positions)) * 0.5)
            color = (
                int(SNAKE_BODY[0] * intensity),
                int(SNAKE_BODY[1] * intensity),
                int(SNAKE_BODY[2] * intensity)
            )
            
            # Draw snake segment with rounded corners
            rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            pygame.draw.rect(surface, color, rect, border_radius=8)
            
            # Draw segment border
            pygame.draw.rect(surface, (color[0]//2, color[1]//2, color[2]//2), rect, 2, border_radius=8)
        
        # Draw snake head with different color
        head_x, head_y = self.positions[0]
        head_rect = pygame.Rect(head_x * CELL_SIZE, head_y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
        pygame.draw.rect(surface, SNAKE_HEAD, head_rect, border_radius=10)
        
        # Draw magnet range if active
        if self.has_power_up("magnet"):
            magnet_surf = pygame.Surface((self.magnet_range * 2 * CELL_SIZE, 
                                        self.magnet_range * 2 * CELL_SIZE), 
                                       pygame.SRCALPHA)
            pygame.draw.circle(magnet_surf, (156, 39, 176, 50), 
                             (self.magnet_range * CELL_SIZE, self.magnet_range * CELL_SIZE), 
                             self.magnet_range * CELL_SIZE)
            magnet_rect = magnet_surf.get_rect(center=head_rect.center)
            surface.blit(magnet_surf, magnet_rect)
        
        # Draw eyes on head
        eye_size = CELL_SIZE // 5
        # Determine eye positions based on direction
        if self.direction == (1, 0):  # Right
            left_eye = (head_rect.right - eye_size - 4, head_rect.top + eye_size + 4)
            right_eye = (head_rect.right - eye_size - 4, head_rect.bottom - eye_size - 4)
        elif self.direction == (-1, 0):  # Left
            left_eye = (head_rect.left + 4, head_rect.top + eye_size + 4)
            right_eye = (head_rect.left + 4, head_rect.bottom - eye_size - 4)
        elif self.direction == (0, 1):  # Down
            left_eye = (head_rect.left + eye_size + 4, head_rect.bottom - eye_size - 4)
            right_eye = (head_rect.right - eye_size - 4, head_rect.bottom - eye_size - 4)
        else:  # Up
            left_eye = (head_rect.left + eye_size + 4, head_rect.top + 4)
            right_eye = (head_rect.right - eye_size - 4, head_rect.top + 4)
        
        pygame.draw.circle(surface, (0, 0, 0), left_eye, eye_size)
        pygame.draw.circle(surface, (0, 0, 0), right_eye, eye_size)
        
        # Draw particles
        self.particles.draw(surface)

# Score manager for multiple users
class ScoreManager:
    def __init__(self):
        self.scores_file = "daily_scores.json"
        self.load_scores()
    
    def load_scores(self):
        try:
            with open(self.scores_file, 'r') as f:
                self.scores = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            self.scores = {}
    
    def save_scores(self):
        with open(self.scores_file, 'w') as f:
            json.dump(self.scores, f)
    
    def add_score(self, player_name, score, health):
        today = datetime.now().strftime("%Y-%m-%d")
        if today not in self.scores:
            self.scores[today] = {}
        
        self.scores[today][player_name] = {
            "score": score,
            "health": health,
            "timestamp": datetime.now().strftime("%H:%M:%S")
        }
        self.save_scores()
    
    def get_daily_scores(self):
        today = datetime.now().strftime("%Y-%m-%d")
        return self.scores.get(today, {})

# Main game class
class Game:
    def __init__(self):
        self.food_images = load_food_images()
        self.snake = Snake()
        self.food_manager = FoodManager(self.food_images)
        self.power_up = PowerUp()
        self.score_manager = ScoreManager()
        self.player_name = "Player1"
        self.game_over = False
        self.paused = False
        self.move_timer = 0
        self.background_particles = ParticleSystem()
        
        # Generate background particles
        for _ in range(50):
            x = random.randint(0, WIDTH)
            y = random.randint(0, HEIGHT)
            color = random.choice([(100, 100, 150), (150, 100, 100), (100, 150, 100)])
            self.background_particles.particles.append(Particle(x, y, color))
        
        # Spawn initial foods
        for _ in range(4):
            self.food_manager.spawn_food(self.snake.positions)
    
    def update(self):
        if self.paused or self.game_over:
            return
            
        # Update background particles
        self.background_particles.update()
        
        # Update game objects
        self.food_manager.update(self.snake.positions)
        self.power_up.update()
        self.power_up.try_spawn(self.snake.positions, self.food_manager.foods)
        
        # Handle magnet power-up (attract nearby foods)
        if self.snake.has_power_up("magnet"):
            magnet_range = self.snake.get_magnet_range()
            head_x, head_y = self.snake.get_head_position()
            
            for food in self.food_manager.foods[:]:
                food_x, food_y = food.position
                distance = math.sqrt((head_x - food_x)**2 + (head_y - food_y)**2)
                
                if distance <= magnet_range and distance > 0:
                    # Move food toward snake
                    dir_x = head_x - food_x
                    dir_y = head_y - food_y
                    length = math.sqrt(dir_x**2 + dir_y**2)
                    if length > 0:
                        dir_x /= length
                        dir_y /= length
                    
                    new_x = food_x + dir_x * 0.3
                    new_y = food_y + dir_y * 0.3
                    
                    # Check if new position is valid
                    new_pos = (round(new_x), round(new_y))
                    if (0 <= new_pos[0] < GRID_WIDTH and 0 <= new_pos[1] < GRID_HEIGHT and
                        new_pos not in self.snake.positions and
                        not any(f.position == new_pos for f in self.food_manager.foods if f != food)):
                        food.position = new_pos
        
        # Move snake based on speed
        self.move_timer += 1/60 * self.snake.speed_multiplier
        if self.move_timer >= 1/GAME_SPEED:
            self.snake.update()
            self.move_timer = 0
            
            # Check if snake ate any food
            head_pos = self.snake.get_head_position()
            food_to_eat = self.food_manager.get_food_at_position(head_pos)
            if food_to_eat:
                self.snake.eat_food(food_to_eat.type)
                self.food_manager.remove_food(head_pos)
            
            # Check if snake got power-up
            if (self.power_up.active and 
                self.snake.get_head_position() == self.power_up.position):
                self.snake.activate_power_up(self.power_up.type)
                self.power_up.active = False
            
            # Check if snake is dead
            if not self.snake.alive:
                self.game_over = True
                self.score_manager.add_score(
                    self.player_name, 
                    self.snake.score, 
                    self.snake.health
                )
    
    def draw(self, surface):
        # Draw background
        surface.fill(BACKGROUND)
        
        # Draw grid (subtle)
        for x in range(0, WIDTH, CELL_SIZE):
            pygame.draw.line(surface, GRID_COLOR, (x, 0), (x, HEIGHT), 1)
        for y in range(0, HEIGHT, CELL_SIZE):
            pygame.draw.line(surface, GRID_COLOR, (0, y), (WIDTH, y), 1)
        
        # Draw background particles
        self.background_particles.draw(surface)
        
        # Draw game objects
        self.food_manager.draw(surface)
        if self.power_up.active:
            self.power_up.draw(surface)
        self.snake.draw(surface)
        
        # Draw UI
        self.draw_ui(surface)
        
        # Draw game over screen
        if self.game_over:
            self.draw_game_over(surface)
        
        # Draw pause screen
        elif self.paused:
            self.draw_pause_screen(surface)
    
    def draw_ui(self, surface):
        # Draw score
        score_text = medium_font.render(f"Score: {self.snake.score}", True, TEXT_COLOR)
        surface.blit(score_text, (20, 20))
        
        # Draw food count
        food_count_text = small_font.render(f"Foods: {len(self.food_manager.foods)}/{MAX_FOODS}", True, TEXT_COLOR)
        surface.blit(food_count_text, (20, 55))
        
        # Draw health bar
        health_width = 200
        health_height = 20
        health_x = WIDTH - health_width - 20
        health_y = 20
        
        # Health bar background
        pygame.draw.rect(surface, (50, 50, 50), 
                        (health_x, health_y, health_width, health_height), 
                        border_radius=10)
        
        # Health bar fill
        health_ratio = self.snake.health / self.snake.max_health
        fill_width = max(0, health_width * health_ratio)
        health_color = HEALTH_BAR_GOOD if health_ratio > 0.3 else HEALTH_BAR_BAD
        pygame.draw.rect(surface, health_color, 
                        (health_x, health_y, fill_width, health_height), 
                        border_radius=10)
        
        # Health text
        health_text = medium_font.render(f"Health: {self.snake.health}", True, TEXT_COLOR)
        surface.blit(health_text, (health_x, health_y + 25))
        
        # Active power-ups
        y_offset = 70
        for power_up, timer in self.snake.power_up_timers.items():
            power_up_text = small_font.render(
                f"{power_up}: {timer:.1f}s", True, POWER_UPS[power_up]["color"]
            )
            surface.blit(power_up_text, (WIDTH - 200, y_offset))
            y_offset += 25
        
        # Draw food legend
        self.draw_food_legend(surface)
    
    def draw_food_legend(self, surface):
        # Draw legend background
        legend_width = 200
        legend_height = 250
        legend_x = 20
        legend_y = HEIGHT - legend_height - 20
        
        # Legend background
        legend_bg = pygame.Surface((legend_width, legend_height), pygame.SRCALPHA)
        legend_bg.fill((0, 0, 0, 150))
        surface.blit(legend_bg, (legend_x, legend_y))
        
        # Legend title
        legend_title = small_font.render("Food Guide", True, TEXT_COLOR)
        surface.blit(legend_title, (legend_x + 10, legend_y + 10))
        
        # Draw food items in legend
        y_offset = 40
        healthy_foods = [food for food in FOOD_DATA.keys() if FOOD_DATA[food]["health"] > 0][:4]
        unhealthy_foods = [food for food in FOOD_DATA.keys() if FOOD_DATA[food]["health"] < 0][:4]
        
        # Healthy foods
        healthy_text = small_font.render("Healthy (+):", True, HEALTH_BAR_GOOD)
        surface.blit(healthy_text, (legend_x + 10, legend_y + y_offset))
        y_offset += 25
        
        for i, food in enumerate(healthy_foods):
            food_img = self.food_images[food]
            surface.blit(food_img, (legend_x + 10 + (i % 2) * 60, legend_y + y_offset + (i // 2) * 40))
        
        # Unhealthy foods  
        y_offset += 80
        unhealthy_text = small_font.render("Unhealthy (-):", True, HEALTH_BAR_BAD)
        surface.blit(unhealthy_text, (legend_x + 10, legend_y + y_offset))
        y_offset += 25
        
        for i, food in enumerate(unhealthy_foods):
            food_img = self.food_images[food]
            surface.blit(food_img, (legend_x + 10 + (i % 2) * 60, legend_y + y_offset + (i // 2) * 40))
    
    def draw_game_over(self, surface):
        # Semi-transparent overlay
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        surface.blit(overlay, (0, 0))
        
        # Game over text
        game_over_text = title_font.render("GAME OVER", True, (255, 100, 100))
        surface.blit(game_over_text, (WIDTH//2 - game_over_text.get_width()//2, HEIGHT//2 - 100))
        
        # Final score
        score_text = large_font.render(f"Final Score: {self.snake.score}", True, TEXT_COLOR)
        surface.blit(score_text, (WIDTH//2 - score_text.get_width()//2, HEIGHT//2 - 20))
        
        # Health status
        health_status = "Healthy Snake!" if self.snake.health > 0 else "Unhealthy Snake!"
        health_color = (100, 255, 100) if self.snake.health > 0 else (255, 100, 100)
        health_text = large_font.render(health_status, True, health_color)
        surface.blit(health_text, (WIDTH//2 - health_text.get_width()//2, HEIGHT//2 + 30))
        
        # Restart instruction
        restart_text = medium_font.render("Press R to Restart or Q to Quit", True, TEXT_COLOR)
        surface.blit(restart_text, (WIDTH//2 - restart_text.get_width()//2, HEIGHT//2 + 100))
    
    def draw_pause_screen(self, surface):
        # Semi-transparent overlay
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        surface.blit(overlay, (0, 0))
        
        # Pause text
        pause_text = title_font.render("PAUSED", True, (255, 255, 100))
        surface.blit(pause_text, (WIDTH//2 - pause_text.get_width()//2, HEIGHT//2 - 50))
        
        # Continue instruction
        continue_text = medium_font.render("Press P to Continue", True, TEXT_COLOR)
        surface.blit(continue_text, (WIDTH//2 - continue_text.get_width()//2, HEIGHT//2 + 30))
    
    def reset(self):
        self.snake.reset()
        self.food_manager = FoodManager(self.food_images)
        self.power_up.active = False
        self.game_over = False
        self.move_timer = 0
        
        # Spawn initial foods
        for _ in range(4):
            self.food_manager.spawn_food(self.snake.positions)

# Create images directory and sample images
def setup_images():
    if not os.path.exists("images"):
        os.makedirs("images")
        print("Created 'images' directory.")
        print("Please add PNG images with these exact names:")
        for food_type in FOOD_DATA.keys():
            print(f"  - {food_type}.png")
        print("\nThe game will use placeholder images until you add real images.")

# Main game loop
def main():
    setup_images()
    game = Game()
    running = True
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if not game.game_over and not game.paused:
                    if event.key == pygame.K_UP:
                        game.snake.change_direction((0, -1))
                    elif event.key == pygame.K_DOWN:
                        game.snake.change_direction((0, 1))
                    elif event.key == pygame.K_LEFT:
                        game.snake.change_direction((-1, 0))
                    elif event.key == pygame.K_RIGHT:
                        game.snake.change_direction((1, 0))
                
                if event.key == pygame.K_p:
                    game.paused = not game.paused
                
                if event.key == pygame.K_r and game.game_over:
                    game.reset()
                
                if event.key == pygame.K_q and game.game_over:
                    running = False
        
        game.update()
        game.draw(screen)
        
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()

if __name__ == "__main__":
    main()