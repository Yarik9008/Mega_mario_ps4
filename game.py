import os
import sys
import pygame
from config import *
import pygame_logger
import json

pygame.init()
pygame.key.set_repeat(200, 70)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

player = None
all_sprites = pygame.sprite.Group()
walltiles_group = pygame.sprite.Group()
emptytiles_group = pygame.sprite.Group()
player_group = pygame.sprite.Group()


def init_controller():
    global joystick, button_keys, analog_keys
    # инициализация джойстика
    joysticks = []
    for i in range(pygame.joystick.get_count()):
        joysticks.append(pygame.joystick.Joystick(i))
    for joystick in joysticks:
        joystick.init()
    # подгрузка конфига джойстика
    with open(os.path.join("ps4_keys.json"), 'r+') as file:
        button_keys = json.load(file)
    # 0: Left analog horizonal, 1: Left Analog Vertical, 2: Right Analog Horizontal
    # 3: Right Analog Vertical 4: Left Trigger, 5: Right Trigger
    analog_keys = {0: 0, 1: 0, 2: 0, 3: 0, 4: -1, 5: -1}


def load_image(name, color_key=None):
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


def load_level(filename):
    filename = "data/" + filename
    # читаем уровень, убирая символы перевода строки
    with open(filename, 'r') as mapFile:
        level_map = [line.strip() for line in mapFile]

    # и подсчитываем максимальную длину
    max_width = max(map(len, level_map))

    # дополняем каждую строку пустыми клетками ('.')
    return list(map(lambda x: x.ljust(max_width, '.'), level_map))


def generate_level(level):
    new_player, x, y = None, None, None
    for y in range(len(level)):
        for x in range(len(level[y])):
            if level[y][x] == '.':
                EmptyTile('empty', x, y)
            elif level[y][x] == '#':
                WallTile('wall', x, y)
            elif level[y][x] == '@':
                EmptyTile('empty', x, y)
                new_player = Player(x, y)
    # вернем игрока, а также размер поля в клетках
    return new_player, x, y


def terminate():
    pygame.quit()
    sys.exit()


def start_screen():
    intro_text = ["ЗАСТАВКА", "",
                  "Правила игры",
                  "Если в правилах несколько строк,",
                  "приходится выводить их построчно"]

    fon = pygame.transform.scale(load_image('fon.jpg'), (WIDTH, HEIGHT))
    screen.blit(fon, (0, 0))
    font = pygame.font.Font(None, 30)
    text_coord = 50
    for line in intro_text:
        string_rendered = font.render(line, 1, pygame.Color('black'))
        intro_rect = string_rendered.get_rect()
        text_coord += 10
        intro_rect.top = text_coord
        intro_rect.x = 10
        text_coord += intro_rect.height
        screen.blit(string_rendered, intro_rect)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                return  # начинаем игру
        pygame.display.flip()
        clock.tick(FPS)


tile_images = {'wall': load_image('box.png'), 'empty': load_image('grass.png')}
player_image = load_image('mar.png')

tile_width = tile_height = 50


class WallTile(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__(walltiles_group, all_sprites)
        self.image = tile_images[tile_type]
        self.rect = self.image.get_rect().move(tile_width * pos_x, tile_height * pos_y)


class EmptyTile(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__(emptytiles_group, all_sprites)
        self.image = tile_images[tile_type]
        self.rect = self.image.get_rect().move(tile_width * pos_x, tile_height * pos_y)


class Player(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(player_group, all_sprites)
        self.image = player_image
        self.rect = self.image.get_rect().move(
            tile_width * pos_x + 15, tile_height * pos_y + 5)

    def move(self, axys, sign):
        if axys == 'x':
            if sign == '+':
                self.rect.x += STEP
                if pygame.sprite.spritecollideany(self, walltiles_group):
                    self.rect.x -= STEP
            else:
                self.rect.x -= STEP
                if pygame.sprite.spritecollideany(self, walltiles_group):
                    self.rect.x += STEP
        else:
            if sign == '+':
                self.rect.y += STEP
                if pygame.sprite.spritecollideany(self, walltiles_group):
                    self.rect.y -= STEP
            else:
                self.rect.y -= STEP
                if pygame.sprite.spritecollideany(self, walltiles_group):
                    self.rect.y += STEP


class Camera:
    # зададим начальный сдвиг камеры и размер поля для возможности реализации циклического сдвига
    def __init__(self, field_size):
        self.dx = 0
        self.dy = 0
        self.field_size = field_size

    # сдвинуть объект obj на смещение камеры
    def apply(self, obj):
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

    # позиционировать камеру на объекте target
    def update(self, target):
        self.dx = -(target.rect.x + target.rect.w // 2 - WIDTH // 2)
        self.dy = -(target.rect.y + target.rect.h // 2 - HEIGHT // 2)


start_screen()

player, level_x, level_y = generate_level(load_level("levelex.txt"))
camera = Camera((level_x, level_y))

running = True

def main_game_ps4():
    global running, player, camera, all_sprites, screen, walltiles_group, emptytiles_group, player_group, clock
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                ############### UPDATE SPRITE IF SPACE IS PRESSED #################################
                pass

            # HANDLES BUTTON PRESSES
            if event.type == pygame.JOYBUTTONDOWN:
                if event.button == button_keys['left_arrow']:
                    LEFT = True
                if event.button == button_keys['right_arrow']:
                    RIGHT = True
                if event.button == button_keys['down_arrow']:
                    DOWN = True
                if event.button == button_keys['up_arrow']:
                    UP = True
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
                # print(analog_keys)
                # Horizontal Analog
                if abs(analog_keys[0]) > .4:
                    if analog_keys[0] < -.7:
                        LEFT = True
                    else:
                        LEFT = False
                    if analog_keys[0] > .7:
                        RIGHT = True
                    else:
                        RIGHT = False
                # Vertical Analog
                if abs(analog_keys[1]) > .4:
                    if analog_keys[1] < -.7:
                        UP = True
                    else:
                        UP = False
                    if analog_keys[1] > .7:
                        DOWN = True
                    else:
                        DOWN = False
                    # Triggers
                if analog_keys[4] > 0:  # Left trigger
                    color += 2
                if analog_keys[5] > 0:  # Right Trigger
                    color -= 2





def main_game_key():
    global running, player, camera, all_sprites, screen, walltiles_group, emptytiles_group, player_group, clock
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    player.move('x', '-')
                if event.key == pygame.K_RIGHT:
                    player.move('x', '+')
                if event.key == pygame.K_UP:
                    player.move('y', '-')
                if event.key == pygame.K_DOWN:
                    player.move('y', '+')

        camera.update(player)

        for sprite in all_sprites:
            camera.apply(sprite)

        screen.fill(pygame.Color(0, 0, 0))
        walltiles_group.draw(screen)
        emptytiles_group.draw(screen)
        player_group.draw(screen)

        pygame.display.flip()

        clock.tick(FPS)

main_game_key()

terminate()
