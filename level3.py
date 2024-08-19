import pygame
import json


class Actor(pygame.sprite.Sprite):
    def __init__(self, image, x, y):
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect(topleft=(x, y))

    def draw(self, surface):
        surface.blit(self.image, self.rect.topleft)


class Level3:
    def __init__(self):
        self.GRID_SIZE = 50
        self.WIDTH, self.HEIGHT = 800, 600  # Adjust according to your map size
        self.GUARD_MOVE_INTERVAL = 50  # Time in milliseconds between guard moves

        # Load the map data from the JSON file
        with open('levels/level3/level3.tmj') as f:
            self.map_data = json.load(f)

        # Load actor images
        self.knight_image = pygame.image.load('images/player.png')
        self.guard_image = pygame.image.load('images/guard.png')
        self.key_image = pygame.image.load('images/key.png')

        # Set up the game objects
        self.setup_game()

        # Initialize guard move timing
        self.last_guard_move_time = pygame.time.get_ticks()

    def setup_game(self):
        self.knight = None
        self.keys_to_collect = []
        self.guards = []

        guard_routes = {
            1: [(250, 100), (250, 50), (250, 100), (250, 150), (250, 100)],  # ID 1
            2: [(200, 450), (200, 400), (200, 350), (250, 350), (250, 400)],  # ID 2
            3: [(500, 350), (450, 350), (450, 400), (500, 400), (500, 350)],  # ID 3
            4: [(450, 147), (450, 150), (500, 150), (500, 150), (500, 100)],  # ID 4

        }
        # Configurar los objetos desde la capa de objetos
        for layer in self.map_data['layers']:
            if layer['type'] == 'objectgroup':
                for obj in layer['objects']:
                    # Convertir las coordenadas en píxeles a coordenadas de cuadrícula
                    grid_x = int(obj['x'] // self.GRID_SIZE)
                    grid_y = int(obj['y'] // self.GRID_SIZE)

                    if obj.get('name') == "Knight":
                        self.knight = Actor(self.knight_image, grid_x * self.GRID_SIZE, grid_y * self.GRID_SIZE)
                    elif obj.get('name') == "Key":
                        self.keys_to_collect.append(
                            Actor(self.key_image, grid_x * self.GRID_SIZE, grid_y * self.GRID_SIZE))
                    elif obj.get('name') == "Guard":
                        guard = Actor(self.guard_image, grid_x * self.GRID_SIZE, grid_y * self.GRID_SIZE)
                        guard_id = obj.get('id')
                        route = guard_routes.get(guard_id, [(grid_x, grid_y)])  # Ruta predeterminada si no se encuentra

                        self.guards.append({'actor': guard, 'route': route, 'route_index': 0, 'direction': 1})

        self.game_over = False
        self.knight_won = False

    def draw_map(self, screen):
        for layer in self.map_data['layers']:
            if layer['type'] == 'tilelayer':
                width = layer['width']
                data = layer['data']

                for index, tile_id in enumerate(data):
                    if tile_id != 0:  # Ignorar tiles vacíos
                        x = (index % width) * self.GRID_SIZE
                        y = (index // width) * self.GRID_SIZE
                        tile_image = self.get_tile_image(tile_id)
                        if tile_image:
                            screen.blit(tile_image, (x, y))

    def get_tile_image(self, tile_id):
        # Load tile images based on tile IDs
        tileset = {
            2: pygame.image.load('images/floor1.png'),
            3: pygame.image.load('images/floor2.png'),
            1: pygame.image.load('images/door.png'),
            4: pygame.image.load('images/wall.png'),
            5: pygame.image.load('images/crack1.png'),
            8: pygame.image.load('images/crack2.png'),
            7: pygame.image.load('images/crack1.png'),
            # Add more tiles as necessary
        }
        return tileset.get(tile_id)

    def draw_actors(self, screen):
        self.knight.draw(screen)
        for key in self.keys_to_collect:
            key.draw(screen)
        for guard in self.guards:
            guard['actor'].draw(screen)

    def draw_game_over(self, screen):
        font = pygame.font.Font(None, 74)
        message = "You won!" if self.knight_won else "You lost!"
        text = font.render(message, True, (255, 255, 255))
        text_rect = text.get_rect(center=(self.WIDTH // 2, self.HEIGHT // 2))
        screen.blit(text, text_rect)

    def draw(self, screen):
        self.draw_map(screen)
        self.draw_actors(screen)
        if self.game_over:
            self.draw_game_over(screen)

    def handle_event(self, event):
        if not self.game_over and event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                self.move_knight(-1, 0)
            elif event.key == pygame.K_UP:
                self.move_knight(0, -1)
            elif event.key == pygame.K_RIGHT:
                self.move_knight(1, 0)
            elif event.key == pygame.K_DOWN:
                self.move_knight(0, 1)
        elif self.game_over and event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            self.restart_level()

    def restart_level(self):
        self.__init__()

    def can_move_to(self, x, y):
        tile_layer = self.map_data['layers'][0]['data']
        width = self.map_data['width']
        tile_id = tile_layer[y * width + x]

        if tile_id in [4]:  # Wall
            return False
        if tile_id == 1 and len(self.keys_to_collect) > 0:  # Door tile, but keys are not collected
            return False
        return True

    def move_knight(self, dx, dy):
        if self.game_over:
            return

        new_x = self.knight.rect.x // self.GRID_SIZE + dx
        new_y = self.knight.rect.y // self.GRID_SIZE + dy

        if self.can_move_to(new_x, new_y):
            self.knight.rect.move_ip(dx * self.GRID_SIZE, dy * self.GRID_SIZE)

        for key in self.keys_to_collect[:]:
            if self.knight.rect.topleft == key.rect.topleft:
                self.keys_to_collect.remove(key)

        self.check_guard_collision()

        if self.is_completed():
            self.game_over = True
            self.knight_won = True

    def move_guard(self, guard):
        next_index = (guard['route_index'] + 1) % len(guard['route'])
        next_x, next_y = guard['route'][next_index]
        guard['actor'].rect.topleft = (next_x, next_y)
        guard['route_index'] = next_index

        self.check_guard_collision()

    def move_guards(self):
        current_time = pygame.time.get_ticks()
        if (current_time - self.last_guard_move_time) > self.GUARD_MOVE_INTERVAL:
            for guard in self.guards:
                self.move_guard(guard)
            self.last_guard_move_time = current_time

    def check_guard_collision(self):
        for guard in self.guards:
            if self.knight.rect.colliderect(guard['actor'].rect):
                self.game_over = True
                self.knight_won = False

    def update(self):
        if not self.game_over:
            self.move_guards()

    def is_completed(self):
        knight_x = self.knight.rect.x // self.GRID_SIZE
        knight_y = self.knight.rect.y // self.GRID_SIZE
        tile_layer = self.map_data['layers'][0]['data']
        width = self.map_data['width']
        tile_id = tile_layer[knight_y * width + knight_x]
        return tile_id == 1 and len(self.keys_to_collect) == 0 and not self.game_over
