import random
from constants import *
import pygame
import numpy as np


class Moss:
    def __init__(self,
                 lifespan=None,
                 dominate_gene=None,
                 color=None,
                 size=None,
                 pos_x=None,
                 pos_y=None,
                 up=True,
                 down=True,
                 left=True,
                 right=True,
                 up_preference=15,
                 down_preference=15,
                 left_preference=15,
                 right_preference=15
                 ):
        self.lifespan = lifespan
        self.lifetime = 0
        self.dominate_gene = dominate_gene
        self.color = color
        self.size = size
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.up = up
        self.down = down
        self.left = left
        self.right = right

        self.up_preference = up_preference
        self.down_preference = down_preference
        self.left_preference = left_preference
        self.right_preference = right_preference

        self.done_growing = False


class TheMossManager:
    def __init__(self, screen):
        self.screen = screen
        self.all_mosses = []
        self.mosses_to_die = []
        self.position_map = {}
        self.max_mosses = 10000
        self.total_mosses = 1
        self.total_operations = 0
        self.size = 3
        self.offset = self.size / 1.5

        self.pixel_surface = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.pixel_surface.fill(BLACK)
        self.pixel_array = pygame.surfarray.pixels3d(self.pixel_surface)

        self.proto_moss = Moss(lifespan=20, dominate_gene="none", color=GRAY, size=self.size, pos_x=WINDOW_WIDTH // 2,
                               pos_y=WINDOW_HEIGHT // 2)
        self.all_mosses.append(self.proto_moss)
        self.position_map[f"{self.proto_moss.pos_x},{self.proto_moss.pos_y}"] = self.proto_moss

    def draw_moss_to_array(self, moss):
        """Draw a moss circle directly to the pixel array"""
        x, y = int(moss.pos_x), int(moss.pos_y)
        r, g, b = moss.color
        size = int(moss.size)

        # Calculate circle bounds
        x_min = max(0, x - size)
        x_max = min(WINDOW_WIDTH - 1, x + size)
        y_min = max(0, y - size)
        y_max = min(WINDOW_HEIGHT - 1, y + size)

        # Create coordinate arrays
        Y, X = np.ogrid[y_min:y_max + 1, x_min:x_max + 1]
        dist = np.sqrt((X - x) ** 2 + (Y - y) ** 2)

        # Create circle mask
        mask = dist <= size

        # Update pixels within circle
        self.pixel_array[x_min:x_max + 1, y_min:y_max + 1][mask.T] = [r, g, b]

    def handle_direction_gene(self, parent_moss):
        # Get current preferences
        up_pref = parent_moss.up_preference
        down_pref = parent_moss.down_preference
        left_pref = parent_moss.left_preference
        right_pref = parent_moss.right_preference

        # Add random drift to each preference
        drift = 10
        up_pref += random.uniform(-drift, drift)
        down_pref += random.uniform(-drift, drift)
        left_pref += random.uniform(-drift, drift)
        right_pref += random.uniform(-drift, drift)

        # Clamp values between 0 and 100
        up_pref = max(0, min(100, up_pref))
        down_pref = max(0, min(100, down_pref))
        left_pref = max(0, min(100, left_pref))
        right_pref = max(0, min(100, right_pref))

        # Determine strongest preference
        preferences = {
            'up': up_pref,
            'down': down_pref,
            'left': left_pref,
            'right': right_pref
        }

        strongest_direction = max(preferences, key=preferences.get)
        bonus = 10

        # Apply bonus to strongest direction and reduce opposite direction
        if strongest_direction == 'up':
            up_pref += bonus
            down_pref = max(0, down_pref - bonus)  # Reduce opposite direction
        elif strongest_direction == 'down':
            down_pref += bonus
            up_pref = max(0, up_pref - bonus)  # Reduce opposite direction
        elif strongest_direction == 'left':
            left_pref += bonus
            right_pref = max(0, right_pref - bonus)  # Reduce opposite direction
        else:  # right
            right_pref += bonus
            left_pref = max(0, left_pref - bonus)  # Reduce opposite direction

        # Normalize the pairs to ensure they sum to at most 100
        total_vertical = up_pref + down_pref
        if total_vertical > 100:
            scale = 100 / total_vertical
            up_pref *= scale
            down_pref *= scale

        total_horizontal = left_pref + right_pref
        if total_horizontal > 100:
            scale = 100 / total_horizontal
            left_pref *= scale
            right_pref *= scale

        # Final clamp to ensure values stay within bounds
        up_pref = max(0, min(100, up_pref))
        down_pref = max(0, min(100, down_pref))
        left_pref = max(0, min(100, left_pref))
        right_pref = max(0, min(100, right_pref))

        return up_pref, down_pref, left_pref, right_pref

    def handle_color_genes(self, parent_moss):
        r, g, b = parent_moss.color

        parent_gene = parent_moss.dominate_gene
        gene_preference_strength = 35
        drift = 10

        # Apply gene preference
        if parent_gene == "r":
            r += gene_preference_strength
        if parent_gene == "g":
            g += gene_preference_strength
        if parent_gene == "b":
            b += gene_preference_strength
        if parent_gene == "white":
            r += 2
            g += 2
            b += 2

        # Add random drift to each color
        r += int(random.uniform(-drift, drift))
        g += int(random.uniform(-drift, drift))
        b += int(random.uniform(-drift, drift))

        # completely random mutation
        # total_mutation = random.uniform(0,1000)
        # if total_mutation > 999:
        #     r = random.uniform(0,255)
        #     g = random.uniform(0,255)
        #     b = random.uniform(0,255)

        # Clamp RGB values between 0 and 255
        r = max(0, min(255, r))
        g = max(0, min(255, g))
        b = max(0, min(255, b))

        # Check if colors are balanced (max difference < threshold)
        balance_threshold = 15
        if (abs(r - g) < balance_threshold and
                abs(g - b) < balance_threshold and
                abs(r - b) < balance_threshold):
            gene_preference = "white"
        else:
            # Determine strongest color and assign gene preference
            if r >= g and r >= b:
                gene_preference = "r"
            elif g >= r and g >= b:
                gene_preference = "g"
            else:
                gene_preference = "b"

        color = (r, g, b)

        return color, gene_preference

    def handle_lifespan_gene(self, moss):
        # lifespan = random.uniform(0,200)
        lifespan = 150
        return int(lifespan)

    def check_position_available(self, x, y, offset):
        self.total_operations += 1
        return f"{x},{y}" not in self.position_map

    def birth_moss(self, parent_moss, pos_x, pos_y, false_direction):
        color, dominate_gene = self.handle_color_genes(parent_moss)
        up_pref, down_pref, left_pref, right_pref = self.handle_direction_gene(parent_moss)

        self.total_operations += 1
        offset = parent_moss.size + self.offset

        # Check boundaries with offset included
        if pos_x + offset > WINDOW_WIDTH or pos_y + offset > WINDOW_HEIGHT:
            return
        if pos_x - offset < 0 or pos_y - offset < 0:
            return

        if self.total_mosses >= self.max_mosses:
            return False

        # Use the proper offset in position check
        if not self.check_position_available(pos_x, pos_y, offset):
            return False

        self.total_mosses += 1
        lifespan = self.handle_lifespan_gene(parent_moss)
        new_moss = Moss(
            lifespan,
            dominate_gene=dominate_gene,
            color=color,
            size=parent_moss.size,
            pos_x=pos_x,
            pos_y=pos_y,
            up_preference=up_pref,
            down_preference=down_pref,
            left_preference=left_pref,
            right_preference=right_pref
        )

        if false_direction == "up":
            new_moss.up = False
        elif false_direction == "down":
            new_moss.down = False
        elif false_direction == "left":
            new_moss.left = False
        elif false_direction == "right":
            new_moss.right = False

        if new_moss.up and f"{pos_x},{pos_y - offset}" in self.position_map:
            new_moss.up = False

        if new_moss.down and f"{pos_x},{pos_y + offset}" in self.position_map:
            new_moss.down = False

        if new_moss.left and f"{pos_x - offset},{pos_y}" in self.position_map:
            new_moss.left = False

        if new_moss.right and f"{pos_x + offset},{pos_y}" in self.position_map:
            new_moss.right = False

        self.all_mosses.append(new_moss)
        self.draw_moss_to_array(new_moss)
        self.position_map[f"{pos_x},{pos_y}"] = new_moss
        return True

    def grow_the_moss(self, moss):
        if moss.done_growing:
            return

        if self.total_mosses >= self.max_mosses:
            return

        offset = moss.size + self.offset

        available_directions = []
        weights = []

        if moss.up:
            available_directions.append(('up', moss.pos_x, moss.pos_y - offset, "down"))
            weights.append(moss.up_preference)
        if moss.down:
            available_directions.append(('down', moss.pos_x, moss.pos_y + offset, "up"))
            weights.append(moss.down_preference)
        if moss.left:
            available_directions.append(('left', moss.pos_x - offset, moss.pos_y, "right"))
            weights.append(moss.left_preference)
        if moss.right:
            available_directions.append(('right', moss.pos_x + offset, moss.pos_y, "left"))
            weights.append(moss.right_preference)

        # If there are available directions, choose one based on preferences
        if available_directions:
            # Normalize weights to sum to 1.0 for random.choices
            total_weight = sum(weights)
            if total_weight > 0:  # Prevent division by zero
                normalized_weights = [w / total_weight for w in weights]
                direction, x, y, false_dir = random.choices(available_directions, weights=normalized_weights, k=1)[0]

                # Still use a growth chance to control overall growth rate
                grow_chance = random.uniform(0, 100)
                if grow_chance < 15:  # Base growth chance
                    if self.birth_moss(moss, x, y, false_dir):
                        setattr(moss, direction, False)

        if not any([moss.up, moss.down, moss.left, moss.right]):
            self.total_operations += 1
            moss.done_growing = True

    def kill_the_moss(self, moss):
        self.total_mosses -= 1
        self.total_operations += 1
        self.all_mosses.remove(moss)
        self.position_map.pop(f"{moss.pos_x},{moss.pos_y}")

    def update(self):
        self.total_operations = 0

        if self.total_mosses <= 0:
            e_moss = Moss(lifespan=20, dominate_gene="none", color=WHITE, size=self.size, pos_x=WINDOW_WIDTH // 2,
                          pos_y=WINDOW_HEIGHT // 2)
            self.all_mosses.append(e_moss)
            self.position_map[f"{e_moss.pos_x},{e_moss.pos_y}"] = e_moss

        for moss in self.all_mosses:
            self.total_operations += 1
            moss.lifetime += 1

            if moss.lifetime > moss.lifespan:
                if moss not in self.mosses_to_die:  # Prevent duplicate additions
                    self.mosses_to_die.append(moss)
            else:
                self.grow_the_moss(moss)

        if self.mosses_to_die:
            for moss in self.mosses_to_die:
                self.kill_the_moss(moss)
            self.mosses_to_die.clear()

        self.draw_the_mosses()
        # self.draw_data()

    def draw_the_mosses(self):
        pygame.surfarray.blit_array(self.screen, self.pixel_array)

    # def draw_the_mosses(self):
    #     font = pygame.font.Font(None, 20)  # Small font size
    #     self.screen.fill(BLACK)
    #     for moss in self.all_mosses:
    #         pos = (int(moss.pos_x), int(moss.pos_y))
    #         pygame.draw.circle(self.screen, moss.color, pos, moss.size)
    # if moss.dominate_gene:
    #     gene_text = font.render(f"{moss.dominate_gene}", True, (255, 255, 255))
    #     gene_x = moss.pos_x - gene_text.get_width() / 2
    #     gene_y = moss.pos_y - moss.size
    #     self.screen.blit(gene_text, (gene_x, gene_y))

    def draw_data(self):
        font = pygame.font.Font(None, 100)
        text = font.render(f"{self.total_operations}, total:{self.total_mosses}", True, (WHITE))
        self.screen.blit(text, (10, 10))
