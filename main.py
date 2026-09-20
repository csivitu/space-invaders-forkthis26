import os
import pygame
import random

pygame.font.init()

width, height = 750, 750
game_window = pygame.display.set_mode((width, height))
pygame.display.set_caption("Amaze Amaze Amaze")

player_ship = pygame.image.load(os.path.join("assets/spaceship.png"))
blue_laser = pygame.image.load(os.path.join("assets/pixel_laser_blue.png"))
asteroid = pygame.image.load(os.path.join("assets/asteroid .png"))

rocky_trapped = pygame.image.load(os.path.join("assets/rocky_trapped.png"))
rocky_freed = pygame.image.load(os.path.join("assets/rocky_freed.png"))

BG = pygame.transform.scale(pygame.image.load(os.path.join("assets/background.png")), (width, height))


class Laser:
    def __init__(self, x, y, img):
        self.x = x
        self.y = y
        self.img = img
        self.mask = pygame.mask.from_surface(self.img)

    def draw(self, window):
        window.blit(self.img, (self.x, self.y))

    def move(self, vel):
        self.y += vel

    def off_screen(self, height):
        return not (self.y <= height and self.y >= 0)

    def collision(self, obj):
        return collide(self, obj)


class Ship:
    COOLDOWN = 30

    def __init__(self, x, y, health=100):
        self.x = x
        self.y = y
        self.health = health
        self.ship_img = None
        self.laser_img = None
        self.lasers = []
        self.cool_down_counter = 0

    def draw(self, window):
        window.blit(self.ship_img, (self.x, self.y))
        for laser in self.lasers:
            laser.draw(window)

    def move_lasers(self, vel, obj):
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(height):
                self.lasers.remove(laser)
            elif laser.collision(obj):
                self.health -= 10
                self.lasers.remove(laser)

    def cooldown(self):
        if self.cool_down_counter >= self.COOLDOWN:
            self.cool_down_counter = 0
        elif self.cool_down_counter > 0:
            self.cool_down_counter += 1

    def shoot(self):
        if self.cool_down_counter == 0:
            laser_x = self.x + self.get_width() // 2 - self.laser_img.get_width() // 2
            laser = Laser(laser_x, self.y, self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 1

    def get_width(self):
        return self.ship_img.get_width()

    def get_height(self):
        return self.ship_img.get_height()


class Player(Ship):
    def __init__(self, x, y, health=100):
        super().__init__(x, y, health)
        self.ship_img = player_ship
        self.laser_img = pygame.transform.scale(blue_laser, (8, 128))
        self.mask = pygame.mask.from_surface(self.ship_img)
        self.max_health = health

    def move_lasers(self, vel, objs, score):
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(height):
                self.lasers.remove(laser)
            else:
                for obj in objs:
                    if laser.collision(obj):
                        if getattr(obj, "is_rocky", False) and not obj.freed:
                            obj.free()
                            score += 50
                        else:
                            score += 10
                        objs.remove(obj)
                        if laser in self.lasers:
                            self.lasers.remove(laser)
                        return score
        return score

    def draw(self, window):
        super().draw(window)
        self.healthbar(window)

    def healthbar(self, window):
        pygame.draw.rect(
            window,
            (255, 0, 0),
            (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width(), 10),
        )
        pygame.draw.rect(
            window,
            (0, 255, 0),
            (
                self.x,
                self.y + self.ship_img.get_height() + 10,
                self.ship_img.get_width() * (self.health / self.max_health),
                10,
            ),
        )


class Enemy(Ship):
    def __init__(self, x, y, health=100):
        super().__init__(x, y, health)
        self.ship_img
        self.laser_img
        self.mask = pygame.mask.from_surface(self.ship_img)
        self.max_health = health










class Asteroid(Ship):
    def __init__(self, x, y, health=100):
        super().__init__(x, y, health)
        self.ship_img = pygame.transform.scale(asteroid, (64, 64))
        self.laser_img = None
        self.mask = pygame.mask.from_surface(self.ship_img)

    def move(self, vel):
        self.y += vel


class RockyAsteroid(Asteroid):
    def __init__(self, x, y, health=100):
        super().__init__(x, y, health)
        self.ship_img = pygame.transform.scale(rocky_trapped, (84, 84))
        self.freed_img = pygame.transform.scale(rocky_freed, (84, 84))
        self.mask = pygame.mask.from_surface(self.ship_img)
        self.is_rocky = True
        self.freed = False

    def free(self):
        self.ship_img = self.freed_img
        self.mask = pygame.mask.from_surface(self.ship_img)
        self.freed = True

    def escape(self):
        pass


def collide(obj1, obj2):
    offset_x = obj2.x - obj1.x
    offset_y = obj2.y - obj1.y
    return obj1.mask.overlap(obj2.mask, (offset_x, offset_y)) is not None


def main():
    run = True
    FPS = 60
    level = 0
    lives = 5
    score = 0
    main_font = pygame.font.SysFont("comicsans", 50)
    lost_font = pygame.font.SysFont("comicsans", 60)

    asteroids = []
    wave_length = 5
    asteroid_vel = 1

    player_vel = 5
    laser_vel = 5

    player = Player(300, 630)

    clock = pygame.time.Clock()

    lost = False
    lost_count = 0

    def redraw_window():
        game_window.blit(BG, (0, 0))
        lives_label = main_font.render(f"Lives: {lives}", 1, (255, 255, 255))
        level_label = main_font.render(f"Level: {level}", 1, (255, 255, 255))
        score_label = main_font.render(f"Score: {score}", 1, (255, 255, 255))

        for asteroid_obj in asteroids:
            asteroid_obj.draw(game_window)

        player.draw(game_window)

        if lost:
            lost_label = lost_font.render("You Lost!!", 1, (255, 255, 255))
            game_window.blit(lost_label, (width / 2 - lost_label.get_width() / 2, 350))

        game_window.blit(lives_label, (10, 10))
        game_window.blit(score_label, (width / 2 - score_label.get_width() / 2, 10))
        game_window.blit(level_label, (width - level_label.get_width() - 10, 10))

        pygame.display.update()

    while run:
        clock.tick(FPS)
        redraw_window()

        if lives <= 0 or player.health <= 0:
            lost = True
            lost_count += 1

        if lost:
            if lost_count > FPS * 4:
                run = False
            else:
                continue

        if len(asteroids) == 0:
            level += 1
            wave_length += 5
            rocky_index = random.randrange(0, wave_length)
            for i in range(wave_length):
                x = random.randrange(50, width - 100)
                y = random.randrange(-1500, -100)
                if i == rocky_index:
                    asteroid_obj = RockyAsteroid(x, y)
                else:
                    asteroid_obj = Asteroid(x, y)
                asteroids.append(asteroid_obj)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and player.x - player_vel > 0:
            player.x -= player_vel
        if keys[pygame.K_RIGHT] and player.x + player_vel + player.get_width() < height:
            player.x += player_vel
        if keys[pygame.K_UP] and player.y - player_vel > 0:
            player.y -= player_vel
        if keys[pygame.K_DOWN] and player.y + player_vel + player.get_height() + 15 < height:
            player.y += player_vel
        if keys[pygame.K_SPACE]:
            player.shoot()

        for asteroid_obj in asteroids[:]:
            if getattr(asteroid_obj, "freed", False):
                asteroid_obj.escape()
                continue

            asteroid_obj.move(asteroid_vel)

            if collide(asteroid_obj, player):
                asteroids.remove(asteroid_obj)
            elif asteroid_obj.y + asteroid_obj.get_height() > height:
                lives -= 1
                asteroids.remove(asteroid_obj)

        score = player.move_lasers(-laser_vel, asteroids, score)


def main_menu():
    title_font = pygame.font.SysFont("comicsans", 30)
    run = True
    while run:
        game_window.blit(BG, (0, 0))
        title_label = title_font.render("click to begin...", 1, (255, 255, 255))
        game_window.blit(title_label, (width / 2 - title_label.get_width() / 2, 350))
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                main()
    pygame.quit()


main_menu()