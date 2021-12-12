import pygame
import os
import Objects
import ScreenEngine as SE
from Logic import GameEngine
import Service
import numpy as np

from config import *


if not KEYBOARD_CONTROL:
    import numpy as np
    answer = np.zeros(4, dtype=float)


def process_key():
    global hero, engine, drawer, iteration, size

    event = pygame.event.wait()
    if event.type == pygame.QUIT:
        engine.working = False
    if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_h:
            engine.show_help = not engine.show_help
        if event.key in (pygame.K_KP_PLUS, pygame.K_PLUS, 61):
            # TODO это бы не в engine, а в driver
            engine.sprite_inc()
            # size += 1
            # create_game(size, False)
        if event.key in (pygame.K_KP_MINUS, pygame.K_MINUS):
            # TODO это бы не в engine, а в driver
            engine.sprite_dec()
            # size -= 1
            # create_game(size, False)
        if event.key == pygame.K_g:
            engine.god_mode()
        if event.key == pygame.K_r:
            engine.create_game(sprite_size=None, is_new=True)
            iteration = 0
        if event.key == pygame.K_ESCAPE:
            engine.working = False
        if engine.game_process:
            if event.key == pygame.K_UP:
                engine.move_up()
                iteration += 1
            elif event.key == pygame.K_DOWN:
                engine.move_down()
                iteration += 1
            elif event.key == pygame.K_LEFT:
                engine.move_left()
                iteration += 1
            elif event.key == pygame.K_RIGHT:
                engine.move_right()
                iteration += 1
        else:
            if event.key == pygame.K_RETURN:
                engine.create_game()


def bullshit():
    """ кусок не исполняемого кода ... """
    global hero, engine, drawer, iteration
    # остатки говнокода проекта
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            engine.working = False
    if engine.game_process:
        actions = [
            engine.move_right,
            engine.move_left,
            engine.move_up,
            engine.move_down,
        ]
        answer = np.random.randint(0, 100, 4)
        prev_score = engine.score
        move = actions[np.argmax(answer)]()
        state = pygame.surfarray.array3d(gameDisplay)
        reward = engine.score - prev_score
        print(reward)
    else:
        engine.create_game()


def main():
    global hero, engine, drawer, iteration

    drawer = SE.GameSurface((640, 480), pygame.SRCALPHA, (0, 480),
                            SE.ProgressBar((640, 120), (640, 0),
                                           SE.InfoWindow((160, 600), (50, 50),
                                                         SE.HelpWindow((700, 500), pygame.SRCALPHA, (0, 0),
                                                                       SE.ScreenHandle(
                                                                           (0, 0))
                                                                       ))))
    drawer.connect_engine(engine)

    while engine.working:
        if KEYBOARD_CONTROL:
            process_key()
        else:
            bullshit()

        gameDisplay.blit(drawer, (0, 0))
        drawer.draw(gameDisplay)

        pygame.display.update()


if __name__ == "__main__":
    global engine, iteration

    iteration = 0

    pygame.init()
    gameDisplay = pygame.display.set_mode(SCREEN_DIM)
    pygame.display.set_caption(GAME_NAME)

    engine = GameEngine()
    engine.create_game(is_new=True)
    main()
    pygame.display.quit()
    pygame.quit()
    exit(0)
