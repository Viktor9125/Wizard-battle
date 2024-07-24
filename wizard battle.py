import pygame as pg
import Constants as cs
import player as pl
import pygame_menu as pm
import random

pg.init()


class Menu:
    def __init__(self):
        self.surface = pg.display.set_mode((900, 550))
        # mytheme = pm.Theme(background_color='darkseagreen1',  # transparent background
        #                    title_background_color='darkslategray1',
        #                    title_font_shadow=True,
        #                    widget_padding=25,
        #                    title_bar_style=pm.widgets.MENUBAR_STYLE_UNDERLINE,
        #                    widget_font_color='crimson',
        #                    widget_font_shadow=False)

        self.menu = pm.Menu(
            height=550,
            width=900,
            theme=pm.themes.THEME_SOLARIZED,
            title='Menu',
        )

        self.menu.add.label('Режим на одного.')
        self.menu.add.selector('Enemy: ',
                               [('lightning wizard.', 1), ('earth monk.', 2), ('random.', 3)],
                               onchange=self.set_enemy)
        self.menu.add.button('Play', self.start_one_player_game)
        self.menu.add.label('Режим на двоих.')
        self.menu.add.selector('Left player: ',
                               [('lightning wizard.', 1), ('earth monk.', 2), ('fire wizard.', 3), ('random.', 4)],
                               onchange=self.set_left_player)
        self.menu.add.selector('Right player: ',
                               [('lightning wizard.', 1), ('earth monk.', 2), ('fire wizard.', 3), ('random.', 4)],
                               onchange=self.set_right_player)
        self.menu.add.button('Play', self.start_two_player_game)
        self.menu.add.button('Exit', quit)

        self.enemies = ['lightning wizard', 'earth monk']

        self.current_enemy = self.enemies[0]

        # Эти три строки — новые. Они нужны для хранения информации, кто за кого играет
        self.players = ["lightning wizard", "earth monk", "fire wizard"]
        self.left_player = self.players[0]
        self.right_player = self.players[0]

        self.run()

    def set_enemy(self, selected, value):
        if value in (1, 2):
            self.current_enemy = self.enemies[value - 1]
        else:
            self.current_enemy = random.choice(self.enemies)

    def set_left_player(self, selected, value):
        if value in (1, 3):
            self.left_player = self.players[value - 1]
        else:
            self.left_player = random.choice(self.players)

    def set_right_player(self, selected, value):
        if value in (1, 3):
            self.right_player = self.players[value - 1]
        else:
            self.right_player = random.choice(self.players)

    def start_one_player_game(self):
        Game("one player", (self.current_enemy,))

    def start_two_player_game(self):
        Game("two players", (self.left_player, self.right_player))

    def run(self):
        self.menu.mainloop(self.surface)


class Game:
    def __init__(self, mode, wizards):

        # Создание окна
        self.screen = pg.display.set_mode((cs.SCREEN_WIDTH, cs.SCREEN_HEIGHT))
        pg.display.set_caption("Битва магов")

        self.mode = mode

        self.background = cs.load_image("images/background.png", cs.SCREEN_WIDTH, cs.SCREEN_HEIGHT)
        self.foreground = cs.load_image("images/foreground.png", cs.SCREEN_WIDTH, cs.SCREEN_HEIGHT)

        self.win = None

        if self.mode == 'one player':
            self.player = pl.Player()
            self.enemy = pl.Enemy(wizards[0])
        elif self.mode == 'two players':
            self.player = pl.Player(folder=wizards[0])
            self.enemy = pl.Player(folder=wizards[1], first_player=False)

        self.enemy_choice = 0

        # font = pm.font.FONT_8BIT
        # pm.themes.THEME_SOLARIZED.widget_font = font color aquamarine1

        self.is_running = True

        self.clock = pg.time.Clock()
        self.run()

    def run(self):
        while self.is_running:
            self.event()
            self.update()
            self.draw()
            self.clock.tick(cs.FPS)

    def event(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.is_running = False
            if event.type == pg.KEYDOWN and self.win is not None:
                self.is_running = False

    def update(self):
        if self.win is None:
            if self.player.hp <= 0:
                self.win = self.enemy
            elif self.enemy.hp <= 0:
                self.win = self.player

            self.player.update(self.player)

            self.enemy.update(self.player)

            self.enemy.magic_balls.update()

            self.player.magic_balls.update()

            if self.mode == 'one players' or self.enemy.image not in self.enemy.down:
                hits = pg.sprite.spritecollide(self.enemy, self.player.magic_balls, True,
                                               pg.sprite.collide_rect_ratio(0.3))
                for hit in hits:
                    self.enemy.hp -= hit.power

            if self.player.image not in self.player.down:
                hits_player = pg.sprite.spritecollide(self.player, self.enemy.magic_balls, True,
                                                      pg.sprite.collide_rect_ratio(0.3))
                for hit in hits_player:
                    self.player.hp -= hit.power

    def draw(self):
        # Отрисовка интерфейса

        self.screen.blit(self.background, (0, 0))

        self.screen.blit(self.player.image, self.player.rect)
        self.screen.blit(self.enemy.image, self.enemy.rect)

        self.screen.blit(self.foreground, (0, 0))

        if self.player.charge_mode:
            self.screen.blit(self.player.charge_indicator, (self.player.rect.left + 120, self.player.rect.top))

        if self.mode == 'two players':
            if self.enemy.charge_mode:
                self.screen.blit(self.enemy.charge_indicator, (self.enemy.rect.left + 120, self.enemy.rect.top))

        self.player.magic_balls.draw(self.screen)
        self.enemy.magic_balls.draw(self.screen)

        pg.draw.rect(self.screen, pg.Color('black'), (50, 25, 205, 30), 2)
        pg.draw.rect(self.screen, pg.Color('black'), (cs.SCREEN_WIDTH - 250, 25, 205, 30), 2)
        pg.draw.rect(self.screen, pg.Color('green'), (cs.SCREEN_WIDTH - 247, 27, self.enemy.hp, 25))
        pg.draw.rect(self.screen, pg.Color('green'), (53, 27, self.player.hp, 25))

        if self.win == self.player:
            text = cs.text_render("ПОБЕДА")
            text_rect = text.get_rect(center=(cs.SCREEN_WIDTH // 2, cs.SCREEN_HEIGHT // 2))
            self.screen.blit(text, text_rect)
            text2 = cs.text_render("Маг в левом углу.")
            text_rect2 = text2.get_rect(center=(cs.SCREEN_WIDTH // 2, cs.SCREEN_HEIGHT - 200))
            self.screen.blit(text2, text_rect2)

        elif self.win == self.enemy:
            text = cs.text_render("ПОБЕДА")
            text_rect = text.get_rect(center=(cs.SCREEN_WIDTH // 2, cs.SCREEN_HEIGHT // 2))
            self.screen.blit(text, text_rect)
            text2 = cs.text_render("Маг в правом углу.")
            text_rect2 = text2.get_rect(center=(cs.SCREEN_WIDTH // 2, cs.SCREEN_HEIGHT - 200))
            self.screen.blit(text2, text_rect2)

        pg.display.flip()


if __name__ == "__main__":
    Menu()
