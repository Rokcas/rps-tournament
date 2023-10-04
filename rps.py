import math
import random
import pygame
import copy

PLAYER_SIZE = (40, 40)
SCREEN_SIZE = (800, 800)
STARTING_MOVE_SPEED = 0.1
MOVE_SPEED = 0.15
TEAM_SIZE = 10

rock_image = pygame.transform.scale(pygame.image.load('rock.png'), PLAYER_SIZE)
paper_image = pygame.transform.scale(pygame.image.load('paper.png'), PLAYER_SIZE)
scissors_image = pygame.transform.scale(pygame.image.load('scissors.png'), PLAYER_SIZE)

class Player:
    def get_next_position(self, players):
        enemies = [t for t in players if type(t) != type(self)]
        if not enemies:
            return self.position

        weighted_directions = []
        for enemy in enemies:
            direction = tuple(e - p for e, p in zip(enemy.position, self.position))
            magnitude = math.sqrt(direction[0] * direction[0] + direction[1] * direction[1])
            if magnitude > MOVE_SPEED:
                direction = tuple(MOVE_SPEED * i / magnitude for i in direction)
            weight = 1 / math.dist(self.position, enemy.position) ** 4

            if enemy.beats == type(self):
                direction = tuple(-i for i in direction)
                weight /= 2

            weighted_directions.append((direction, weight))

        direction_x = sum(x * w for (x, _), w in weighted_directions)
        direction_y = sum(y * w for (_, y), w in weighted_directions)
        direction = (direction_x, direction_y)

        teammates = len([type(p) == type(self) for p in players])
        move_bonus = 1 + 10 / teammates

        magnitude = math.sqrt(direction[0] * direction[0] + direction[1] * direction[1])
        if magnitude > 0:
            direction = tuple(move_bonus * MOVE_SPEED * i / magnitude for i in direction)

        direction = tuple(i + random.uniform(-MOVE_SPEED * 0.2, MOVE_SPEED * 0.2) for i in direction)

        new_position = tuple(c + d for c, d in zip(self.position, direction))
        return tuple(max(p, min(n, s - p)) for p, s, n in zip(PLAYER_SIZE, SCREEN_SIZE, new_position))


    def get_new_team(self, players):
        enemies = [e for e in players if e.beats == type(self)]
        if not enemies:
            return self

        nearest_enemy = min(enemies, key=lambda p: math.dist(self.position, p.position))
        if (any(abs(e - p) > d for p, e, d in zip(self.position, nearest_enemy.position, PLAYER_SIZE))):
            return self

        return type(nearest_enemy)(self.position)

class Rock(Player):
    def __init__(self, position):
        self.beats = Scissors
        self.position = position
        self.image = rock_image

class Paper(Player):
    def __init__(self, position):
        self.beats = Rock
        self.position = position
        self.image = paper_image

class Scissors(Player):
    def __init__(self, position):
        self.beats = Paper
        self.position = position
        self.image = scissors_image

pygame.init()

screen = pygame.display.set_mode(SCREEN_SIZE)
pygame.display.set_caption('Rock paper scissors tournament')
pygame.display.set_icon(rock_image)

def generate_random_position():
    return tuple(random.uniform(p, s - p) for s, p in zip(SCREEN_SIZE, PLAYER_SIZE))

players = [init(generate_random_position()) for _ in range(TEAM_SIZE) for init in [Rock, Paper, Scissors]]
running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    pygame.display.flip()
    screen.fill((255, 255, 255))

    # Render
    for player in players:
        screen.blit(player.image, (player.position[0] - PLAYER_SIZE[0] / 2, player.position[1] - PLAYER_SIZE[1] / 2))

    # Move
    players = [type(p)(p.get_next_position(players)) for p in players]

    # Update teams
    players = [p.get_new_team(players) for p in players.copy()]

    MOVE_SPEED = STARTING_MOVE_SPEED + pygame.time.get_ticks() / 50000

pygame.quit()
