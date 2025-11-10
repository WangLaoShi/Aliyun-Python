#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
    子弹的实现
"""

import pygame


class Bullet(pygame.sprite.Sprite):

    def __init__(self, position):
        super(Bullet, self).__init__()
        self.image = pygame.image.load("material/image/bullet1.png")
        self.rect = self.image.get_rect()
        self.rect.left, self.rect.top = position
        self.speed = 30
        self.active = True
        self.mask = pygame.mask.from_surface(self.image)

    def move(self):
        """
        子弹移动, 超出屏幕范围, 则设置死亡
        :return:
        """
        if self.rect.top < 0:
            self.active = False
        else:
            self.rect.top -= self.speed

    def reset(self, position):
        """
        复位函数
        :param position:
        :return:
        """
        self.rect.left, self.rect.top = position
        self.active = True



