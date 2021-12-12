import os

import Service
import Logic
from Objects import Ally, Enemy, Hero
from config import *


class GameEngine:
    objects = []
    map = None
    hero = None
    level = -1
    working = True
    subscribers = set()
    score = 0.
    game_process = True
    show_help = False

    def __init__(self):
        # на самом деле спрайт надо загнать в ScreenEngine,
        # т.к. он отвечает за отрисовку.
        # Подумать как передавать ему изменения спрайта.
        self._sprite_size = START_SPRITE_SIZE

    def sprite_inc(self):
        if self._sprite_size + SPRITE_STEP <= SPRITE_MAX:
            self._sprite_size += SPRITE_STEP
            self.create_game(self._sprite_size, False)
        else:
            self.notify('sorry ... max size')

    def sprite_dec(self):
        if self._sprite_size - SPRITE_STEP >= SPRITE_MIN:
            self._sprite_size -= SPRITE_STEP
            self.create_game(self._sprite_size, False)
        else:
            self.notify('sorry ... min size')

    @property
    def sprite_size(self):
        return self._sprite_size

    # лучше, чем в service, но надо бы часть в ScreenEngine
    # все что касается размеров и спрайтов,
    # тут только пересоздаем героя.
    def create_game(self, sprite_size=None, is_new=True):
        if sprite_size:
            self._sprite_size = sprite_size
        if is_new:
            # TODO путь до картинок вынести в config
            self.hero = Hero(HERO_BASE_STATS, Service.create_sprite(
                os.path.join("texture", "Hero.png"), self._sprite_size))
            Service.service_init(self._sprite_size)
            Service.reload_game(self, self.hero)
        else:
            # TODO путь до картинок вынести в config
            self.hero.sprite = Service.create_sprite(
                os.path.join("texture", "Hero.png" if self.hero.is_alive() else 'hero_rip.png'), self._sprite_size)
            # TODO вызываем перезагрузку всех объектов, когда надо просто пересчитать спрайты и перерисовать
            #  бредятина.
            Service.service_init(self._sprite_size, False)

    def subscribe(self, obj):
        self.subscribers.add(obj)

    def unsubscribe(self, obj):
        if obj in self.subscribers:
            self.subscribers.remove(obj)

    def notify(self, message):
        for i in self.subscribers:
            i.update(message)

    # HERO
    def add_hero(self, hero):
        self.hero = hero

    def interact(self, position):
        result = True
        # говнокод. каждый раз по всем объектам ... словарь для кого изобрели?
        for obj in self.objects:
            if obj.position == position:    # могут ли 2 врага быть на одной позиции. по коду могут...?
                obj.interact(self, self.hero)
                if isinstance(obj, Ally):
                    self.delete_object(obj)
                elif isinstance(obj, Enemy):
                    if not obj.is_alive():
                        self.delete_object(obj)
                    else:
                        result = False
                else:
                    raise Exception('не предусмотренный объект для interact...')
        return result

    # режим бога ;)
    def god_mode(self):
        self.hero.god_mode = not self.hero.god_mode
        self.notify(f'set god mode: {self.hero.god_mode}')

    # MOVEMENT
    def move(self, diff):
        if self.hero.is_alive():
            self.score -= 0.02
            new_position = (self.hero.position[0] + diff[0], self.hero.position[1] + diff[1])
            if self.map[new_position[1]][new_position[0]] == Service.wall:
                return

            if self.interact(new_position) and self.hero.is_alive():
                self.hero.position = new_position

    def move_up(self):
        self.move((0, -1))

    def move_down(self):
        self.move((0, 1))

    def move_left(self):
        self.move((-1, 0))

    def move_right(self):
        self.move((1, 0))

    # MAP
    def load_map(self, game_map):
        self.map = game_map

    # OBJECTS
    def add_object(self, obj):
        self.objects.append(obj)

    def add_objects(self, objects):
        self.objects.extend(objects)

    def delete_object(self, obj):
        # TODO проблема с выносом объектов иногда ...
        try:
            self.objects.remove(obj)
        except:
            print(obj)
