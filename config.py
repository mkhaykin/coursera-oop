import os

SCREEN_DIM = (800, 600)

OBJECT_TEXTURE = os.path.join("texture", "objects")
ENEMY_TEXTURE = os.path.join("texture", "enemies")
ALLY_TEXTURE = os.path.join("texture", "ally")


RANDOM_MAP_SIZE_X = 30  # 41
RANDOM_MAP_SIZE_Y = 22  # 41


HERO_BASE_STATS = {
    "strength": 20,
    "endurance": 20,
    "intelligence": 5,
    "luck": 5
}

# зачем сделано не понятно.
KEYBOARD_CONTROL = True

GAME_NAME = "MyRPG"
START_SPRITE_SIZE = 40

# важно, должен быть кратен области отображения,
# иначе может прыгать при изменении
SPRITE_STEP = 10
SPRITE_MIN = 1
SPRITE_MAX = 150

colors = {
    "black": (0, 0, 0, 255),
    "white": (255, 255, 255, 255),
    "red": (255, 0, 0, 255),
    "green": (0, 255, 0, 255),
    "blue": (0, 0, 255, 255),
    "wooden": (153, 92, 0, 255),
}

# БЛОК КАРТ
MAP_FINISH = ['000000000000000000000000000000000000000',
              '0                                     0',
              '0                                     0',
              '0  0   0   000   0   0  00000  0   0  0',
              '0  0  0   0   0  0   0  0      0   0  0',
              '0  000    0   0  00000  0000   0   0  0',
              '0  0  0   0   0  0   0  0      0   0  0',
              '0  0   0   000   0   0  00000  00000  0',
              '0                                   0 0',
              '0                                     0',
              '000000000000000000000000000000000000000']