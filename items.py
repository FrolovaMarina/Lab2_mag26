import pygame as pg
from appearance import *
from extra import *


class Item(pg.sprite.Sprite):
    def __init__(self, cell_size: int, colour: str, field_name: str, file_name: str):
        super().__init__()
        picture1 = pg.image.load('items/' + colour + file_name)
        picture = picture1.convert_alpha()
        self.image = pg.transform.scale(picture, (cell_size, cell_size))
        self.rect = self.image.get_rect()
        self.field_name = field_name


class Queen1(Item):
    def __init__(self, cell_size: int, colour: str, field: str):
        super().__init__(cell_size, colour, field, '_w.png')
        Queen1.icolour = WHITE


class Queen2(Item):
    def __init__(self, cell_size: int, colour: str, field: str):
        super().__init__(cell_size, colour, field, '_b.png')
        Queen2.icolour = BLACK


class Checker1(Item):
    def __init__(self, cell_size: int, icolour: str, field: str):
        super().__init__(cell_size, icolour, field, '_w.png')
        Checker1.icolour = WHITE


class Checker2(Item):
    def __init__(self, cell_size: int, icolour: str, field: str):
        super().__init__(cell_size, icolour, field, '_b.png')
        Checker2.icolour = BLACK
