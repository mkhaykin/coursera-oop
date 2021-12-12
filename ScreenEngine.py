import pygame
import collections

from config import *


class ScreenHandle(pygame.Surface):

    def __init__(self, *args, **kwargs):
        if len(args) > 1:
            self.successor = args[-1]
            self.next_coord = args[-2]
            args = args[:-2]
        else:
            self.successor = None
            self.next_coord = (0, 0)
        super().__init__(*args, **kwargs)
        self.fill(colors["wooden"])

        self.engine = None  # мой код

    def draw(self, canvas):
        if self.successor is not None:
            canvas.blit(self.successor, self.next_coord)
            self.successor.draw(canvas)

    def connect_engine(self, engine):
        self.engine = engine
        if self.successor is not None:
            self.successor.connect_engine(engine=engine)


class GameSurface(ScreenHandle):
    """ игровое поле """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._min_x, self._min_y = 0, 0

    def _calc_min_xy(self):
        """ calculate (min_x,min_y) - left top corner """
        def _calc(screen, field, hero):
            if field > screen:
                # герой должен оказаться в центральной позиции,
                # если только это не создает пустышки по краям
                value = hero - screen // 2
                if value < 0:
                    return 0
                elif hero >= field - screen // 2:
                    return field - screen
                else:
                    return value
            else:
                return 0
        # размер экрана в спрайтах
        screen_x, screen_y = map(lambda n: n // self.engine.sprite_size, self.get_size())
        # размер поля
        field_x, field_y = len(self.engine.map[0]), len(self.engine.map)
        # позиция героя
        hero_x, hero_y = self.engine.hero.position[0], self.engine.hero.position[1]
        return _calc(screen_x, field_x, hero_x), _calc(screen_y, field_y, hero_y)

    def draw_map(self):
        size = self.engine.sprite_size
        min_x, min_y = self._calc_min_xy()

        self.fill(colors["wooden"])
        if self.engine.map:
            for i in range(len(self.engine.map[0]) - min_x):
                for j in range(len(self.engine.map) - min_y):
                    self.blit(self.engine.map[min_y + j][min_x + i][
                              0], (i * size, j * size))
        else:
            self.fill(colors["white"])

    def draw_object(self, sprite, coord):
        size = self.engine.sprite_size
        min_x, min_y = self._calc_min_xy()

        self.blit(sprite, ((coord[0] - min_x) * size,
                           (coord[1] - min_y) * size))

    def draw_objects(self):
        for obj in self.engine.objects:
            self.draw_object(obj.sprite[0], obj.position)

    def draw_hero(self):
        # вряд ли стоит разбивать перерисовку ...
        # self.engine.hero.draw(self)
        # TODO подтяжки (
        if self.engine.hero.position[0] >= len(self.engine.map[0]) or \
                self.engine.hero.position[1] >= len(self.engine.map):
            self.engine.hero.position = (1, 1)

        self.draw_object(self.engine.hero.sprite, self.engine.hero.position)

    def draw(self, canvas):
        self.draw_map()
        self.draw_objects()
        self.draw_hero()
        # draw next surface in chain
        super().draw(canvas)


class ProgressBar(ScreenHandle):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fill(colors["wooden"])

    def draw(self, canvas):
        self.fill(colors["wooden"])
        pygame.draw.rect(self, colors["black"], (50, 30, 200, 30), 2)
        pygame.draw.rect(self, colors["black"], (50, 70, 200, 30), 2)

        pygame.draw.rect(self, colors[
                         "red"], (50, 30, 200 * self.engine.hero.hp / self.engine.hero.max_hp, 30))
        pygame.draw.rect(self, colors["green"], (50, 70,
                                                 200 * self.engine.hero.exp / (100 * (2**(self.engine.hero.level - 1))), 30))

        font = pygame.font.SysFont("comicsansms", 20)
        self.blit(font.render(f'Hero at {self.engine.hero.position}', True, colors["black"]),
                  (250, 0))

        self.blit(font.render(f'{self.engine.level} floor', True, colors["black"]),
                  (10, 0))

        self.blit(font.render(f'HP', True, colors["black"]),
                  (10, 30))
        self.blit(font.render(f'Exp', True, colors["black"]),
                  (10, 70))

        self.blit(font.render(f'{self.engine.hero.hp}/{self.engine.hero.max_hp}', True, colors["black"]),
                  (60, 30))
        self.blit(font.render(f'{self.engine.hero.exp}/{(100*(2**(self.engine.hero.level-1)))}', True, colors["black"]),
                  (60, 70))

        self.blit(font.render(f'Level', True, colors["black"]),
                  (300, 30))
        self.blit(font.render(f'Gold', True, colors["black"]),
                  (300, 70))

        self.blit(font.render(f'{self.engine.hero.level}', True, colors["black"]),
                  (360, 30))
        self.blit(font.render(f'{self.engine.hero.gold}', True, colors["black"]),
                  (360, 70))

        self.blit(font.render(f'Str', True, colors["black"]),
                  (420, 30))
        self.blit(font.render(f'Luck', True, colors["black"]),
                  (420, 70))

        self.blit(font.render(f'{self.engine.hero.stats["strength"]}', True, colors["black"]),
                  (480, 30))
        self.blit(font.render(f'{self.engine.hero.stats["luck"]}', True, colors["black"]),
                  (480, 70))

        self.blit(font.render(f'SCORE', True, colors["black"]),
                  (550, 30))
        self.blit(font.render(f'{self.engine.score:.4f}', True, colors["black"]),
                  (550, 70))

        # draw next surface in chain
        super().draw(canvas=canvas)


class InfoWindow(ScreenHandle):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.len = 30
        clear = []
        self.data = collections.deque(clear, maxlen=self.len)

    def update(self, value):
        self.data.append(f"> {str(value)}")

    def draw(self, canvas):
        self.fill(colors["wooden"])
        size = self.get_size()

        font = pygame.font.SysFont("comicsansms", 10)
        for i, text in enumerate(self.data):
            self.blit(font.render(text, True, colors["black"]),
                      (5, 20 + 18 * i))

        # draw next surface in chain
        super().draw(canvas)

    def connect_engine(self, engine):
        # set this class as Observer to engine and send it to next in
        super().connect_engine(engine)
        engine.subscribe(self)


class HelpWindow(ScreenHandle):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.len = 30
        clear = []
        self.data = collections.deque(clear, maxlen=self.len)
        self.data.append([" →", "Move Right"])
        self.data.append([" ←", "Move Left"])
        self.data.append([" ↑ ", "Move Top"])
        self.data.append([" ↓ ", "Move Bottom"])
        self.data.append([" H ", "Show Help"])
        self.data.append([" G ", "God mode"])
        self.data.append(["Num+", "Zoom +"])
        self.data.append(["Num-", "Zoom -"])
        self.data.append([" R ", "Restart Game"])

    def draw(self, canvas):
        alpha = 0
        if self.engine.show_help:
            alpha = 128
        self.fill((0, 0, 0, alpha))
        font1 = pygame.font.SysFont("courier", 24)
        font2 = pygame.font.SysFont("serif", 24)
        if self.engine.show_help:
            pygame.draw.lines(self, (255, 0, 0, 255), True, [
                              (0, 0), (700, 0), (700, 500), (0, 500)], 5)
            for i, text in enumerate(self.data):
                self.blit(font1.render(text[0], True, ((128, 128, 255))),
                          (50, 50 + 30 * i))
                self.blit(font2.render(text[1], True, ((128, 128, 255))),
                          (150, 50 + 30 * i))

        # draw next surface in chain
        super().draw(canvas)
