import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from scipy.optimize import fsolve
from scipy.optimize import least_squares

class Joint:
    def __init__(self, x, y, fixed=False):
        self.pos = np.array([x, y], dtype=float)
        self.fixed = fixed

class Link:
    def __init__(self, joint1, joint2):
        self.joint1 = joint1
        self.joint2 = joint2
        self.length = np.linalg.norm(joint1.pos - joint2.pos)

class Mechanism:
    def __init__(self, crank_speed):
        self.joints = []
        self.links = []
        self.crank_speed = crank_speed
        self.theta = 0
        self.trace = [] 

    def add_joint(self, x, y, fixed=False):
        joint = Joint(x, y, fixed)
        self.joints.append(joint)
        return joint

    def add_link(self, joint1, joint2):
        link = Link(joint1, joint2)
        self.links.append(link)
        return link

    def solve_positions(self):
        """ Berechnet die Positionen der beweglichen Gelenke mit least_squares() """
        movable_joints = [j for j in self.joints if not j.fixed]

        if not movable_joints:
            return

        def equations(positions):
            positions = positions.reshape(-1, 2)
            eqs = []
            joint_positions = {joint: joint.pos for joint in self.joints if joint.fixed}

            # Aktualisiere die Positionen der beweglichen Gelenke
            for i, joint in enumerate(movable_joints):
                joint_positions[joint] = positions[i]

            # Gleichungen für alle Verbindungen
            for link in self.links:
                pos1 = joint_positions[link.joint1]
                pos2 = joint_positions[link.joint2]
                eqs.append((pos2[0] - pos1[0])**2 + (pos2[1] - pos1[1])**2 - link.length**2)

            return np.array(eqs)

        # Startwerte für die Optimierung
        initial_guess = np.array([j.pos for j in movable_joints]).flatten()

        # Nutze 'trf' statt 'lm', um Shape-Fehler zu vermeiden
        result = least_squares(equations, initial_guess, method='trf')

        if result.success:
            solved_positions = result.x.reshape(-1, 2)
            for i, joint in enumerate(movable_joints):
                joint.pos = solved_positions[i]
        else:
            print("Lösung nicht gefunden:", result.message)



    def update(self, frame):
        """ Aktualisiert die Mechanismus-Position für die Animation """
        self.theta = (self.theta + self.crank_speed) % (2 * np.pi)
        self.joints[1].pos = self.joints[0].pos + np.array([np.cos(self.theta), np.sin(self.theta)]) * self.links[0].length
        self.solve_positions()

        #Bahnkurve von Gelenk D speichern
        tracked_joint = self.joints[7]  # Gelenk D (Index anpassen, falls anderes Gelenk gewünscht)
        self.trace.append(tracked_joint.pos.copy())

        # Links als Linien zeichnen
        link_xs = []
        link_ys = []
        for link in self.links:
            link_xs.extend([link.joint1.pos[0], link.joint2.pos[0], None])
            link_ys.extend([link.joint1.pos[1], link.joint2.pos[1], None])

        self.line.set_data(link_xs, link_ys)

        trace_xs, trace_ys = zip(*self.trace)
        self.trace_line.set_data(trace_xs, trace_ys)

        return self.line, self.trace_line


    def animate(self):
        """ Erstellt die Matplotlib-Animation """
        fig, ax = plt.subplots()
        ax.set_xlim(-50, 50)
        ax.set_ylim(-50, 50)

        self.line, = ax.plot([], [], 'k-', lw=2)  # Mechanismus-Linien
        self.trace_line, = ax.plot([], [], 'r-', lw=1)  #Bahnkurve in Rot

        ani = animation.FuncAnimation(fig, self.update, frames=360, interval=20, blit=False)
        plt.show()

# Mechanismus erstellen
mechanism = Mechanism(crank_speed=0.05)
A = mechanism.add_joint(10, 0, fixed=True)  # Fixpunkt
B = mechanism.add_joint(14.8, -1.3)  # Kurbel
C = mechanism.add_joint(-3, 0, fixed=True)  # Fixiertes Gelenk
D = mechanism.add_joint(3.7, 8.7)  # Bewegliches Gelenk
E = mechanism.add_joint(-12.1, 6.2)  # Bewegliches Gelenk
F = mechanism.add_joint(-9.6, -4.6)  # Bewegliches Gelenk
G = mechanism.add_joint(-0.5, -10.7)  # Bewegliches Gelenk
H = mechanism.add_joint(-4.9, -24)  # Bewegliches Gelenk

mechanism.add_link(A, B)
mechanism.add_link(B, D)
mechanism.add_link(B, G)
mechanism.add_link(C, E)
mechanism.add_link(C, D)
mechanism.add_link(C, G)
mechanism.add_link(D, E)
mechanism.add_link(F, E)
mechanism.add_link(F, G)
mechanism.add_link(F, H)
mechanism.add_link(H, G)


mechanism.solve_positions()  # Wichtig, um die Startpositionen zu berechnen

mechanism.animate()
