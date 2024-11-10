import pygame
import sys
import random
import threading
import tkinter as tk
from pygame.locals import *
from wallsgen import wallsgen


class FunctionGame:
    def __init__(self):
        # Инициализируем Pygame
        pygame.init()
        # Задаем окно
        self.WIDTH, self.HEIGHT = 400, 800
        self.WINDOW = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption("Function Game")
        # Определяем цвета
        self.WHITE = (255, 255, 255)
        self.BLUE = (0, 0, 255)
        self.RED = (255, 0, 0)
        # Атрибуты игрока 
        self.player_pos = [self.WIDTH // 2, self.HEIGHT - 10]
        self.player_size = [20, 20]
        self.player_speed = 1
        # Атрибуты стены
        self.wall_size = [20, 20]
        self.wall_speed = 1
        self.walls = []
        # Игровые переменные
        self.clock = pygame.time.Clock()
        self.game_running = True
        waiting_for_input = False
        input_result = None

    def redraw_window(self):
        self.WINDOW.fill(self.WHITE)
        pygame.draw.rect(self.WINDOW, self.BLUE, (self.player_pos[0], self.player_pos[1], self.player_size[0], self.player_size[1]))
        for wall in self.walls:
            pygame.draw.rect(self.WINDOW, self.RED, (wall[0], wall[1], self.wall_size[0], self.wall_size[1]))
            
        pygame.display.update()

    def main(self):
        while self.game_running:
            self.clock.tick(30)
            #! Выход из игры
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()
            self.player_pos[1] -= self.player_speed
            # print(self.player_pos[0], self.player_pos[1])
            print(self.walls)
            if random.randint(1, 200) == 1:
                wallsgen(self.WIDTH, 0, 20, 2, wall=self.walls)
            # Движение стен на игрока
            for wall in self.walls:
                wall[1] += self.wall_speed
            # Remove walls that have moved off screen
            self.walls = [wall for wall in self.walls if wall[1] + self.wall_size[1] > 0]
            self.redraw_window()

if __name__ == "__main__":
    x = FunctionGame()
    x.main()
