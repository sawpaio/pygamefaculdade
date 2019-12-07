from collections import deque
from hashlib import sha256
from numpy import array


def _clamp(n, smallest, largest):
    return max(smallest, min(n, largest))


class Particle():
    def __init__(self,
                 pos=(100, 0),
                 vel=(100, 0),
                 mass=1,
                 charge=0,
                 color=None):
        # set position, velocity and space
        self.pos = array(pos, dtype="float64")
        self.vel = array(vel, dtype="float64")
        
        # set mass and charge
        self.mass = float(mass)
        self.charge = float(charge)

        # set a color
        self.color = color or self.get_hash_color()

        # keep position log
        self.positions = deque([tuple(self.pos)], 200)

    def __str__(self):
        return (f"pos[{self.pos[0]:#6.1f}|{self.pos[0]:#6.1f}] "
                f"vel[{self.vel[0]:#6.1f}|{self.vel[0]:#6.1f}] "
                f"mass[{self.mass:#6.1f}] "
                f"charge[{self.charge:#6.1f}]")
        pass

    def get_hash_color(self):
        hash = sha256(bytes(str(self.mass) +
                            str(self.charge) +
                            str(self.mass + self.charge) +
                            str(self.mass * self.charge) +
                            "qwfnvoiskfj XXX YES XXX 0xF00DBABE XXX jpcd", "utf-8")).digest()[0:3]
        return (hash[0] | (1 << 7), hash[1] | (1 << 7), hash[2] | (1 << 7))  # turn on HSB for light colors

    def apply_force(self, force, time):
        self.accelerate(array(force, dtype="float64") / self.mass, time)
        pass

    def accelerate(self, acc, time):
        self.vel += array(acc, dtype="float64") * time
        pass

    def move(self, time):
        self.pos += (self.vel * time)
        self.positions.append(tuple(self.pos))

    def tick(self, time, space=None, edges: {"clamp", "torus", "bouncy"}=None):
        # move it
        self.move(time)

        # keep itself in space
        if space is not None and edges is not None:
            for i in range(2):
                if not (-space[i] / 2 < self.pos[i] <= space[i] / 2):
                    self.pos[i] = _clamp(self.pos[i], -space[i] / 2, space[i] / 2)
                    if edges == "clamp":
                        # stop particles from moving further
                        self.vel[i] = 0
                    elif edges == "torus":
                        # wrap current coordinate
                        self.pos[i] *= -1
                    elif edges == "bouncy":
                        # invert direction of traveling if its out of bounds
                        self.vel[i] *= -1
