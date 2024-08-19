import pygame
from level1 import Level1
from level2 import Level2
from level3 import Level3
from level4 import Level4


WIDTH = 800
HEIGHT = 600
FPS = 70


pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()



levels = [Level1(), Level2(), Level3(), Level4()]
level_index = 0
current_level = levels[level_index]

# Loop principal
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        current_level.handle_event(event)
    current_level.update()
    current_level.draw(screen)

    if current_level.game_over and current_level.knight_won:
        level_index += 1  # Avanzar al siguiente nivel
        if level_index < len(levels):
            current_level = levels[level_index]
        else:
            print("Game completed. ¡Congratulations!")
            running = False

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
