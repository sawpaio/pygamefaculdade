from itertools import combinations
from numpy import array, dot
from numpy.linalg import norm
from moleculas import Particle
from random import random
from collections import deque
from time import sleep, time
import pygame


BACKGROUND = (0, 0, 0)
FOREGROUND = (255, 255, 255)


def random_tuple(max_x, max_y=None):
    max_y = max_y or max_x
    return array((max_x * (2 * random() - 1), max_y * (2 * random() - 1)))


class Universe():
    def __init__(self,
                 tamanho=(500, 500),
                 edges: {"clamp", "torus", "bouncy"}="bouncy",
                 friction=0,
                 gravity=10,
                 electromagnetism=1):
        # graphical settings
        self.particle_radius = 6

        # universe settings
        self.space = array(tamanho, dtype="float64")  # total positions in x/y-direction
        self.edges = edges  # type of edges the universe will have
        self.particles = []  # empty particle list
        self.friction = float(friction)  # friction in the system
        self.gravity = float(gravity)  # the strength of gravity
        self.electromagnetism = float(electromagnetism)  # the strength of electromagnetism

        # for pygame display
        pygame.init()
        self.screen = pygame.display.set_mode(tamanho, pygame.RESIZABLE)
        self.font = pygame.font.SysFont("Consolas", 14)
        self.render_text = lambda pos, string, color, antialias: self.screen.blit(self.font.render(string, antialias, color), pos)

        # for fps
        self.frames = deque([0], 60)

    def add_molecula(self, *args, **kwargs):
        self.particles.append(Particle(*args, **kwargs))

    def pos_to_px(self, pos):
        pos_ = array((pos[0], -pos[1]))
        return array((self.space / 2 + pos_), dtype="int32")

    def pos_to_px_list(self, pos_list):
        res = []
        for pos in pos_list:
            res.append(self.pos_to_px(pos))
        return res

    def draw(self, info_str="", show_trace=False):
        # clear screen
        self.screen.fill(BACKGROUND)

        # draw particles
        for p in self.particles:
            pygame.draw.circle(self.screen, p.color, self.pos_to_px(p.pos), self.particle_radius)
            if show_trace and len(p.positions) > 1:
                pygame.draw.lines(self.screen, p.color, False, self.pos_to_px_list(p.positions), self.particle_radius//3)
        pygame.draw.circle(self.screen, FOREGROUND, array(self.space/2, dtype="int32"), 3)
        self.render_text((3, 3), info_str, FOREGROUND, True)
        pygame.display.flip()

        # update fps
        delta = time() - self.frames[-1]
        if delta < 1.0 / 60.0:
            sleep(1.0 / 60.0 - delta)
        self.frames.append(time())
        return len(self.frames) // (self.frames[-1] - self.frames[0])

    def tick(self, dt):
        # apply all forces the particles have on each other
        for p1, p2 in combinations(self.particles, r=2):
            # collision
            dpos = p2.pos - p1.pos
            dist = norm(dpos)
            if dist < 2 * self.particle_radius:
                # see https://en.wikipedia.org/wiki/Elastic_collision
                v1, v2 = array(p1.vel), array(p2.vel)
                m1, m2 = p1.mass, p2.mass
                dvel = v2 - v1
                x = 2 / (m1 + m2) * dpos * dot(dvel, dpos) / dist ** 2
                p1.vel += m2 * x
                p2.vel -= m1 * x

            # gravity and charge
            else:
                force = dpos * (self.gravity * p1.mass * p2.mass - self.electromagnetism * p1.charge * p2.charge) / (dist ** 2) 
                p1.apply_force(+force, dt)
                p2.apply_force(-force, dt)
            
        # move all particles
        for p in self.particles:
            # friction
            p.vel *= (self.friction ** dt)

            # move all particles
            p.tick(dt, space=self.space, edges=self.edges)
    
    def loop(self, show_trace=False, ffw=False, step=1.0/60.0):
        # print controls
        print("MENU")
        print("t:   caminho da molecula")
        print("k/l: aumenta/diminui velocidade")
        print("q:   exit")
        print("")

        fps = 0
        done = False  # loop condition
        shift = ctrl = alt = False  # modifier
        while not done:
            setting_str = f"step:{step*1000:5.2f} | fps:{fps:3.0f} | trace:{'true ' if show_trace else 'false'}"
            print(setting_str, end="\r")
            # process events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    done = True
                elif event.type == pygame.VIDEORESIZE:
                    self.space = array(event.size)
                    self.screen = pygame.display.set_mode(self.space, pygame.RESIZABLE)
                elif event.type == pygame.KEYDOWN:
                    # increase/decrease delay
                    if event.key == pygame.K_l:
                        step /= 1.2
                    elif event.key == pygame.K_k:
                        step *= 1.2
                    # show trace
                    elif event.key == pygame.K_t:
                        show_trace = not show_trace
                    # exit
                    elif event.key == pygame.K_q:
                        done = True
                    # modifier (kinda flawed, but good enough)
                    elif event.key == pygame.K_LSHIFT or event.key == pygame.K_RSHIFT:
                        shift = True
                    elif event.key == pygame.K_LCTRL or event.key == pygame.K_RCTRL:
                        ctrl = True
                    elif event.key == pygame.K_LALT or event.key == pygame.K_RALT:
                        alt = True
                elif event.type == pygame.KEYUP:
                    # show trace
                    if not shift and event.key == pygame.K_t:
                        show_trace = not show_trace
                    # modifier (kinda flawed, but good enough)
                    elif event.key == pygame.K_LSHIFT or event.key == pygame.K_RSHIFT:
                        shift = False
                    elif event.key == pygame.K_LCTRL or event.key == pygame.K_RCTRL:
                        ctrl = False
                    elif event.key == pygame.K_LALT or event.key == pygame.K_RALT:
                        alt = False


            # tick
            self.tick(step)
            fps = self.draw(setting_str, show_trace)
