import pygame
import os
import glob

class Settings(object):
    window_height = 500
    window_width = 800

    base_file = os.path.dirname(os.path.abspath(__file__))
    path_assets = os.path.join(base_file, "assets")
    path_image = os.path.join(path_assets, "images")
    path_animations = os.path.join(path_image, "animations")
    title = "Fighter - Animations"

    player_size = (33,90)
    player_animations = [
        'idle',
        'jump',
        'punsh',
        'lower_punsh',
        'kick',
        'lower_kick'
    ]

    background_image = 'background.png'
    fps = 60

class Timer(object):
    def __init__(self, duraton, with_start=True):
        self.duraton = duraton
        if with_start:
            self.next = pygame.time.get_ticks()
        else:
            self.next = pygame.time.get_ticks() + self.duraton

    def is_next_stop_reached(self):
        if pygame.time.get_ticks() > self.next:
            self.next = pygame.time.get_ticks() + self.duraton
            return True
        return False

class Background(pygame.sprite.Sprite):
    def __init__(self, filename):
        super().__init__()
        self.image = pygame.image.load(os.path.join(Settings.path_image, filename)).convert()
        self.image = pygame.transform.scale(self.image, (Settings.window_width, Settings.window_height))

    def draw(self, screen):
        screen.blit(self.image, (0,0))

class Player(pygame.sprite.Sprite):
    def __init__(self, fallback_action='idle'):
        self.fallback_image = 'fallback.png'
        self.fallback_action = fallback_action
        self.actions = { "current_action": None, "current_action_loop": False, "next_action": None, "next_action_loop": False }
        self.current_frame = 0
        self.animations = {}
        self.current_animation = { "count": 0, "frames": [], "name": "" }
        self.animation_timer = Timer(100)

        self.change_action(self.fallback_action, True)
        self.update_sprite(self.fallback_image)
        self.load_animations()

    def set_pos(self, x, y):
        self.rect.top = y
        self.rect.left = x

    def update_sprite(self, filename):
        self.image = pygame.image.load(os.path.join(Settings.path_image, filename)).convert_alpha()
        self.size =  self.image.get_size()
        self.image = pygame.transform.scale(self.image, self.size)
        self.rect = self.image.get_rect()
        self.set_pos(Settings.window_width // 2 - (self.size[0] // 2), Settings.window_height - 25 - self.size[1])

    def play_animation(self):
        if self.current_frame >= self.current_animation['count']:
            if self.actions['current_action_loop'] != True:
                self.change_action(self.fallback_action, True)
            self.current_frame = 0
        else:
            self.current_frame += 1

        current_frame = os.path.join(Settings.path_animations, self.current_animation['name'], self.current_animation['frames'][self.current_frame])
        self.update_sprite(current_frame)

    def load_animations(self):
        for animation in Settings.player_animations:
            raw_frames = glob.glob(os.path.join(Settings.path_animations, animation) + "/*.png")
            frames = [ os.path.basename(frame).split('.')[0] for frame in raw_frames ]
            frames.sort(key=int)
            self.animations[animation] = [ frame + '.png' for frame in frames ]
        print(self.animations)

    def change_action(self, action, loop=False):
        self.actions['next_action'] = action
        self.actions['next_action_loop'] = loop
        print(f"Next Action queued: {action} (Loop: {loop})")

    def change_animation(self):
        self.current_animation['frames'] = self.animations[self.actions['current_action']]
        self.current_animation['count'] = len(self.current_animation['frames']) - 1
        self.current_animation['name'] = self.actions['current_action']

    def update(self):
        if self.actions['next_action'] != self.actions['current_action']:
            if self.current_frame == 0:
                self.actions['current_action'] = self.actions['next_action']
                self.actions['current_action_loop'] = self.actions['next_action_loop']
                self.change_animation()

        if self.animation_timer.is_next_stop_reached():
            if self.actions['current_action'] != None:
                self.play_animation()

    def draw(self, screen):
        screen.blit(self.image, self.rect)

class Game():
    def __init__(self):
        super().__init__()
        os.environ['SDL_VIDEO_WINDOW_POS'] = '1'
        pygame.init()
        pygame.display.set_caption(Settings.title)

        self.screen = pygame.display.set_mode((Settings.window_width, Settings.window_height))
        self.fps = pygame.time.Clock()

        self.background = Background(Settings.background_image)
        self.player = Player()

        self.running = True

    def run(self):
        while self.running:
            self.fps.tick(Settings.fps)
            self.update()
            self.draw()
            self.watch_for_events()

    def update(self):
        self.player.update()

    def draw(self):
        self.background.draw(self.screen)
        self.player.draw(self.screen)
        pygame.display.flip()

    def watch_for_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.player.change_action('jump', False)
                
                elif event.key == pygame.K_e:
                    self.player.change_action('kick', False)

                elif event.key == pygame.K_q:
                    self.player.change_action('lower_kick', False)

                elif event.key == pygame.K_d:
                    self.player.change_action('punsh', False)

                elif event.key == pygame.K_a:
                    self.player.change_action('lower_punsh', False)

if __name__ == '__main__':
    game = Game()
    game.run()