import os

SCREEN_DIM = (800, 600)

OBJECT_TEXTURE = os.path.join("texture", "objects")
ENEMY_TEXTURE = os.path.join("texture", "enemies")
ALLY_TEXTURE = os.path.join("texture", "ally")


RANDOM_MAP_SIZE_X = 15  # 41
RANDOM_MAP_SIZE_Y = 11  # 41


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