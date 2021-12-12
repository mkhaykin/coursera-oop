from abc import ABC, abstractmethod
import pygame
import os
import random
import yaml


# TODO дважды скопирован create_sprite ...
def create_sprite(img, sprite_size):
    icon = pygame.image.load(img).convert_alpha()
    icon = pygame.transform.scale(icon, (sprite_size, sprite_size))
    sprite = pygame.Surface((sprite_size, sprite_size), pygame.HWSURFACE)
    sprite.blit(icon, (0, 0))
    return sprite


class Interactive(ABC):
    @abstractmethod
    def interact(self, engine, hero):
        pass


class AbstractObject(ABC):
    """ моя реализация """
    # TODO у меня криво
    @abstractmethod
    def __init__(self, icon, position):
        self.sprite = icon
        self.position = position

    def draw(self, display):
        pass
        # спорное решение: все рисование в sevice.py, а героя сюда запихнули (
        # хз зачем
        # sprite_size = self.sprite.get_size()[0]
        # display.blit(self.sprite, [5 * sprite_size,
        #                            5 * sprite_size])


class Ally(AbstractObject, Interactive):
    def __init__(self, icon, action, position):
        super().__init__(icon, position)
        self.action = action

    def interact(self, engine, hero):
        self.action(engine, hero)


class Creature(AbstractObject):
    def __init__(self, icon, stats, position):
        self.sprite = icon
        self.stats = stats
        self.position = position
        # stats['strength']        # сила
        # stats['endurance']       # выносливость
        # stats['intelligence']    # интеллект
        # stats['luck']            # удача
        # stats['experience']      # опыт
        self.max_hp = self.calc_max_hp()
        self.hp = self.max_hp

    def calc_max_hp(self):
        return 5 + self.stats['endurance'] * 2

    def set_max_hp(self):
        self.max_hp = self.calc_max_hp()
        self.hp = self.max_hp

    def is_alive(self):
        return self.hp > 0

    def set_sprite(self, icon):
        self.sprite = icon


class Enemy(Creature, Interactive):
    def __init__(self, icon, stats, coord):
        super().__init__(icon, stats, coord)

    def interact(self, engine, hero):
        damage = hero.stats["strength"]
        if random.randint(1, 100) < hero.stats["luck"]:
            damage *= 2
            engine.notify(f'you lucky: damage x2')
        self.hp -= damage
        engine.notify(f'the enemy takes {damage} damage')

        if self.hp > 0:
            if not hero.god_mode:
                damage = self.stats["strength"]
                hero.hp -= damage
                engine.notify(f'you takes {damage} damage')
            if not hero.is_alive():
                hero.hp = 0
                sprite_size = engine.sprite_size
                hero.sprite = create_sprite(os.path.join("texture", "hero_rip.png"), sprite_size)
                engine.notify("Ooops ... you die. :(")
        else:
            hero.exp += self.stats["experience"]
            engine.notify("You killed him!")
            # TODO плохо так делать: глобально нужен другой способ передачи сообщений
            hero.level_up(engine=engine)


class Hero(Creature):
    def __init__(self, stats, icon):
        pos = [1, 1]
        self.level = 1
        self.exp = 0
        self.gold = 0
        self.base = None
        # игрок в режиме бога
        self.god_mode = False
        super().__init__(icon, stats, pos)

    # TODO плохо, что герой знает о способе отправки сообщений. переделать.
    def level_up(self, engine=None):
        while self.exp >= 100 * (2 ** (self.level - 1)):
            if engine:
                # отправить сообщение "level up!" для героя.
                engine.notify(f"level up!")
            self.level += 1
            self.stats["strength"] += 2
            self.stats["endurance"] += 2
            self.set_max_hp()
            self.hp = self.max_hp


class Effect(Hero):

    def __init__(self, base):
        self.base = base
        self.stats = self.base.stats.copy()
        self.apply_effect()

    @property
    def god_mode(self):
        return self.base.god_mode

    @god_mode.setter
    def god_mode(self, value):
        self.base.god_mode = value

    @property
    def position(self):
        return self.base.position

    @position.setter
    def position(self, value):
        self.base.position = value

    @property
    def level(self):
        return self.base.level

    @level.setter
    def level(self, value):
        self.base.level = value

    @property
    def gold(self):
        return self.base.gold

    @gold.setter
    def gold(self, value):
        self.base.gold = value

    @property
    def hp(self):
        return self.base.hp

    @hp.setter
    def hp(self, value):
        self.base.hp = value

    @property
    def max_hp(self):
        return self.base.max_hp

    @max_hp.setter
    def max_hp(self, value):
        self.base.max_hp = value

    @property
    def exp(self):
        return self.base.exp

    @exp.setter
    def exp(self, value):
        self.base.exp = value

    @property
    def sprite(self):
        return self.base.sprite

    @sprite.setter
    def sprite(self, value):        # мое
        self.base.sprite = value

    @abstractmethod
    def apply_effect(self):
        pass


class Berserk(Effect):
    def apply_effect(self):
        self.stats["strength"] += 5
        super().apply_effect()


class Blessing(Effect):
    def apply_effect(self):
        self.stats["strength"] += 2
        self.stats["luck"] += 2
        self.stats["intelligence"] += 2
        super().apply_effect()


class Weakness(Effect):
    def apply_effect(self):
        self.stats["strength"] -= 2
        super().apply_effect()


class Luck(Effect):
    def apply_effect(self):
        self.stats["luck"] += 10
        super().apply_effect()
