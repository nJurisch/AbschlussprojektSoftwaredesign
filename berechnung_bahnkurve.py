import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from scipy.optimize import fsolve

class Joint:
    def __init__(self, x, y, fixed=False):
        self.pos = np.array([x, y], dtype=float)
        self.fixed = fixed

class Link:
    def __init__(self, joint1, joint2, length):
        self.joint1 = joint1
        self.joint2 = joint2
        self.length = length

class Mechanism:
    def __init__(self, crank_speed):
        self.joints = []
        self.links = []
        self.crank_speed = crank_speed
        self.theta = 0

    def add_joint(self, x, y, fixed=False):
        joint = Joint(x, y, fixed)
        self.joints.append(joint)
        return joint

    def add_link(self, joint1, joint2):
        length = np.linalg.norm(joint1.pos - joint2.pos)
        link = Link(joint1, joint2, length)
        self.links.append(link)
        return link

    def solve_positions(self):
        """ Berechnet die Positionen der beweglichen Gelenke """
        def equations(positions):
            positions = positions.reshape(-1, 2)
            eqs = []
            for i, link in enumerate(self.links):
                if not (link.joint1.fixed and link.joint2.fixed):
                    x1, y1 = positions[self.joints.index(link.joint1)]
                    x2, y2 = positions[self.joints.index(link.joint2)]
                    eqs.append((x2 - x1) ** 2 + (y2 - y1) ** 2 - link.length ** 2)
            return np.concatenate(eqs)
        
        movable_joints = [j for j in self.joints if not j.fixed]
        initial_guess = np.array([j.pos for j in movable_joints]).flatten()
        solved_positions = fsolve(equations, initial_guess).reshape(-1, 2)
        for i, joint in enumerate(movable_joints):
            joint.pos = solved_positions[i]

    def update(self, frame):
        """ Aktualisiert die Mechanismus-Position für die Animation """
        self.theta = (self.theta + self.crank_speed) % (2 * np.pi)
        self.joints[1].pos = self.joints[0].pos + np.array([np.cos(self.theta), np.sin(self.theta)]) * self.links[0].length
        self.solve_positions()
        self.line.set_data([j.pos[0] for j in self.joints], [j.pos[1] for j in self.joints])
        #test
        print([j.pos for j in self.joints])

        return self.line,

    def animate(self):
        """ Erstellt die Matplotlib-Animation """
        fig, ax = plt.subplots()
        ax.set_xlim(-10, 10)
        ax.set_ylim(-10, 10)
        self.line, = ax.plot([], [], 'o-', lw=2)
        ani = animation.FuncAnimation(fig, self.update, frames=360, interval=20, blit=False)
        plt.show()

# Mechanismus erstellen
mechanism = Mechanism(crank_speed=0.05)
A = mechanism.add_joint(0, 0, fixed=True)  # Fixpunkt
B = mechanism.add_joint(2, 0)  # Kurbel
C = mechanism.add_joint(4, 0, fixed=True)  # Fixiertes Gelenk
D = mechanism.add_joint(3, 2)  # Bewegliches Gelenk

mechanism.add_link(A, B)
mechanism.add_link(B, D)
mechanism.add_link(D, C)

mechanism.animate()



