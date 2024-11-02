# import pygame
# import math
# import random
# import os

# def get_home_path(subpath=""):
#     # Get the current user's home directory
#     home_dir = os.path.expanduser("~")
#     # Return the full path by appending the optional subpath
#     return os.path.join(home_dir, subpath)

# code_folder = get_home_path() + "code/"
# media_folder = get_home_path() + "media/"
# plylst_folder = get_home_path() + "media/plylst/"

# # Initialize Pygame
# pygame.init()

# # Full-screen settings
# screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)  # Set to full screen
# width, height = screen.get_size()  # Get the screen size dynamically
# pygame.display.set_caption("Morphing Graphic Display")

# # Colors
# colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0), (255, 0, 255), (0, 255, 255)]

# # Music
# pygame.mixer.music.load(media_folder + 'music/home cookin.wav')
# pygame.mixer.music.play(-1)  # Play the music in a loop

# # Function to draw a morphing circle
# def draw_morphing_circles(screen, time):
#     for i in range(8):
#         angle = math.radians(time * 50 + i * 45)
#         x = int(width / 2 + math.sin(angle) * 200)
#         y = int(height / 2 + math.cos(angle) * 200)
#         radius = int(50 + 30 * math.sin(time + i))
#         color = random.choice(colors)
#         pygame.draw.circle(screen, color, (x, y), radius, 5)

# # Main loop
# running = True
# clock = pygame.time.Clock()

# while running:
#     screen.fill((0, 0, 0))  # Clear the screen
#     time = pygame.time.get_ticks() / 1000.0  # Get the elapsed time in seconds
    
#     draw_morphing_circles(screen, time)

#     pygame.display.flip()  # Update the display

#     for event in pygame.event.get():
#         if event.type == pygame.QUIT:
#             running = False

#     clock.tick(60)  # Limit the frame rate to 60 FPS

# pygame.quit()


import pygame as pg
import random
import math

vec2, vec3 = pg.math.Vector2, pg.math.Vector3

RES = WIDTH, HEIGHT = 1600, 900
NUM_STARS = 1500
CENTER = vec2(WIDTH // 2, HEIGHT // 2)
COLORS = 'red green blue orange purple cyan'.split()
Z_DISTANCE = 40
ALPHA = 120


class Star:
    def __init__(self, app):
        self.screen = app.screen
        self.pos3d = self.get_pos3d()
        self.vel = random.uniform(0.05, 0.25)
        self.color = random.choice(COLORS)
        self.screen_pos = vec2(0, 0)
        self.size = 10

    def get_pos3d(self, scale_pos=35):
        angle = random.uniform(0, 2 * math.pi)
        radius = random.randrange(HEIGHT // scale_pos, HEIGHT) * scale_pos
        x = radius * math.cos(angle)
        y = radius * math.sin(angle)
        return vec3(x, y, Z_DISTANCE)

    def update(self):
        self.pos3d.z -= self.vel
        self.pos3d = self.get_pos3d() if self.pos3d.z < 1 else self.pos3d

        self.screen_pos = vec2(self.pos3d.x, self.pos3d.y) / self.pos3d.z + CENTER
        self.size = (Z_DISTANCE - self.pos3d.z) / (0.2 * self.pos3d.z)
        # rotate xy
        self.pos3d.xy = self.pos3d.xy.rotate(0.2)
        # mouse
        # mouse_pos = CENTER - vec2(pg.mouse.get_pos())
        # self.screen_pos += mouse_pos

    def draw(self):
        s = self.size
        if (-s < self.screen_pos.x < WIDTH + s) and (-s < self.screen_pos.y < HEIGHT + s):
            pg.draw.rect(self.screen, self.color, (*self.screen_pos, self.size, self.size))


class Starfield:
    def __init__(self, app):
        self.stars = [Star(app) for i in range(NUM_STARS)]

    def run(self):
        [star.update() for star in self.stars]
        self.stars.sort(key=lambda star: star.pos3d.z, reverse=True)
        [star.draw() for star in self.stars]


class App:
    def __init__(self):
        self.screen = pg.display.set_mode(RES)
        self.alpha_surface = pg.Surface(RES)
        self.alpha_surface.set_alpha(ALPHA)
        self.clock = pg.time.Clock()
        self.starfield = Starfield(self)

    def run(self):
        while True:
            # self.screen.fill('black')
            self.screen.blit(self.alpha_surface, (0, 0))
            self.starfield.run()

            pg.display.flip()
            [exit() for i in pg.event.get() if i.type == pg.QUIT]
            self.clock.tick(60)


if __name__ == '__main__':
    app = App()
    app.run()