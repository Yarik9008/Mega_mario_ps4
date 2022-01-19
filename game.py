import os
import sys
import pygame
from config import *
from pygame_logger import Mario_Logging as login
import json

try:
    pygame.init()
    pygame.key.set_repeat(200, 70)
    pygame.display.set_caption('Super Mario PS4')
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()

    player = None
    coins = 0
    all_coins = 0
    joy_control = True
    all_sprites = pygame.sprite.Group()
    wall_tiles_group = pygame.sprite.Group()
    empty_tiles_group = pygame.sprite.Group()
    player_group = pygame.sprite.Group()
    coins_group = pygame.sprite.Group()
    victory_group = pygame.sprite.Group()
except Exception as err:
    login.critical(login(), err)


def init_controller():
    global joystick, button_keys, analog_keys, joy_control
    # инициализация джойстика
    try:
        joysticks = []
        for i in range(pygame.joystick.get_count()):
            joysticks.append(pygame.joystick.Joystick(i))
        for joystick in joysticks:
            joystick.init()
        # подгрузка конфига джойстика
        with open(os.path.join("ps4_keys.json"), 'r+') as file:
            button_keys = json.load(file)
        if not joysticks:
            joy_control = False
        # 0: Left analog horizonal, 1: Left Analog Vertical, 2: Right Analog Horizontal
        # 3: Right Analog Vertical 4: Left Trigger, 5: Right Trigger
        analog_keys = {0: 0, 1: 0, 2: 0, 3: 0, 4: -1, 5: -1}
    except Exception as err:
        login.critical(login(), err)


def load_image(name, color_key=None):
    try:
        fullname = os.path.join('data', name)
        try:
            image = pygame.image.load(fullname)
        except pygame.error as message:
            print('Cannot load image:', name)
            raise SystemExit(message)
        if color_key is not None:
            image.convert()
            if color_key == -1:
                color_key = image.get_at((0, 0))
            image.set_colorkey(color_key)
        else:
            image = image.convert_alpha()
        return image
    except Exception as err:
        login.critical(login(), err)


def generate_level(filename):
    global all_coins
    try:
        filename = "data/levels/" + filename
        with open(filename, 'r') as mapFile:
            level_map = [line.strip() for line in mapFile]
            all_coins = 0
            for string in level_map:
                all_coins += list(string).count('*')
        max_width = max(map(len, level_map))
        level = list(map(lambda x: x.ljust(max_width, '.'), level_map))
        new_player, x, y = None, None, None
        for y in range(len(level)):
            for x in range(len(level[y])):
                if level[y][x] == '.':
                    EmptyTile('empty', x, y)
                elif level[y][x] == '#':
                    WallTile('wall', x, y)
                elif level[y][x] == '@':
                    EmptyTile('empty', x, y)
                    new_player = Mario(x, y)
                elif level[y][x] == '*':
                    Coin('coin', x, y)
                elif level[y][x] == '?':
                    VictoryTile('v_block', x, y)
        # вернем игрока, а также размер поля в клетках
        return new_player, x, y
    except Exception as err:
        login.critical(login(), err)


def terminate():
    try:
        pygame.quit()
        sys.exit()
    except Exception as err:
        login.critical(login(), err)


def start_screen():
    try:
        intro_text = ["SUPER MARIO PS4", "", "", "", "", "", "",
                      "Правила игры:",
                      "Управление персонажем осуществляется",
                      "посредством стрелочек/грибка.",
                      "Esc - выход из игры.",
                      "",
                      "Нажмите пробел"]

        background = pygame.transform.scale(load_image('background.png'), (WIDTH, HEIGHT))
        screen.blit(background, (0, 0))
        font = pygame.font.Font(None, 40)
        text_coord = 50
        for i in range(len(intro_text)):
            string_rendered = font.render(intro_text[i], 1, pygame.Color(0, 0, 0))
            intro_rect = string_rendered.get_rect()
            text_coord += 10
            intro_rect.top = text_coord
            intro_rect.x = 400 - intro_rect.width // 2
            text_coord += intro_rect.height
            screen.blit(string_rendered, intro_rect)

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    terminate()
                elif event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                    return  # начинаем игру
                elif event.type == pygame.JOYBUTTONDOWN:
                    if event.button == button_keys['left_arrow']:
                        return
            pygame.display.flip()
            clock.tick(FPS)
    except Exception as err:
        login.critical(login(), err)


def end_screen():
    global coins, all_coins
    try:
        intro_text = [f"Coins: {coins}/{all_coins}"]
        background = pygame.transform.scale(load_image('victory_screen.jpg'), (WIDTH, HEIGHT))
        screen.blit(background, (0, 0))
        font = pygame.font.Font(None, 40)
        text_coord = 50
        for i in range(len(intro_text)):
            string_rendered = font.render(intro_text[i], 1, pygame.Color(0, 0, 0))
            intro_rect = string_rendered.get_rect()
            text_coord += 10
            intro_rect.top = text_coord
            intro_rect.x = 400 - intro_rect.width // 2
            text_coord += intro_rect.height
            screen.blit(string_rendered, intro_rect)

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    terminate()
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    return
            pygame.display.flip()
            clock.tick(FPS)
    except Exception as err:
        login.critical(login(), err)


try:
    tile_images = {
        'wall': load_image('box.png'),
        'empty': load_image('grass.png'),
        'coin': load_image('coin.png'),
        'v_block': load_image('v_block.png')
    }
    player_image = load_image('mar.png')
    tile_width = tile_height = 50
except Exception as err:
    login.critical(login(), err)


class WallTile(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        try:
            super().__init__(wall_tiles_group, all_sprites)
            self.image = tile_images[tile_type]
            self.rect = self.image.get_rect().move(tile_width * pos_x, tile_height * pos_y)
        except Exception as err:
            login.critical(login(), err)


class EmptyTile(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        try:
            super().__init__(empty_tiles_group, all_sprites)
            self.image = tile_images[tile_type]
            self.rect = self.image.get_rect().move(tile_width * pos_x, tile_height * pos_y)
        except Exception as err:
            login.critical(login(), err)


class Coin(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        try:
            super().__init__(coins_group, all_sprites)
            self.image = tile_images[tile_type]
            self.rect = self.image.get_rect().move(tile_width * pos_x, tile_height * pos_y)
            self.taken = False
        except Exception as err:
            login.critical(login(), err)


class VictoryTile(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        try:
            super().__init__(victory_group, all_sprites)
            self.image = tile_images[tile_type]
            self.rect = self.image.get_rect().move(tile_width * pos_x, tile_height * pos_y)
        except Exception as err:
            login.critical(login(), err)


class Mario(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        try:
            super().__init__(player_group, all_sprites)
            self.image = player_image
            self.rect = self.image.get_rect().move(
                tile_width * pos_x + 15, tile_height * pos_y + 5)
        except Exception as err:
            login.critical(login(), err)

    def move(self, axys, sign, step):
        try:
            if axys == 'x':
                if sign == '+':
                    self.rect.x += step
                    if pygame.sprite.spritecollideany(self, wall_tiles_group):
                        self.rect.x -= step
                else:
                    self.rect.x -= step
                    if pygame.sprite.spritecollideany(self, wall_tiles_group):
                        self.rect.x += step
            else:
                if sign == '+':
                    self.rect.y += step
                    if pygame.sprite.spritecollideany(self, wall_tiles_group):
                        self.rect.y -= step
                else:
                    self.rect.y -= step
                    if pygame.sprite.spritecollideany(self, wall_tiles_group):
                        self.rect.y += step
        except Exception as err:
            login.critical(login(), err)


class Camera:
    # зададим начальный сдвиг камеры и размер поля для возможности реализации циклического сдвига
    def __init__(self, field_size):
        self.dx = 0
        self.dy = 0
        self.field_size = field_size

    # сдвинуть объект obj на смещение камеры
    def apply(self, obj):
        try:
            obj.rect.x += self.dx
            # вычислим координату клетки, если она уехала влево за границу экрана
            if obj.rect.x < -obj.rect.width:
                obj.rect.x += (self.field_size[0] + 1) * obj.rect.width
            # вычислим координату клетки, если она уехала вправо за границу экрана
            if obj.rect.x >= (self.field_size[0]) * obj.rect.width:
                obj.rect.x += -obj.rect.width * (1 + self.field_size[0])
            obj.rect.y += self.dy
            # вычислим координату клетки, если она уехала вверх за границу экрана
            if obj.rect.y < -obj.rect.height:
                obj.rect.y += (self.field_size[1] + 1) * obj.rect.height
            # вычислим координату клетки, если она уехала вниз за границу экрана
            if obj.rect.y >= (self.field_size[1]) * obj.rect.height:
                obj.rect.y += -obj.rect.height * (1 + self.field_size[1])
        except Exception as err:
            login.critical(login(), err)

    # позиционировать камеру на объекте target
    def update(self, target):
        try:
            self.dx = -(target.rect.x + target.rect.w // 2 - WIDTH // 2)
            self.dy = -(target.rect.y + target.rect.h // 2 - HEIGHT // 2)
        except Exception as err:
            login.critical(login(), err)


start_screen()
def main_game_ps4():
    global running, player, camera, all_sprites, screen, wall_tiles_group, empty_tiles_group, player_group, clock, coins
    try:
        step = 10
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    terminate()
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE or\
                        pygame.sprite.spritecollideany(player, victory_group):
                    running = False
                if event.type == pygame.KEYDOWN:
                    ############### UPDATE SPRITE IF SPACE IS PRESSED #################################
                    pass

                # HANDLES BUTTON PRESSES
                if event.type == pygame.JOYBUTTONDOWN:
                    if event.button == button_keys['left_arrow']:
                        LEFT = True
                        player.move('x', '-', step)
                    if event.button == button_keys['right_arrow']:
                        RIGHT = True
                        player.move('x', '+', step)
                    if event.button == button_keys['down_arrow']:
                        DOWN = True
                        player.move('y', '+', step)
                    if event.button == button_keys['up_arrow']:
                        UP = True
                        player.move('y', '-', step)
                # HANDLES BUTTON RELEASES
                if event.type == pygame.JOYBUTTONUP:
                    if event.button == button_keys['left_arrow']:
                        LEFT = False
                    if event.button == button_keys['right_arrow']:
                        RIGHT = False
                    if event.button == button_keys['down_arrow']:
                        DOWN = False
                    if event.button == button_keys['up_arrow']:
                        UP = False

                #HANDLES ANALOG INPUTS
                if event.type == pygame.JOYAXISMOTION:
                    analog_keys[event.axis] = event.value
                    # Horizontal Analog
                    if abs(analog_keys[0]) > .4:
                        if analog_keys[0] < -.7:
                            LEFT = True
                            player.move('x', '-', 1)
                        else:
                            LEFT = False
                        if analog_keys[0] > .7:
                            RIGHT = True
                            player.move('x', '+', 1)
                        else:
                            RIGHT = False
                    # Vertical Analog
                    if abs(analog_keys[1]) > .4:
                        if analog_keys[1] < -.7:
                            UP = True
                            player.move('y', '-', 1)
                        else:
                            UP = False
                        if analog_keys[1] > .7:
                            DOWN = True
                            player.move('y', '+', 1)
                        else:
                            DOWN = False
                        # Triggers
            camera.update(player)
            for sprite in all_sprites:
                camera.apply(sprite)
            for c in coins_group:
                if player.rect.colliderect(c.rect):
                    c.taken = True
                    c.image = tile_images['empty']
            k = 0
            for c in coins_group:
                if c.taken:
                    k += 1
            coins = k
            screen.fill(pygame.Color(0, 0, 0))
            wall_tiles_group.draw(screen)
            empty_tiles_group.draw(screen)
            coins_group.draw(screen)
            victory_group.draw(screen)
            player_group.draw(screen)
            pygame.display.flip()
            clock.tick(FPS)
    except Exception as err:
        login.critical(login(), err)


def main_game_key():
    global running, player, camera, all_sprites, screen, wall_tiles_group, empty_tiles_group, player_group, clock, coins
    try:
        step = 10
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    terminate()
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE or\
                        pygame.sprite.spritecollideany(player, victory_group):
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT:
                        player.move('x', '-', step)
                    if event.key == pygame.K_RIGHT:
                        player.move('x', '+', step)
                    if event.key == pygame.K_UP:
                        player.move('y', '-', step)
                    if event.key == pygame.K_DOWN:
                        player.move('y', '+', step)
            camera.update(player)
            for sprite in all_sprites:
                camera.apply(sprite)
            for c in coins_group:
                if player.rect.colliderect(c.rect):
                    c.taken = True
                    c.image = tile_images['empty']
            k = 0
            for c in coins_group:
                if c.taken:
                    k += 1
            coins = k
            screen.fill(pygame.Color(0, 0, 0))
            wall_tiles_group.draw(screen)
            empty_tiles_group.draw(screen)
            coins_group.draw(screen)
            victory_group.draw(screen)
            player_group.draw(screen)
            pygame.display.flip()
            clock.tick(FPS)
    except Exception as err:
        login.critical(login(), err)


try:
    init_controller()
    player, level_x, level_y = generate_level("level_1.txt")
    camera = Camera((level_x, level_y))
    running = True
    if joy_control:
        main_game_ps4()
    else:
        main_game_key()
    all_sprites = pygame.sprite.Group()
    wall_tiles_group = pygame.sprite.Group()
    empty_tiles_group = pygame.sprite.Group()
    player_group = pygame.sprite.Group()
    coins_group = pygame.sprite.Group()
    victory_group = pygame.sprite.Group()
    player, level_x, level_y = generate_level("level_2.txt")
    camera = Camera((level_x, level_y))
    running = True
    if joy_control:
        main_game_ps4()
    else:
        main_game_key()
    all_sprites = pygame.sprite.Group()
    wall_tiles_group = pygame.sprite.Group()
    empty_tiles_group = pygame.sprite.Group()
    player_group = pygame.sprite.Group()
    coins_group = pygame.sprite.Group()
    victory_group = pygame.sprite.Group()
    player, level_x, level_y = generate_level("level_3.txt")
    camera = Camera((level_x, level_y))
    running = True
    if joy_control:
        main_game_ps4()
    else:
        main_game_key()
    all_sprites = pygame.sprite.Group()
    wall_tiles_group = pygame.sprite.Group()
    empty_tiles_group = pygame.sprite.Group()
    player_group = pygame.sprite.Group()
    coins_group = pygame.sprite.Group()
    victory_group = pygame.sprite.Group()
    player, level_x, level_y = generate_level("level_4.txt")
    camera = Camera((level_x, level_y))
    running = True
    if joy_control:
        main_game_ps4()
    else:
        main_game_key()
    all_sprites = pygame.sprite.Group()
    wall_tiles_group = pygame.sprite.Group()
    empty_tiles_group = pygame.sprite.Group()
    player_group = pygame.sprite.Group()
    coins_group = pygame.sprite.Group()
    victory_group = pygame.sprite.Group()
    player, level_x, level_y = generate_level("level_5.txt")
    camera = Camera((level_x, level_y))
    running = True
    if joy_control:
        main_game_ps4()
    else:
        main_game_key()
    end_screen()
except Exception as err:
    login.critical(login(), err)

terminate()
