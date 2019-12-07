from fundo import Particle, Universe, random_tuple
from random import choice

if __name__ == "__main__":
    u = Universe(edges="bouncy", friction=0.9, gravity=80, electromagnetism=1)

    azul =   {"mass":    100.0,
                "charge":  0.0,
                "color":   (255, 80, 80)}
    branco =  {"mass":    100.0,
                "charge":  0.0,
                "color":   (50, 205, 50)}
    vermelho = {"mass":    1.0,
                "charge": 0.0,
                "color":   (128, 128, 128)}

    for p in [azul, branco, vermelho]:
        for _ in range(10):
            u.add_molecula(pos=random_tuple(100), vel=random_tuple(100), **p)

    u.loop()

