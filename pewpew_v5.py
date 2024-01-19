from random import randint
import pygame, sys
from os import path


pygame.init()
pygame.mixer.init()


img_dir = path.join(path.dirname(sys.argv[0]), 'img')
snd_dir = path.join(path.dirname(sys.argv[0]), 'snd')


TileType = {0: "GROUND", 1: "HOLE", 2: "WALL", 3: "START"}

TileType_color_dict = {
    "GROUND": (0, 255, 34),
    "HOLE": (0, 0, 0),
    "WALL": (115, 54, 0),
    "START": (0, 255, 34)
}


SCREEN_SIZE = 600, 600
TILE_SIZE = 20

MAP_HEIGHT = 30
MAP_WIDTH = 30

SCREEN = pygame.display.set_mode(SCREEN_SIZE)

#  load graphics

ground_graphic = pygame.image.load(path.join(img_dir, "grass_v7_20px.png")).convert()
hole_graphic = pygame.image.load(path.join(img_dir, "hole_v7_20px.png")).convert()
wall_graphic = pygame.image.load(path.join(img_dir, "wall_v1_20px.png")).convert()

player_sprite = pygame.image.load(path.join(img_dir, "player_left_v4_20px.png")).convert()
player_sprite.set_colorkey((255, 255, 255))
standard_mob_sprite = pygame.image.load(path.join(img_dir, "standardmob_left_v2_20px.png")).convert()
standard_mob_sprite.set_colorkey((255, 255, 255))
tracker_mob_sprite = pygame.image.load(path.join(img_dir, "trackermob_left_v2_20px.png")).convert()
tracker_mob_sprite.set_colorkey((255, 255, 255))

health_drop_sprite = pygame.image.load(path.join(img_dir, "healthdrop_v1_20px.png")).convert()
ammo_supply_sprite = pygame.image.load(path.join(img_dir, "ammosupply_v4_20px.png")).convert()
ammo_supply_sprite.set_colorkey((255, 255, 255))
#  graphics made w FireAlpaca

TileType_graphics_dict = {
    "GROUND": ground_graphic,
    "HOLE": hole_graphic,
    "WALL": wall_graphic,
    "START": ground_graphic,
}

#  load sounds
shoot_sound = pygame.mixer.Sound(path.join(snd_dir, "playershoot_v4.wav"))
shoot_sound.set_volume(0.25)
player_hit_sound = pygame.mixer.Sound(path.join(snd_dir, "playerhit_v2.wav"))
player_hit_sound.set_volume(1)
player_death_sound = pygame.mixer.Sound(path.join(snd_dir, "playerdeath_v1.wav"))
player_death_sound.set_volume(1.5)

mob_shoot_sound = pygame.mixer.Sound(path.join(snd_dir, "mobshoot_v2.wav"))
mob_shoot_sound.set_volume(0.5)  # mob shoot sound was set to volume 25 on website instead of 50
mob_hit_sound = pygame.mixer.Sound(path.join(snd_dir, "mobhit_v1.wav"))
mob_hit_sound.set_volume(1)
mob_death_sound = pygame.mixer.Sound(path.join(snd_dir, "mobdeath_v1.wav"))
mob_death_sound.set_volume(1)

health_pickup_sound = pygame.mixer.Sound(path.join(snd_dir, "healthpickup_v1.wav"))
health_pickup_sound.set_volume(0.5)
ammo_pickup_sound = pygame.mixer.Sound(path.join(snd_dir, "ammopickup_v1.wav"))
ammo_pickup_sound.set_volume(0.5)

#  sounds made w https://www.bfxr.net

#  load music
pygame.mixer.music.load(path.join(snd_dir, 'Map.wav'))
pygame.mixer.music.set_volume(0.3)


#  Music is SketchyLogic's Map from his NES Shooter Music track.
#  Music found on https://opengameart.org
#  SketchyLogic's page : https://opengameart.org/users/sketchylogic


all_sprites = pygame.sprite.Group()

standard_mobs = pygame.sprite.Group()
tracker_mobs = pygame.sprite.Group()
mobs = pygame.sprite.Group()
health_bar = pygame.sprite.Group()

bullets = pygame.sprite.Group()
mob_bullets = pygame.sprite.Group()

drops = pygame.sprite.Group()


health_drop_chance = 70

bullet_positions = []

pygame.display.set_caption('pewpew_v5')

font_path = path.join(path.dirname(sys.argv[0]), 'freesansbold.ttf')

font_1_size = int(SCREEN_SIZE[0] / 10)
font_1 = pygame.font.Font(font_path, font_1_size)
font_2_size = int(font_1_size / 3)
font_2 = pygame.font.Font(font_path, font_2_size)
font_3_size = int(SCREEN_SIZE[0] / 25)
font_3 = pygame.font.Font(font_path, font_3_size)
font_4_size = int(font_3_size / 1.5)
font_4 = pygame.font.Font(font_path, font_4_size)


class Game:
    def __init__(self, map_height, map_width, grid_width, grid_height, screen):
        self.grid_width = grid_width
        self.grid_height = grid_height

        self.map_height = map_height
        self.map_width = map_width

        self.screen_size = SCREEN_SIZE

        self.screen = screen

        self.round_number = 1

        self.running = True
        self.help_menu = False

        # self.grid = np.full((self.grid_width, self.grid_height), 0)
        self.grid = []
        for _ in range(self.grid_height):
            row = []
            for __ in range(self.grid_width):
                row.append(0)
            self.grid.append(row)

        # for row in self.grid:
        #    print(row)

        self.position = (randint(1, self.grid_height - 2), randint(1, self.grid_width - 2))
        self.grid[self.position[1]][self.position[0]] = 3
        self.player = Player(self.position[0], self.position[1])
        self.player_alive = False

        self.occupied_locations = []
        self.occupied_locations.append(self.position[::-1])

        self.file_str = 'high_score.txt'
        if not path.isfile(self.file_str):
            with open(self.file_str, 'w') as f:
                f.write('0')

    # METTRE EN PLACE LE MAP

    def place_walls(self):

        for col in range(1, self.grid_width - 2):
            for row in range(1, self.grid_height - 2):
                if not(self.occupied_locations.__contains__((row, col))):

                        if (self.grid[row - 1][col] == 2 or self.grid[row + 1][col] == 2
                                or self.grid[row][col - 1] == 2 or self.grid[row][col + 1] == 2):
                            if randint(1, 100) <= 45: # chance of wall spawning next to pre existing wall
                                self.occupied_locations.append((row, col))
                                self.grid[row][col] = 2

                        elif not(self.grid[row - 1][col - 1] == 2 or self.grid[row - 1][col + 1] == 2 or
                                self.grid[row + 1][col - 1] == 2 or self.grid[row + 1][col + 1] == 2):
                            if randint(1, 100) <= 10: # chance of wall spawning next to all ground
                                self.occupied_locations.append((row, col))
                                self.grid[row][col] = 2

    def place_holes(self):
        for col in range(1, self.grid_width - 2):
            for row in range(1, self.grid_height - 2):
                if not (self.occupied_locations.__contains__((row, col))):

                    if (self.grid[row - 1][col] == 1 or self.grid[row + 1][col] == 1
                            or self.grid[row][col - 1] == 1 or self.grid[row][col + 1] == 1):
                        if randint(1, 100) <= 35:  # Chance of hole spawning next to a pre-existing hole
                            self.occupied_locations.append((row, col))
                            self.grid[row][col] = 1

                    elif not (self.grid[row - 1][col - 1] == 1 or self.grid[row - 1][col + 1] == 1 or
                              self.grid[row + 1][col - 1] == 1 or self.grid[row + 1][col + 1] == 1):
                        if randint(1, 100) <= 8: # Chance of hole spawning next to all ground
                            self.occupied_locations.append((row, col))
                            self.grid[row][col] = 1

    def place_start(self):
        start = (randint(1, len(self.grid[0]) - 2), randint(1, len(self.grid[1]) - 2))
        while self.occupied_locations.__contains__(start):
            start = (randint(1, len(self.grid[0]) - 2), randint(1, len(self.grid[1]) - 2))

        self.occupied_locations.append((start[1], start[0]))
        self.grid[start[1]][start[0]] = 3  # TODO maybe [0][1] ?

        self.player.x = start[0] * TILE_SIZE
        self.player.y = start[1] * TILE_SIZE

    def update_high_score(self, score):
        with open(self.file_str, 'r') as f:
            current_high_score = int(f.readline())
        f.close()

        if current_high_score < score:
            with open(self.file_str, 'w') as f:
                f.write(str(score))
            f.close()

    # DIFFÉRENTES PAGES DU JEU

    def game_over(self, score):
        self.update_high_score(score)

        title_text = font_1.render('PewPew', True, (255, 240, 0))
        title_text_width, title_text_height = font_1.size('PewPew')
        self.screen.blit(title_text, ((self.screen_size[0] - title_text_width) / 2, 25))

        game_over_msg = 'Game Over!'
        msg_1 = font_1.render(game_over_msg, True, (255, 240, 0))
        msg_1_width, msg_1_height = font_1.size(game_over_msg)

        restart_msg = 'Press R to Restart'
        msg_2 = font_2.render(restart_msg, True, (255, 240, 0))
        msg_2_width, msg_2_height = font_2.size(restart_msg)

        help_text = font_2.render('Press H to get help on the game', True, (255, 240, 0))
        help_text_width, help_text_height = font_2.size('Press H to get help on the game')

        self.screen.blit(msg_1, ((self.screen_size[0] - msg_1_width) / 2, (self.screen_size[1] - msg_1_height) / 2))
        self.screen.blit(msg_2, ((self.screen_size[0] - msg_2_width) / 2, (self.screen_size[1] - msg_2_height) / 2 + font_1_size / 2))

        self.screen.blit(help_text, ((self.screen_size[0] - help_text_width) / 2,
                                (self.screen_size[1] - help_text_height) / 2 + font_1_size / 2 + font_2_size * 2))

    def intro(self):
        title_text = font_1.render('PewPew', True, (255, 240, 0))
        title_text_width, title_text_height = font_1.size('PewPew')

        play_text = font_2.render('Press R to start the game', True, (255, 240, 0))
        play_text_width, play_text_height = font_2.size('Press R to start the game')

        help_text = font_2.render('Press H to get help on the game', True, (255, 240, 0))
        help_text_width, help_text_height = font_2.size('Press H to get help on the game')

        self.screen.blit(GAME.player.image, (GAME.player.x, GAME.player.y))

        self.screen.blit(title_text, ((self.screen_size[0] - title_text_width) / 2, (self.screen_size[1] - title_text_height) / 3))
        self.screen.blit(play_text, ((self.screen_size[0] - title_text_width) / 2,
                                (self.screen_size[1] - play_text_height) / 3 + 75))

        self.screen.blit(help_text, ((self.screen_size[0] - help_text_width) / 2,
                                (self.screen_size[1] - help_text_height) / 3 + 225))

    def help_page(self):
        for col in range(len(self.grid[0])):
            for row in range(len(self.grid[1])):
                self.screen.blit(TileType_graphics_dict["GROUND"],
                            pygame.Rect((row * TILE_SIZE, col * TILE_SIZE), (TILE_SIZE, TILE_SIZE)))
        self.screen.blit(GAME.player.image, (GAME.player.x, GAME.player.y))

        title_text = font_1.render('PewPew', True, (255, 240, 0))
        title_text_width, title_text_height = font_1.size('PewPew')
        self.screen.blit(title_text, ((self.screen_size[0] - title_text_width) / 2, 25))

        self.screen.blit(wall_graphic, (35, 100))
        wall_desc = font_4.render('A wall for cover', True, (255, 240, 0))
        self.screen.blit(wall_desc, (60, 100 + TILE_SIZE - font_4_size))

        self.screen.blit(hole_graphic, (35, 150))
        hole_desc = font_4.render('A hole in the ground that ends that round when fallen into', True, (255, 240, 0))
        self.screen.blit(hole_desc, (60, 150 + TILE_SIZE - font_4_size))

        self.screen.blit(standard_mob_sprite, (35, 200))
        standard_mob_desc = font_4.render('Standard mob that stays in place to shoot when player is in range',
                                          True, (255, 240, 0))
        self.screen.blit(standard_mob_desc, (60, 200 + TILE_SIZE - font_4_size))

        self.screen.blit(tracker_mob_sprite, (35, 250))
        tracker_mob_desc = font_4.render('Tracker mob that approaches while shooting when player is in range',
                                         True, (255, 240, 0))
        self.screen.blit(tracker_mob_desc, (60, 250 + TILE_SIZE - font_4_size))

        self.screen.blit(health_drop_sprite, (35, 300))
        health_drop_desc = font_4.render('A health drop that heals 20 HP', True, (255, 240, 0))
        self.screen.blit(health_drop_desc, (60, 300 + TILE_SIZE - font_4_size))

        self.screen.blit(ammo_supply_sprite, (35, 350))
        ammo_supply_desc = font_4.render('An ammo supply that gives 20 ammo', True, (255, 240, 0))
        self.screen.blit(ammo_supply_desc, (60, 350 + TILE_SIZE - font_4_size))

        play_text = font_4.render('Press R to start the game', True, (255, 240, 0))
        self.screen.blit(play_text, (35, 500))

        credit_text = "Graphics made with FireAlpaca 2, sounds made with bfxr.net, and music by " \
                      "SketchyLogic opengameart.org/users/sketchylogic"
        credit_list = []
        credit_pos = [35, 450]
        for word in credit_text.split():
            credit_list.append(word)
            credit_list.append(" ")
        for word in credit_list:
            credit_text = font_4.render(word, True, (255, 240, 0))
            if credit_pos[0] >= 500:
                credit_pos = [35, credit_pos[1] + 20]
                self.screen.blit(credit_text, credit_pos)
                credit_pos[0] += font_4.size(word)[0]
            else:
                self.screen.blit(credit_text, credit_pos)
                credit_pos[0] += font_4.size(word)[0]


class Player(pygame.sprite.Sprite):

    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.x = x * TILE_SIZE
        self.y = y * TILE_SIZE

        self.image = pygame.transform.scale(player_sprite, (TILE_SIZE, TILE_SIZE))
        self.rect = pygame.Rect((self.x, self.y), (TILE_SIZE, TILE_SIZE))
        self.hp = 100
        self.hp_bar = pygame.Rect((20, 580), (self.hp, 10))

        all_sprites.add(self)

        self.ammo = 100
        self.ammo_count_text = font_3.render(str(self.ammo), True, (255, 255, 0))

    def move(self):
        global player_alive
        keystate = pygame.key.get_pressed()
        if GAME.grid[int(self.y / TILE_SIZE)][int(self.x / TILE_SIZE)] == 1:
            player_death_sound.play()
            self.hp = 0
            GAME.player_alive = False
            GAME.round_number += 1
        else:
            if keystate[pygame.K_s] or keystate[pygame.K_DOWN]:
                if not self.y + TILE_SIZE >= SCREEN_SIZE[1] \
                        and GAME.grid[int((self.y + TILE_SIZE) / TILE_SIZE)][int(self.x / TILE_SIZE)] != 2:
                    self.y += TILE_SIZE
            elif keystate[pygame.K_w] or keystate[pygame.K_UP]:
                if not self.y - TILE_SIZE <= 0 - TILE_SIZE \
                        and GAME.grid[int((self.y - TILE_SIZE) / TILE_SIZE)][int(self.x / TILE_SIZE)] != 2:
                    self.y -= TILE_SIZE
            if keystate[pygame.K_d] or keystate[pygame.K_RIGHT]:
                if not self.x + TILE_SIZE >= SCREEN_SIZE[0] \
                        and GAME.grid[int(self.y / TILE_SIZE)][int((self.x + TILE_SIZE) / TILE_SIZE)] != 2:
                    self.x += TILE_SIZE
                    self.image = pygame.image.load(path.join(img_dir, "player_right_v4_20px.png")).convert()
            elif keystate[pygame.K_a] or keystate[pygame.K_LEFT]:
                if not self.x - TILE_SIZE <= 0 - TILE_SIZE \
                        and GAME.grid[int(self.y / TILE_SIZE)][int((self.x - TILE_SIZE) / TILE_SIZE)] != 2:
                    self.x -= TILE_SIZE
                    self.image = pygame.image.load(path.join(img_dir, "player_left_v4_20px.png")).convert()

        self.image.set_colorkey((255, 255, 255))
        self.rect = pygame.Rect((self.x, self.y), (TILE_SIZE, TILE_SIZE))
        return self.x, self.y, self.image

    def shoot(self):
        bullet = Bullet()
        bullets.add(bullet)
        all_sprites.add(bullet)
        shoot_sound.play()


class Mob(pygame.sprite.Sprite):
    def __init__(self):
        global TILE_SIZE, MAP_HEIGHT, MAP_WIDTH
        pygame.sprite.Sprite.__init__(self)
        mobs.add(self)

        self.hp = 20

        borders = [[0, 'y'], [MAP_HEIGHT - 1, 'y'],  # permet de choisir une position
                   ['x', 0], ['x', MAP_WIDTH - 1]]  # sur côté du map

        self.spawn = borders[randint(0, len(borders) - 1)]
        if type(self.spawn[0]) == int:
            self.spawn[1] = randint(0, MAP_HEIGHT - 1)
        else:
            self.spawn[0] = randint(0, MAP_WIDTH - 1)
        self.x, self.y = self.spawn[0] * TILE_SIZE, self.spawn[1] * TILE_SIZE

        self.rect = pygame.Rect((self.x, self.y), (TILE_SIZE, TILE_SIZE))

        self.target_x = GAME.player.x
        self.target_y = GAME.player.y

        self.range = 10 * TILE_SIZE
        self.target_in_range = False

        self.neighbors = [(-1 * TILE_SIZE, -1 * TILE_SIZE), (-1 * TILE_SIZE, 0 * TILE_SIZE),
                          (-1 * TILE_SIZE, 1 * TILE_SIZE),
                          (0 * TILE_SIZE, -1 * TILE_SIZE), (0 * TILE_SIZE, 0 * TILE_SIZE),
                          (0 * TILE_SIZE, 1 * TILE_SIZE),
                          (1 * TILE_SIZE, -1 * TILE_SIZE), (1 * TILE_SIZE, 0 * TILE_SIZE),
                          (1 * TILE_SIZE, 1 * TILE_SIZE)]
        # TODO: enlever voisins diagonaux ou pas ?

        self.move_event = pygame.USEREVENT
        self.move_speed = 250
        pygame.time.set_timer(self.move_event, self.move_speed)

    def update_range(self):
        global GAME
        self.target_x = GAME.player.x
        self.target_y = GAME.player.y
        if self.range >= self.target_x - self.x >= -self.range \
                and self.range >= self.target_y - self.y >= -self.range:
            self.target_in_range = True
        else:
            self.target_in_range = False

    def move_out_of_range(self):  # détermine mouvements fait par Mob quand Player pas in range
        move = self.neighbors[randint(0, len(self.neighbors) - 1)]
        while self.x + move[0] >= SCREEN_SIZE[0] or self.x + move[0] < 0 \
                or self.y + move[1] >= SCREEN_SIZE[1] or self.y + move[1] < 0 \
                or GAME.screen.get_at((self.x + move[0], self.y + move[1])) != \
                TileType_graphics_dict["GROUND"].get_at((0, 0)):
            move = self.neighbors[randint(0, len(self.neighbors) - 1)]

        self.update_graphic(move)

        self.x += move[0]
        self.y += move[1]

        self.rect = pygame.Rect((self.x, self.y), (TILE_SIZE, TILE_SIZE))

    def update_graphic(self, move):
        if self.x < self.x + move[0]:
            self.image = pygame.image.load(path.join(img_dir, self.graphic_right)).convert()
        else:
            self.image = pygame.image.load(path.join(img_dir, self.graphic_left)).convert()

        self.image.set_colorkey((255, 255, 255))

    def shoot(self):
        mob_bullet = MobBullet(self.x, self.y)
        all_sprites.add(mob_bullet)
        mob_shoot_sound.play()

    def update(self):
        self.update_range()
        self.update_move()


class StandardMob(Mob):
    def __init__(self):
        Mob.__init__(self)
        standard_mobs.add(self)

        self.graphic_left = "standardmob_left_v2_20px.png"
        self.graphic_right = "standardmob_right_v2_20px.png"
        self.image = pygame.transform.scale(standard_mob_sprite, (TILE_SIZE, TILE_SIZE))

    def update_move(self):
        if self.target_in_range:
            self.shoot()
        else:
            self.move_out_of_range()


class TrackerMob(Mob):
    def __init__(self):
        Mob.__init__(self)
        tracker_mobs.add(self)

        self.graphic_left = "trackermob_left_v2_20px.png"
        self.graphic_right = "trackermob_right_v2_20px.png"
        self.image = pygame.transform.scale(tracker_mob_sprite, (TILE_SIZE, TILE_SIZE))

        self.shortest_path = []

    def find_path(self):
        start_node = (int(self.x / TILE_SIZE), int(self.y / TILE_SIZE))
        goal = (int(self.target_x / TILE_SIZE), int(self.target_y / TILE_SIZE))
        unvisited_nodes = []
        visited_nodes = [start_node]

        for row in range(int(SCREEN_SIZE[0] / TILE_SIZE)):
            for col in range(int(SCREEN_SIZE[1] / TILE_SIZE)):
                if GAME.grid[col][row] == 0:
                    unvisited_nodes.append((row, col))

        unvisited_node_values = {}

        for node in unvisited_nodes:
            unvisited_node_values[node] = None

        visited_node_values = {start_node: 0}

        neighbors = [(-1, 0), (0, -1), (0, 1), (1, 0),  # voisins non diagonaux
                     (1, 1), (-1, -1), (1, -1), (-1, 1)]  # voisins diagonaux

        node_move_cost = 1

        for node in visited_nodes:
            if visited_nodes.__contains__(goal):
                break
            else:
                for neighbor in neighbors:
                    if unvisited_nodes.__contains__((node[0] + neighbor[0], node[1] + neighbor[1])):
                        unvisited_nodes.pop(unvisited_nodes.index((node[0] + neighbor[0], node[1] + neighbor[1])))
                        unvisited_node_values.pop((node[0] + neighbor[0], node[1] + neighbor[1]))
                        visited_nodes.append((node[0] + neighbor[0], node[1] + neighbor[1]))
                        visited_node_values[(node[0] + neighbor[0], node[1] + neighbor[1])] = \
                            visited_node_values[node] + node_move_cost

        shortest_path = []
        possible_moves = []
        possible_move_values = []

        next_move = goal

        while True:
            for neighbor in neighbors:
                if visited_nodes.__contains__((next_move[0] + neighbor[0], next_move[1] + neighbor[1])):
                    possible_moves.append((next_move[0] + neighbor[0], next_move[1] + neighbor[1]))
                    possible_move_values.append(
                        visited_node_values[(next_move[0] + neighbor[0], next_move[1] + neighbor[1])])
            if possible_moves.__contains__(start_node):
                break

            if len(possible_move_values) > 0:
                next_move = possible_moves[possible_move_values.index(min(possible_move_values))]
                shortest_path.append(next_move)
                possible_moves = []
                possible_move_values = []
            else:
                break

        return shortest_path[::-1]

    def update_move(self):
        if self.target_in_range:
            self.shortest_path = TrackerMob.find_path(self)

            if len(self.shortest_path) > 0:
                self.update_graphic(self.shortest_path[0])

                self.x = self.shortest_path[0][0] * TILE_SIZE
                self.y = self.shortest_path[0][1] * TILE_SIZE

                self.rect = pygame.Rect((self.x, self.y), (TILE_SIZE, TILE_SIZE))

            self.shoot()
        else:
            self.move_out_of_range()


class Bullet(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((TILE_SIZE / 4, TILE_SIZE / 4))
        self.image.fill((255, 255, 0))
        self.x = GAME.player.x + TILE_SIZE / 3
        self.y = GAME.player.y + TILE_SIZE / 3
        # self.center_x = self.x + (TILE_SIZE / 3) / 2
        # self.center_y = self.y + (TILE_SIZE / 3) / 2
        self.rect = pygame.Rect((self.x, self.y), (5, 5))
        self.target_x, self.target_y = pygame.mouse.get_pos()
        self.biggest_distance = max(abs(self.target_x), abs(self.target_y))
        self.max_speed = 5
        self.damage = 10
        self.distance_x = self.target_x - self.x
        self.distance_y = self.target_y - self.y

        if abs(self.distance_x) > abs(self.distance_y):
            if self.target_x < self.x:
                self.speed_x = -self.max_speed
            else:
                self.speed_x = self.max_speed
            self.speed_y = self.speed_x * self.distance_y / self.distance_x
        elif abs(self.distance_x) < abs(self.distance_y):
            if self.target_y < self.y:
                self.speed_y = -self.max_speed
            else:
                self.speed_y = self.max_speed
            self.speed_x = self.speed_y * self.distance_x / self.distance_y
        else:
            if self.distance_x < 0:
                self.speed_x = -self.max_speed
            else:
                self.speed_x = self.max_speed
            if self.distance_y < 0:
                self.speed_y = -self.max_speed
            else:
                self.speed_y = self.max_speed

    def update(self):
        if GAME.player_alive:
            self.x += self.speed_x
            self.y += self.speed_y
            self.rect = pygame.Rect((self.x, self.y), (TILE_SIZE / 3, TILE_SIZE / 3))
            try:
                if self.x < 0 or self.x > SCREEN_SIZE[0] or self.y < 0 or self.y > SCREEN_SIZE[1] \
                        or GAME.grid[int(self.y / TILE_SIZE)][int(self.x / TILE_SIZE)] == 2:
                    self.kill()
            except IndexError:
                Nones


class MobBullet(pygame.sprite.Sprite):
    def __init__(self, mob_x, mob_y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((TILE_SIZE / 4, TILE_SIZE / 4))
        self.image.fill((255, 178, 0))
        self.x = mob_x + TILE_SIZE / 3
        self.y = mob_y + TILE_SIZE / 3
        self.rect = pygame.Rect((self.x, self.y), (5, 5))
        self.target_x = GAME.player.x + TILE_SIZE / 3
        self.target_y = GAME.player.y + TILE_SIZE / 3
        self.max_speed = 5
        self.damage = 10
        self.distance_x = self.target_x - self.x
        self.distance_y = self.target_y - self.y
        mob_bullets.add(self)
        if abs(self.distance_x) > abs(self.distance_y):
            if self.target_x < self.x:
                self.speed_x = -self.max_speed
            else:
                self.speed_x = self.max_speed
            self.speed_y = self.speed_x * self.distance_y / self.distance_x
        elif abs(self.distance_x) < abs(self.distance_y):
            if self.target_y < self.y:
                self.speed_y = -self.max_speed
            else:
                self.speed_y = self.max_speed
            self.speed_x = self.speed_y * self.distance_x / self.distance_y
        else:
            if self.distance_x < 0:
                self.speed_x = -self.max_speed
            else:
                self.speed_x = self.max_speed
            if self.distance_y < 0:
                self.speed_y = -self.max_speed
            else:
                self.speed_y = self.max_speed

    def update(self):
        if GAME.player_alive:
            self.x += self.speed_x
            self.y += self.speed_y
            self.rect = pygame.Rect((self.x, self.y), (TILE_SIZE / 3, TILE_SIZE / 3))
            try:
                if self.x < 0 or self.x > SCREEN_SIZE[0] or self.y < 0 or self.y > SCREEN_SIZE[1] \
                        or GAME.grid[int(self.y / TILE_SIZE)][int(self.x / TILE_SIZE)] == 2:
                    self.kill()
            except IndexError:
                None

health_drop_counter = 0


class HealthDrop(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        drops.add(self)
        all_sprites.add(self)
        self.image = health_drop_sprite
        self.x, self.y = randint(0, len(GAME.grid) - 1) * TILE_SIZE + 2.5, \
                         randint(0, len(GAME.grid) - 1) * TILE_SIZE + 2.5
        while GAME.occupied_locations.__contains__((int(self.y / TILE_SIZE), int(self.x / TILE_SIZE))):
            self.x, self.y = randint(0, len(GAME.grid) - 1) * TILE_SIZE + 2.5, \
                             randint(0, len(GAME.grid) - 1) * TILE_SIZE + 2.5
        self.rect = pygame.Rect((self.x, self.y), (14, 14))

    def update(self):
        global health_drop_counter
        self.rect = pygame.Rect((self.x, self.y), (int(TILE_SIZE * 15 / 20), int(TILE_SIZE * 15 / 20)))
        if self.rect.colliderect(GAME.player.rect):
            GAME.player.hp += 20
            health_drop_counter -= 1
            self.kill()
            health_pickup_sound.play()


ammo_supply_counter = 0


class AmmoSupply(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        drops.add(self)
        all_sprites.add(self)
        self.image = ammo_supply_sprite
        # self.image.set_colorkey((255, 255, 255))
        self.x, self.y = randint(0, len(GAME.grid) - 1) * TILE_SIZE + int(TILE_SIZE * 2 / 15), \
                         randint(0, len(GAME.grid) - 1) * TILE_SIZE + int(TILE_SIZE * 2 / 15)
        while GAME.occupied_locations.__contains__((int(self.y / TILE_SIZE), int(self.x / TILE_SIZE))):
            self.x, self.y = randint(0, len(GAME.grid) - 1) * TILE_SIZE + int(TILE_SIZE * 2 / 15), \
                             randint(0, len(GAME.grid) - 1) * TILE_SIZE + int(TILE_SIZE * 2 / 15)
        self.rect = pygame.Rect((self.x, self.y), (int(TILE_SIZE * 11 / 15), int(TILE_SIZE * 11 / 15)))

    def update(self):
        global ammo_supply_counter
        self.rect = pygame.Rect((self.x, self.y), (int(TILE_SIZE * 11 / 15), int(TILE_SIZE * 11 / 15)))
        if self.rect.colliderect(GAME.player.rect):
            GAME.player.ammo += 20
            ammo_supply_counter -= 1
            self.kill()
            ammo_pickup_sound.play()


GAME = Game(SCREEN_SIZE[0], SCREEN_SIZE[1], MAP_HEIGHT, MAP_WIDTH, SCREEN)
GAME.place_walls()
GAME.place_holes()

clock = pygame.time.Clock()

score = 0

player_move_event = pygame.USEREVENT + 1
player_move_speed = 250

mob_spawn_event = pygame.USEREVENT + 2
mob_spawn_speed = 3500

mob_move_event = pygame.USEREVENT + 3
mob_move_speed = 500

drop_spawn_event = pygame.USEREVENT + 4
drop_spawn_speed = 20000


# player_alive = False
# first_round = True

pygame.mixer.music.play(loops=-1)

while GAME.running:
    clock.tick(60)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            GAME.running = False
            sys.exit()
        if GAME.player_alive:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if GAME.player.ammo > 0:
                    GAME.player.shoot()
                    GAME.player.ammo -= 1
            if event.type == player_move_event:
                GAME.player.move()
            if event.type == mob_spawn_event:
                random_num = randint(0, 100)
                if random_num <= 30:
                    mob = TrackerMob()
                else:
                    mob = StandardMob()
            if event.type == mob_move_event:
                for mob in mobs:
                    mob.update_range()
                    mob.update_move()
            if event.type == drop_spawn_event:
                if GAME.player.ammo <= 20:
                    health_drop_chance = 10
                else:
                    health_drop_chane = 70
                if randint(0, 100) <= health_drop_chance and health_drop_counter < 5:
                    health_drop = HealthDrop()
                    health_drop_counter += 1
                else:
                    if ammo_supply_counter < 5:
                        ammo_supply = AmmoSupply()
                        ammo_supply_counter += 1

    for bullet in bullets:
        for mob in mobs:
            if bullet.rect.colliderect(mob.rect):
                bullet.kill()
                if mob.hp > 0:
                    mob.hp -= bullet.damage
                if mob.hp <= 0:
                    mob.kill()
                    mob_death_sound.play()
                    score += 1
                else:
                    mob_hit_sound.play()
    for mob_bullet in mob_bullets:
        if mob_bullet.rect.colliderect(GAME.player.rect):
            mob_bullet.kill()
            if GAME.player.hp > 0:
                GAME.player.hp -= mob_bullet.damage
            if GAME.player.hp <= 0:
                GAME.player_alive = False
                player_death_sound.play()

                GAME.round_number += 1
            else:
                player_hit_sound.play()

    #for col, row in np.ndindex(GAME.grid.shape):
    for row in range(len(GAME.grid[0])):
        for col in range(len(GAME.grid[1])):
            GAME.screen.blit(TileType_graphics_dict[TileType[int(GAME.grid[col][row])]],
                        pygame.Rect((row * TILE_SIZE, col * TILE_SIZE), (TILE_SIZE, TILE_SIZE)))

    all_sprites.draw(GAME.screen)
    mobs.draw(GAME.screen)
    all_sprites.update()

    GAME.player.hp_bar = pygame.Rect((20, 580), (GAME.player.hp, 10))
    GAME.screen.fill((255, 255, 0), GAME.player.hp_bar)

    score_text = font_3.render((str(score)), True, (255, 240, 0))
    score_text_2 = font_4.render('kills', True, (255, 240, 0))

    GAME.player.ammo_count_text = font_4.render(str(GAME.player.ammo), True, (255, 255, 0))
    ammo_text = font_4.render('bullets', True, (255, 255, 0))

    high_score_text = font_4.render('High Score: ', True, (255, 255, 0))
    with open(GAME.file_str, 'r') as f:
        high_score_text_2 = font_4.render(f.readline(), True, (255, 255, 0))
    f.close()

    GAME.screen.blit(score_text, (GAME.screen_size[0] * 10 / 600, 5))
    GAME.screen.blit(score_text_2, (score_text.get_rect().width + 15, score_text.get_rect().height - font_4_size + 2.5))

    GAME.screen.blit(GAME.player.ammo_count_text, (20, 580 - font_4_size))
    GAME.screen.blit(ammo_text, (GAME.player.ammo_count_text.get_rect().width + 22.5, 580 - font_4_size))

    GAME.screen.blit(high_score_text, (GAME.screen_size[0] - 120, 5))
    GAME.screen.blit(high_score_text_2, (GAME.screen_size[0] - 120 + high_score_text.get_rect().width, 5))

    if not GAME.player_alive and GAME.round_number != 1:
        GAME.game_over(score)

        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_h:
                    GAME.help_menu = True
                elif event.key == pygame.K_r:
                    GAME.help_menu = False
                    for mob in mobs:
                        mob.kill()
                    for bullet in bullets:
                        bullet.kill()
                    for mob_bullet in mob_bullets:
                        mob_bullet.kill()
                    for drop in drops:
                        drop.kill()

                    GAME.grid = []
                    for _ in range(GAME.grid_height):
                        row = []
                        for __ in range(GAME.grid_width):
                            row.append(0)
                        GAME.grid.append(row)

                    GAME.occupied_locations = []

                    GAME.place_start()

                    GAME.place_walls()
                    GAME.place_holes()

                    GAME.player_alive = True
                    GAME.player.hp = 100
                    GAME.player.ammo = 100
                    score = 0

                    health_drop_counter = 0
                    ammo_supply_counter = 0

                    pygame.time.set_timer(mob_spawn_event, mob_spawn_speed)
                    pygame.time.set_timer(mob_move_event, mob_move_speed)
                    pygame.time.set_timer(drop_spawn_event, drop_spawn_speed)

        if GAME.help_menu:
            GAME.help_page()

    elif not GAME.player_alive and GAME.round_number == 1:

        #for col, row in np.ndindex(GAME.grid.shape):
        for col in range(len(GAME.grid[0])):
            for row in range(len(GAME.grid[1])):
                GAME.screen.blit(TileType_graphics_dict["GROUND"],
                            pygame.Rect((row * TILE_SIZE, col * TILE_SIZE), (TILE_SIZE, TILE_SIZE)))

        if not GAME.help_menu:
            GAME.intro()

        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    GAME.player_alive = True
                    GAME.help_menu = False
                    pygame.time.set_timer(player_move_event, player_move_speed)
                    pygame.time.set_timer(mob_spawn_event, mob_spawn_speed)
                    pygame.time.set_timer(mob_move_event, mob_move_speed)
                    pygame.time.set_timer(drop_spawn_event, drop_spawn_speed)
                elif event.key == pygame.K_h:
                    GAME.help_menu = True

        if GAME.help_menu:
            GAME.help_page()

    pygame.display.flip()

#  when typing coords row goes first then col
#  the placement of the tiles in game is not en rapport avec the map string/grid that is created
#     the coordinates are swapped
