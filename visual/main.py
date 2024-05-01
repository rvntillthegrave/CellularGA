import os
import cv2
import pygame
import numpy as np
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from cellularAutomaton import CellularAutomaton

""" 
PARAMETRY VZHLEDU SIMULACE CA
ABS_SIZE - velikost celulárního automatu
"""
CELL_SIZE = 20  
CELL_GAP = 1 
ABS_SIZE = 11 
MARGIN = 20 
TEXT_HEIGHT = 50

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (200, 200, 200)

pygame.init()


window_width = CELL_SIZE * ABS_SIZE + CELL_GAP * (ABS_SIZE + 1) + 2 * MARGIN
window_height = CELL_SIZE * ABS_SIZE + CELL_GAP * (ABS_SIZE + 1) + TEXT_HEIGHT + 2 * MARGIN
window_size = (window_width, window_height)
window = pygame.display.set_mode(window_size)
pygame.display.set_caption("Buněčný automat") 

clock = pygame.time.Clock()
font = pygame.font.SysFont('SF Pro', 24)

"""
NASTAVENÍ POČÁTEČNÍHO STAVU
"""
initial_grid = np.zeros((ABS_SIZE, ABS_SIZE), dtype=int)
initial_grid[ABS_SIZE // 2, ABS_SIZE // 2] = 1

ca = CellularAutomaton(ABS_SIZE, ABS_SIZE, initial_grid)

""" 
NASTAVENÍ SIMULACE CELULARNÍHO AUTOMATU
rule_string - pravidla celulárního automatu
max_gen - nastavení délky simulace 
update_rate - rychlost simulace
"""
rule_string = "B023457/S03456"
generation = 0
max_gen = 25
update_rate = 1.9
last_update = pygame.time.get_ticks()

current_directory = os.path.dirname(__file__)
video_path = os.path.join(current_directory, 'simulation.mp4')

fourcc = cv2.VideoWriter_fourcc(*'mp4v')
video_writer = cv2.VideoWriter(video_path, fourcc, update_rate, (window_width, window_height))

running = True
paused = False
while running and generation < (max_gen+1):
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                paused = not paused

    current_time = pygame.time.get_ticks()
    if not paused and current_time - last_update > 1000 // update_rate:
        window.fill(WHITE)

        for x in range(ABS_SIZE + 1):
            pygame.draw.line(window, GRAY, (MARGIN + x * (CELL_SIZE + CELL_GAP), MARGIN + TEXT_HEIGHT),
                             (MARGIN + x * (CELL_SIZE + CELL_GAP), MARGIN + TEXT_HEIGHT + ABS_SIZE * (CELL_SIZE + CELL_GAP)))
        for y in range(ABS_SIZE + 1):
            pygame.draw.line(window, GRAY, (MARGIN, MARGIN + TEXT_HEIGHT + y * (CELL_SIZE + CELL_GAP)),
                             (MARGIN + ABS_SIZE * (CELL_SIZE + CELL_GAP), MARGIN + TEXT_HEIGHT + y * (CELL_SIZE + CELL_GAP)))

        for y in range(ABS_SIZE):
            for x in range(ABS_SIZE):
                cell_x = MARGIN + x * (CELL_SIZE + CELL_GAP) + CELL_GAP
                cell_y = MARGIN + TEXT_HEIGHT + y * (CELL_SIZE + CELL_GAP) + CELL_GAP
                if ca.grid[y][x] == 1:
                    pygame.draw.rect(window, BLACK, (cell_x, cell_y, CELL_SIZE, CELL_SIZE))

        generation_text = font.render(f"Generace {generation}.", True, BLACK)
        generation_text.set_alpha(255)
        text_x = window_width // 2
        text_y = MARGIN // 2 + TEXT_HEIGHT // 2
        text_rect = generation_text.get_rect(center=(text_x, text_y))
        window.blit(generation_text, text_rect)

        rule_text = font.render(f"Pravidlo: {rule_string}", True, BLACK)
        rule_text.set_alpha(255)
        rule_x = window_width // 2
        rule_y = text_y + TEXT_HEIGHT // 2 - 2 
        rule_rect = rule_text.get_rect(center=(rule_x, rule_y))
        window.blit(rule_text, rule_rect)

        pygame.display.flip()
        ca.apply_rules(rule_string)
        ca.grid = ca.next_grid.copy()
        generation += 1
        last_update = current_time

        frame = pygame.surfarray.array3d(window)
        frame = cv2.transpose(cv2.cvtColor(frame, cv2.COLOR_RGB2BGR))
        video_writer.write(frame)

    clock.tick(60)

video_writer.release()
pygame.quit()
