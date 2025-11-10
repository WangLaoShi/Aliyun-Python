#! /usr/bin/env python
# -*- coding: utf-8 -*-

import os
import pygame


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

pygame.init()  # 游戏初始化
pygame.mixer.init()  # 混音器初始化

# 游戏背景音乐
pygame.mixer.music.load(os.path.join(BASE_DIR, "material/sound/game_music.wav"))
pygame.mixer.music.set_volume(0.2)

# 子弹发射音乐
bullet_sound = pygame.mixer.Sound(os.path.join(BASE_DIR, "material/sound/bullet.wav"))
bullet_sound.set_volume(0.2)

# 我方飞机挂了的音乐
me_down_sound = pygame.mixer.Sound(os.path.join(BASE_DIR, "material/sound/game_over.wav"))
me_down_sound.set_volume(0.2)

# 敌方飞机挂了的音乐
enemy1_down_sound = pygame.mixer.Sound(os.path.join(BASE_DIR, "material/sound/enemy1_down.wav"))
enemy1_down_sound.set_volume(0.2)

enemy2_down_sound = pygame.mixer.Sound(os.path.join(BASE_DIR, "material/sound/enemy2_down.wav"))
enemy2_down_sound.set_volume(0.2)

enemy3_down_sound = pygame.mixer.Sound(os.path.join(BASE_DIR, "material/sound/enemy3_down.wav"))
enemy3_down_sound.set_volume(0.2)

button_down_sound = pygame.mixer.Sound(os.path.join(BASE_DIR, "material/sound/button.wav"))
button_down_sound.set_volume(0.2)

level_up_sound = pygame.mixer.Sound(os.path.join(BASE_DIR, "material/sound/achievement.wav"))
level_up_sound.set_volume(0.2)

bomb_sound = pygame.mixer.Sound(os.path.join(BASE_DIR, "material/sound/use_bomb.wav"))
bomb_sound.set_volume(0.2)

get_bomb_sound = pygame.mixer.Sound(os.path.join(BASE_DIR, "material/sound/get_bomb.wav"))
get_bomb_sound.set_volume(0.2)

get_bullet_sound = pygame.mixer.Sound(os.path.join(BASE_DIR, "material/sound/get_double_laser.wav"))
get_bullet_sound.set_volume(0.2)

big_enemy_flying_sound = pygame.mixer.Sound(os.path.join(BASE_DIR, "material/sound/big_spaceship_flying.wav"))
big_enemy_flying_sound.set_volume(0.2)

