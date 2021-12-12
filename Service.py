import pygame
import random
import yaml
from abc import ABC

from config import *
import Objects


# TODO  ScreenEngine
def create_sprite(img, sprite_size):
    icon = pygame.image.load(img).convert_alpha()
    icon = pygame.transform.scale(icon, (sprite_size, sprite_size))
    sprite = pygame.Surface((sprite_size, sprite_size), pygame.HWSURFACE)
    sprite.blit(icon, (0, 0))
    return sprite


# TODO В Logic
def reload_game(engine, hero):
    # это в общем не релоад, а просто загрузка уровня для отображения
    # стоит переписать
    # TODO глобальная ... ппц (
    global level_list, generator
    level_list_max = len(level_list) - 1
    engine.level += 1
    engine.objects = []
    generator = level_list[min(engine.level, level_list_max)]
    _map = generator['map'].get_map()
    engine.load_map(_map)
    engine.add_objects(generator['obj'].get_objects(_map))

    # hero.position = [1, 1]
    # размещаем случайным образом
    hero.position = get_free_random_pos(engine.map, engine.objects)
    engine.add_hero(hero)


# TODO по хорошему все обработчики эффектов в объекты. Ну или в logic
def restore_hp(engine, hero):
    engine.score += 0.1
    hero.set_max_hp()
    engine.notify("HP restored")


def apply_berserk(engine, hero):
    engine.score += 0.2
    engine.hero = Objects.Berserk(hero)
    engine.notify("Berserk applied")


def apply_blessing(engine, hero):
    engine.score += 0.2
    engine.hero = Objects.Blessing(hero)
    engine.notify("Blessing applied")


def apply_weakness(engine, hero):
    engine.score += 0.2
    engine.hero = Objects.Weakness(hero)
    engine.notify("Weakness applied")


def apply_luck(engine, hero):
    engine.score += 0.2
    engine.hero = Objects.Luck(hero)
    engine.notify("Lucky applied")


def apply_random(engine, hero):
    engine.score += 0.2
    effects = [apply_blessing, apply_luck, apply_weakness, apply_blessing, apply_berserk]
    # повысим шансы на боевые ;)
    effects.extend([apply_blessing, apply_berserk] * 2)
    engine.notify("Select effect: ...")
    random.choice(effects)(engine, hero)


def remove_effect(engine, hero):
    if hero.base:
        engine.hero = hero.base
        engine.hero.set_max_hp()
        engine.notify("Effect removed")
    else:
        engine.notify("No effect")


def add_gold(engine, hero):
    if random.randint(1, 10) == 1:
        engine.score -= 0.05
        engine.hero = Objects.Weakness(hero)
        engine.notify("You were cursed")
    else:
        engine.score += 0.1
        gold = int(random.randint(10, 1000) * (1.1**(engine.hero.level - 1)))
        hero.gold += gold
        engine.notify(f"{gold} gold added")


# TODO в карты
def get_free_random_pos(_map, _object):
    """ получить свободные координаты по карте и уже размещенным объектам"""
    lim_x, lim_y = len(_map[0]) - 2, len(_map) - 2
    position = (random.randint(1, lim_x), random.randint(1, lim_y))
    # делаем список занятых позиций
    busy = []
    for y in range(1, lim_y):
        for x in range(1, lim_x):
            if _map[y][x] == wall:
                busy.append((x, y))

    busy.extend([obj.position for obj in _object if obj.position])

    assert len(busy) == len(list(set(busy))), "совпадение объектов по координатам"

    count = 0
    while position in busy:
        position = (random.randint(1, lim_x), random.randint(1, lim_y))
        count += 1
        if count > 10:
            raise Exception('не возможно найти свободную позицию.')
    return position


class MapFactory(yaml.YAMLObject):

    @classmethod
    def from_yaml(cls, loader, node):
        _map = cls.Map()
        _obj = cls.Objects()
        _enemy = {}
        for item in node.value:
            _enemy[item[0].value] = int(item[1].value)
        return {'map': _map, 'obj': _obj, 'enemy': _enemy}

    @classmethod
    def get_map(cls):
        return cls.Map()

    @classmethod
    def get_objects(cls):
        return cls.Objects()

    class Map(ABC):
        pass

    class Objects(ABC):
        pass


class EndMap(MapFactory):
    yaml_tag = "!end_map"

    class Map:
        def __init__(self):
            self.Map = MAP_FINISH
            self.Map = list(map(list, self.Map))
            for i in self.Map:
                for j in range(len(i)):
                    i[j] = wall if i[j] == '0' else floor1
         
        def get_map(self):
            return self.Map

    class Objects:
        def __init__(self):
            self.objects = []

        def get_objects(self, _map):
            return self.objects


class RandomMap(MapFactory):
    yaml_tag = "!random_map"

    class Map:

        def __init__(self):
            self.Map = [[0 for _ in range(RANDOM_MAP_SIZE_X)] for _ in range(RANDOM_MAP_SIZE_Y)]
            for i in range(RANDOM_MAP_SIZE_X):
                for j in range(RANDOM_MAP_SIZE_Y):
                    if i == 0 or j == 0 or i == RANDOM_MAP_SIZE_X - 1 or j == RANDOM_MAP_SIZE_Y - 1:
                        self.Map[j][i] = wall
                    else:
                        self.Map[j][i] = [wall, floor1, floor2, floor3, floor1,
                                          floor2, floor3, floor1, floor2][random.randint(0, 8)]

        def get_map(self):
            return self.Map

    class Objects:

        def __init__(self):
            self.objects = []

        def get_objects(self, _map):

            for obj_name in object_list_prob['objects']:
                prop = object_list_prob['objects'][obj_name]
                for i in range(random.randint(prop['min-count'], prop['max-count'])):
                    coord = get_free_random_pos(_map, self.objects)
                    self.objects.append(Objects.Ally(
                        prop['sprite'], prop['action'], coord))

            for obj_name in object_list_prob['ally']:
                prop = object_list_prob['ally'][obj_name]
                for i in range(random.randint(prop['min-count'], prop['max-count'])):
                    coord = get_free_random_pos(_map, self.objects)
                    self.objects.append(Objects.Ally(
                        prop['sprite'], prop['action'], coord))

            for obj_name in object_list_prob['enemies']:
                prop = object_list_prob['enemies'][obj_name]
                for i in range(random.randint(1, 5)):
                    coord = get_free_random_pos(_map, self.objects)
                    self.objects.append(Objects.Enemy(
                        prop['sprite'], prop, coord))

            return self.objects


class EmptyMap(RandomMap):
    yaml_tag = "!empty_map"

    class Map:

        def __init__(self):
            size_x = len(MAP_EMPTY[0])
            size_y = len(MAP_EMPTY)
            self.Map = [[floor1 for _ in range(size_x)] for _ in range(size_y)]
            for j in range(size_y):
                for i in range(size_x):
                    if MAP_EMPTY[j][i] == 'X':
                        self.Map[j][i] = wall

        def get_map(self):
            return self.Map

    class Objects:

        def __init__(self):
            self.objects = []

        def get_objects(self, _map):

            for obj_name in object_list_prob['objects']:
                prop = object_list_prob['objects'][obj_name]
                for i in range(random.randint(prop['min-count'], prop['max-count'])):
                    coord = get_free_random_pos(_map, self.objects)
                    self.objects.append(Objects.Ally(
                        prop['sprite'], prop['action'], coord))

            for obj_name in object_list_prob['ally']:
                prop = object_list_prob['ally'][obj_name]
                for i in range(random.randint(prop['min-count'], prop['max-count'])):
                    coord = get_free_random_pos(_map, self.objects)
                    self.objects.append(Objects.Ally(
                        prop['sprite'], prop['action'], coord))

            return self.objects


class SpecialMap(RandomMap):
    yaml_tag = "!special_map"

    class Map:

        def __init__(self):
            size_x = len(MAP_SPECIAL[0])
            size_y = len(MAP_SPECIAL)
            self.Map = [[floor1 for _ in range(size_x)] for _ in range(size_y)]
            for j in range(size_y):
                for i in range(size_x):
                    if MAP_SPECIAL[j][i] == 'X':
                        self.Map[j][i] = wall

        def get_map(self):
            return self.Map

    class Objects:

        def __init__(self):
            self.objects = []

        def get_objects(self, _map):
            # TODO пришлось чтобы иметь доступ ограничениям монстров
            global generator

            for obj_name in object_list_prob['objects']:
                prop = object_list_prob['objects'][obj_name]
                for i in range(random.randint(prop['min-count'], prop['max-count'])):
                    coord = get_free_random_pos(_map, self.objects)
                    self.objects.append(Objects.Ally(
                        prop['sprite'], prop['action'], coord))

            for obj_name in object_list_prob['ally']:
                prop = object_list_prob['ally'][obj_name]
                for i in range(random.randint(prop['min-count'], prop['max-count'])):
                    coord = get_free_random_pos(_map, self.objects)
                    self.objects.append(Objects.Ally(
                        prop['sprite'], prop['action'], coord))

            # enemy только из списка map
            enemy_list = generator['enemy']
            for obj_name in object_list_prob['enemies']:
                prop = object_list_prob['enemies'][obj_name]
                if obj_name in enemy_list.keys():
                    for _ in range(enemy_list[obj_name]):
                        coord = get_free_random_pos(_map, self.objects)
                        self.objects.append(Objects.Enemy(
                            prop['sprite'], prop, coord))

            return self.objects


# TODO глобальные ... фу так делать
wall = [0]
floor1 = [0]
floor2 = [0]
floor3 = [0]


def service_init(sprite_size, full=True):
    global object_list_prob, level_list

    global wall
    global floor1
    global floor2
    global floor3

    wall[0] = create_sprite(os.path.join("texture", "wall.png"), sprite_size)
    floor1[0] = create_sprite(os.path.join("texture", "Ground_1.png"), sprite_size)
    floor2[0] = create_sprite(os.path.join("texture", "Ground_2.png"), sprite_size)
    floor3[0] = create_sprite(os.path.join("texture", "Ground_3.png"), sprite_size)

    file = open("objects.yml", "r")

    object_list_tmp = yaml.load(file.read(), yaml.FullLoader)
    if full:
        object_list_prob = object_list_tmp

    object_list_actions = {'reload_game': reload_game,
                           'add_gold': add_gold,
                           'remove_effect': remove_effect,
                           'restore_hp': restore_hp,
                           'apply_berserk': apply_berserk,
                           'apply_blessing': apply_blessing,
                           'apply_weakness': apply_weakness,
                           'apply_luck': apply_luck,
                           'apply_random': apply_random
                           }

    for obj in object_list_prob['objects']:
        prop = object_list_prob['objects'][obj]
        prop_tmp = object_list_tmp['objects'][obj]
        prop['sprite'][0] = create_sprite(
            os.path.join(OBJECT_TEXTURE, prop_tmp['sprite'][0]), sprite_size)
        prop['action'] = object_list_actions[prop_tmp['action']]

    for ally in object_list_prob['ally']:
        prop = object_list_prob['ally'][ally]
        prop_tmp = object_list_tmp['ally'][ally]
        prop['sprite'][0] = create_sprite(
            os.path.join(ALLY_TEXTURE, prop_tmp['sprite'][0]), sprite_size)
        prop['action'] = object_list_actions[prop_tmp['action']]

    for enemy in object_list_prob['enemies']:
        prop = object_list_prob['enemies'][enemy]
        prop_tmp = object_list_tmp['enemies'][enemy]
        prop['sprite'][0] = create_sprite(
            os.path.join(ENEMY_TEXTURE, prop_tmp['sprite'][0]), sprite_size)

    file.close()

    if full:
        # загружаем уровни
        # TODO переделать на with
        file = open("levels.yml", "r")
        level_list = yaml.load(file.read(), yaml.FullLoader)['levels']
        # добавляем финальный
        level_list.append({'map': EndMap.Map(), 'obj': EndMap.Objects(), 'enemy': dict()})
        file.close()
