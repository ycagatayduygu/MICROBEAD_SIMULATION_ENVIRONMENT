import pygame
from pygame.locals import *
import math
resolution = (400, 300)
white = (255, 255, 255)
black = (0, 0, 0)
red = (255, 0, 0)

screen = pygame.display.set_mode(resolution)

class Robot:
    def __init__(self, object_type=None, xPos=resolution[0] / 2, yPos=resolution[1] / 2, xVel=0, yVel=0, rad=15):
        self.x = xPos
        self.y = yPos
        self.dx = xVel
        self.dy = yVel
        self.radius = rad
        self.type = object_type

    def draw(self, surface):
        pygame.draw.circle(surface, black, (int(self.x), int(self.y)), self.radius)

    def update(self, gameObjects, potential_field):
        self.x += self.dx
        self.y += self.dy
        keys = pygame.key.get_pressed()

        # Limit the velocity
        if keys[K_LEFT]:
            self.dx = max(self.dx - 1, -2)
        if keys[K_RIGHT]:
            self.dx = min(self.dx + 1, 2)
        if keys[K_DOWN]:
            self.dy = min(self.dy + 1, 2)
        if keys[K_UP]:
            self.dy = max(self.dy - 1, -2)

        # Check if the robot is at the edge of the screen
        at_left_edge = self.x <= self.radius
        at_right_edge = self.x >= resolution[0] - self.radius
        at_top_edge = self.y <= self.radius
        at_bottom_edge = self.y >= resolution[1] - self.radius

        # Stop the robot if it is at the edge
        if at_left_edge:
            self.x = self.radius
            if keys[K_LEFT]:
                self.dx = 0
        if at_right_edge:
            self.x = resolution[0] - self.radius
            if keys[K_RIGHT]:
                self.dx = 0
        if at_top_edge:
            self.y = self.radius
            if keys[K_UP]:
                self.dy = 0
        if at_bottom_edge:
            self.y = resolution[1] - self.radius
            if keys[K_DOWN]:
                self.dy = 0

        # Only change direction if the corresponding key is pressed
        if not at_left_edge and keys[K_LEFT]:
            self.dx = max(self.dx - 1, -2)
        if not at_right_edge and keys[K_RIGHT]:
            self.dx = min(self.dx + 1, 2)
        if not at_top_edge and keys[K_UP]:
            self.dy = max(self.dy - 1, -2)
        if not at_bottom_edge and keys[K_DOWN]:
            self.dy = min(self.dy + 1, 2)

        # Apply magnetic force based on the potential field
        if not keys[K_LEFT] and not keys[K_RIGHT] and not keys[K_UP] and not keys[K_DOWN]:
            self.dx = 0
            self.dy = 0

        force_x = -potential_field[int(self.y)][int(self.x + self.radius)] + potential_field[int(self.y)][int(self.x - self.radius)]
        force_y = -potential_field[int(self.y + self.radius)][int(self.x)] + potential_field[int(self.y - self.radius)][int(self.x)]

        self.dx += force_x
        self.dy += force_y

        for gameObj in gameObjects:
            if gameObj.type != self.type:
                if isinstance(gameObj, Robot):
                    if (gameObj.x - self.x) ** 2 + (gameObj.y - self.y) ** 2 <= (gameObj.radius + self.radius) ** 2:
                        # Attach the robots
                        total_mass = self.radius ** 2 + gameObj.radius ** 2
                        if at_left_edge or at_right_edge or at_top_edge or at_bottom_edge:
                            gameObj.dx = self.dx
                            gameObj.dy = self.dy
                        else:
                            self.dx = (self.dx * self.radius ** 2 + gameObj.dx * gameObj.radius ** 2) / total_mass
                            self.dy = (self.dy * self.radius ** 2 + gameObj.dy * gameObj.radius ** 2) / total_mass
                            gameObj.dx = self.dx
                            gameObj.dy = self.dy
                else:
                    if (gameObj.x - self.x) ** 2 + (gameObj.y - self.y) ** 2 <= (gameObj.radius + self.radius) ** 2:
                        self.dx *= -1
                        self.dy *= -1


class Material:
    def __init__(self, object_type=None, xPos=300, yPos=250, rad=20):
        self.x = xPos
        self.y = yPos
        self.radius = rad
        self.type = object_type
        self.dx = 0.0
        self.dy = 0.0
        self.max_speed = 0.2  # Set maximum speed here

    def draw(self, surface):
        pygame.draw.circle(surface, red, (int(self.x), int(self.y)), self.radius)

    def update(self, gameObjects, potential_field):
        self.x += self.dx
        self.y += self.dy

        if self.x <= 0 or self.x >= resolution[0]:
            self.dx *= -1
        if self.y <= 0 or self.y >= resolution[1]:
            self.dy *= -1

        # Limit the velocity
        speed = math.sqrt(self.dx ** 2 + self.dy ** 2)
        if speed > self.max_speed:
            scale = self.max_speed / speed
            self.dx *= scale
            self.dy *= scale

        for gameObj in gameObjects:
            if gameObj.type != self.type:
                if (gameObj.x - self.x) ** 2 + (gameObj.y - self.y) ** 2 <= (gameObj.radius + self.radius) ** 2:
                    self.dx += -0.1 * gameObj.dx
                    self.dy += -0.1 * gameObj.dy


class Game:
    def __init__(self):
        pygame.init()

        self.screen = pygame.display.set_mode(resolution)
        self.clock = pygame.time.Clock()
        self.gameObjects = []
        self.gameObjects.append(Material('material'))
        self.gameObjects.append(Robot('robot_1'))
        self.gameObjects.append(Robot('robot_2', 100))
        self.gameObjects.append(Robot('robot_3', 300))

        self.potential_field = self.create_potential_field()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()

    def create_potential_field(self):
        # Create a 2D array to represent the potential field
        potential_field = []
        for y in range(resolution[1]):
            row = []
            for x in range(resolution[0]):
                # Calculate the potential based on position
                force_factor = x / resolution[0]  # Adjust this factor to control the force variation
                potential = -force_factor
                row.append(potential)
            potential_field.append(row)
        return potential_field

    def run(self):
        while True:
            self.handle_events()

            for gameObj in self.gameObjects:
                gameObj.update(self.gameObjects, self.potential_field)

            self.screen.fill(white)

            for gameObj in self.gameObjects:
                gameObj.draw(self.screen)

            self.clock.tick(60)
            pygame.display.flip()


Game().run()
