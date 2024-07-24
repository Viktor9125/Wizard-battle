import pygame as pg
import Constants as cs
import random


class Player(pg.sprite.Sprite):
    def __init__(self, folder='fire wizard', first_player=True):
        super().__init__()

        self.folder = folder
        self.load_animation()

        if first_player:
            self.coord = (100, cs.SCREEN_HEIGHT // 2)
            self.current_animation = self.idle_animation_right
            self.side = 'right'
            self.key_right = pg.K_d
            self.key_left = pg.K_a
            self.key_down = pg.K_s
            self.key_charge = pg.K_SPACE
        else:
            self.coord = (cs.SCREEN_WIDTH - 100, cs.SCREEN_HEIGHT // 2)
            self.current_animation = self.idle_animation_left
            self.side = 'left'
            self.key_right = pg.K_RIGHT
            self.key_left = pg.K_LEFT
            self.key_down = pg.K_DOWN
            self.key_charge = pg.K_RCTRL

        self.hp = 200

        self.image = self.current_animation[0]
        self.current_image = 0

        self.timer = pg.time.get_ticks()
        self.interval = 300
        self.animation_mode = True

        self.direction = 0

        self.rect = self.image.get_rect()
        self.rect.center = self.coord

        self.charge_power = 0
        self.charge_indicator = pg.Surface((self.charge_power, 10))
        self.charge_indicator.fill('red')

        self.charge_mode = False

        self.attack_mode = False
        self.attack_interval = 500

        self.magic_balls = pg.sprite.Group()

    def load_animation(self):
        self.idle_animation_right = []

        for i in range(1, 4):
            self.idle_animation_right.append(
                cs.load_image(f'images/{self.folder}/idle{i}.png', cs.Character_width, cs.Character_height))

        self.idle_animation_left = []

        for image in self.idle_animation_right:
            self.idle_animation_left.append(pg.transform.flip(image, True, False))

        self.walk_animation_right = []

        for i in range(1, 5):
            self.walk_animation_right.append(
                cs.load_image(f'images/{self.folder}/move{i}.png', cs.Character_width, cs.Character_height))

        self.walk_animation_left = []

        for image in self.walk_animation_right:
            self.walk_animation_left.append(pg.transform.flip(image, True, False))

        self.charge = [cs.load_image(f'images/{self.folder}/charge.png', cs.Character_width, cs.Character_height)]
        self.charge.append(pg.transform.flip(self.charge[0], True, False))

        self.attack = [cs.load_image(f'images/{self.folder}/attack.png', cs.Character_width, cs.Character_height)]
        self.attack.append(pg.transform.flip(self.attack[0], True, False))

        self.down = [cs.load_image(f'images/{self.folder}/down.png', cs.Character_width, cs.Character_height)]
        self.down.append(pg.transform.flip(self.down[0], True, False))

    def update(self, player):

        keys = pg.key.get_pressed()

        if keys[self.key_left]:
            self.direction = -1
            self.side = 'left'
        if keys[self.key_right]:
            self.direction = 1
            self.side = 'right'

        self.handle_attack_mode()
        self.handle_movement(self.direction, keys)
        self.handle_animation()

    def handle_attack_mode(self):
        if self.attack_mode:
            if pg.time.get_ticks() - self.timer > self.attack_interval:
                self.attack_mode = False
                self.timer = pg.time.get_ticks()

    def handle_animation(self):
        if not self.charge_mode and self.charge_power > 0:
            self.attack_mode = True

        if self.animation_mode and not self.attack_mode:
            if pg.time.get_ticks() - self.timer > self.interval:
                self.current_image += 1
                if self.current_image >= len(self.current_animation):
                    self.current_image = 0
                self.image = self.current_animation[self.current_image]
                self.timer = pg.time.get_ticks()

        if self.charge_mode:
            self.charge_power += 1
            self.charge_indicator = pg.Surface((self.charge_power, 10))
            self.charge_indicator.fill('red')
            if self.charge_power == 100:
                self.attack_mode = True

        if self.attack_mode and self.charge_power > 0:
            fireball_position = self.rect.topright if self.side == 'right' else self.rect.topleft
            self.magic_balls.add(Magicball(fireball_position, self.side, self.charge_power, self.folder))
            self.charge_power = 0
            self.charge_mode = False
            self.image = self.attack[self.side != 'right']
            self.timer = pg.time.get_ticks()

    def handle_movement(self, direction, keys):
        if self.attack_mode:
            return

        if direction != 0:
            self.animation_mode = True
            self.charge_mode = False
            self.rect.x += direction
            self.current_animation = self.walk_animation_left if direction == -1 else self.walk_animation_right
        else:
            self.animation_mode = True
            self.charge_mode = False
            self.current_animation = self.idle_animation_left if self.side == 'left' else self.idle_animation_right
        if keys[self.key_down]:
            self.animation_mode = False
            self.charge_mode = False
            self.image = self.down[self.side != 'right']
        elif keys[self.key_charge]:
            self.direction = 0
            self.animation_mode = False
            self.image = self.charge[self.side != 'right']
            self.charge_mode = True

        if self.rect.right >= cs.SCREEN_WIDTH:
            self.rect.right = cs.SCREEN_WIDTH
        elif self.rect.left <= 0:
            self.rect.left = 0


class Enemy(pg.sprite.Sprite):
    def __init__(self, folder):
        super().__init__()

        self.folder = folder
        self.load_animations()

        self.hp = 200

        self.image = self.idle_animation_right[0]
        self.current_image = 0
        self.current_animation = self.idle_animation_left

        self.rect = self.image.get_rect()
        self.rect.center = (cs.SCREEN_WIDTH - 100, cs.SCREEN_HEIGHT // 2)

        self.timer = pg.time.get_ticks()
        self.interval = 300
        self.side = "left"
        self.animation_mode = True

        self.magic_balls = pg.sprite.Group()

        self.attack_mode = False
        self.attack_interval = 500

        self.move_interval = 800
        self.move_duration = 0
        self.direction = 0
        self.move_timer = pg.time.get_ticks()

        self.charge_power = 0

    def load_animations(self):
        self.idle_animation_right = [
            cs.load_image(f"images/{self.folder}/idle{i}.png", cs.Character_width, cs.Character_height)
            for i in range(1, 4)]

        self.idle_animation_left = [pg.transform.flip(image, True, False) for image in self.idle_animation_right]

        self.move_animation_right = [
            cs.load_image(f"images/{self.folder}/move{i}.png", cs.Character_width, cs.Character_height)
            for i in range(1, 5)]

        self.move_animation_left = [pg.transform.flip(image, True, False) for image in self.move_animation_right]

        self.attack = [cs.load_image(f"images/{self.folder}/attack.png", cs.Character_width, cs.Character_height)]
        self.attack.append(pg.transform.flip(self.attack[0], True, False))

        self.down = [cs.load_image(f'images/{self.folder}/down.png', cs.Character_width, cs.Character_height)]
        self.down.append(pg.transform.flip(self.down[0], True, False))

    def update(self, player):
        self.handle_attack_mode(player)
        self.handle_movement()
        self.handle_animation()

    def handle_attack_mode(self, player):
        if not self.attack_mode:
            self.attack_probability = 1
            if player.charge_mode:
                self.attack_probability += 2

            if random.randint(1, 100) <= self.attack_probability:
                self.attack_mode = True
                self.charge_power = random.randint(1, 100)

                if player.rect.centerx < self.rect.centerx:
                    self.side = 'left'
                else:
                    self.side = 'right'

                self.animation_mode = False
                self.image = self.attack[self.side != 'right']

        if self.attack_mode:
            if pg.time.get_ticks() - self.timer > self.attack_interval:
                self.attack_mode = False
                self.timer = pg.time.get_ticks()
                self.animation_mode = True

    def handle_movement(self):
        if self.attack_mode:
            return

        now = pg.time.get_ticks()  # взять количество тиков

        if now - self.move_timer < self.move_duration:
            # включить режим анимации
            self.animation_mode = True
            # подвинуть по X координате на direction
            self.rect.x += self.direction
            self.current_animation = self.move_animation_left if self.direction == -1 else self.move_animation_right
        else:
            if random.randint(1, 100) == 1 and now - self.move_timer > self.move_interval:
                self.move_timer = pg.time.get_ticks()
                self.move_duration = random.randint(400, 1500)  # случайное число от 400 до 1500
                self.direction = random.choice([-1, 1])
            else:
                # включить режим анимации
                self.animation_mode = True
                self.current_animation = self.idle_animation_left if self.side == "left" else self.idle_animation_right

        if self.rect.right >= cs.SCREEN_WIDTH:
            self.rect.right = cs.SCREEN_WIDTH
        elif self.rect.left <= 0:
            self.rect.left = 0

    def handle_animation(self):
        if self.animation_mode and not self.attack_mode:

            if pg.time.get_ticks() - self.timer > self.interval:
                self.current_image += 1
                if self.current_image >= len(self.current_animation):
                    self.current_image = 0
                self.image = self.current_animation[self.current_image]
                self.timer = pg.time.get_ticks()

        if self.attack_mode and self.charge_power > 0:
            fireball_position = self.rect.topright if self.side == 'right' else self.rect.topleft
            self.magic_balls.add(Magicball(fireball_position, self.side, self.charge_power, self.folder))
            self.charge_power = 0
            self.image = self.attack[self.side != 'right']
            self.timer = pg.time.get_ticks()


class Magicball(pg.sprite.Sprite):
    def __init__(self, coord, side, power, folder):
        super().__init__()

        self.side = side
        self.power = power
        self.image = cs.load_image(f'images/{folder}/magicball.png', 200, 150)
        self.coord = coord[0], coord[1] + 120

        if self.side == 'right':
            self.image = pg.transform.flip(self.image, True, False)

        self.rect = self.image.get_rect(center=self.coord)

    def update(self):
        if self.side == 'right':
            self.rect.x += 4
            if self.rect.right >= cs.SCREEN_WIDTH:
                self.kill()
        else:
            self.rect.x -= 4
            if self.rect.left <= 0:
                self.kill()
