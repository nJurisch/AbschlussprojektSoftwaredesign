import berechnung as br
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import streamlit as st
import streamlit.components.v1 as components
from scipy.optimize import fsolve
from scipy.optimize import least_squares

class Joint:
    def __init__(self, x, y, fixed=False):
        self.pos = np.array([x, y], dtype=float)
        self.fixed = fixed
    
    def __repr__(self):
        # Lesbare Darstellung des Gelenks
        return f"Joint(pos={self.pos.tolist()}, fixed={self.fixed})"
    


class Link:
    def __init__(self, joint1, joint2):
        self.joint1 = joint1
        self.joint2 = joint2
        self.length = np.linalg.norm(joint1.pos - joint2.pos)

    def __repr__(self):
        # Lesbare Darstellung des Links
        return f"Link({self.joint1} <-> {self.joint2})"

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
    
    def from_data(self, data):
        # Fügt alle Gelenke hinzu
        for joint_data in data["joints"]:
            self.add_joint(joint_data["x"], joint_data["y"], joint_data["fixed"])

        # Fügt alle Verbindungen hinzu
        for link_data in data["links"]:
            joint1 = self.joints[link_data[0]]
            joint2 = self.joints[link_data[1]]
            self.add_link(joint1, joint2)

    def solve_positions(self):
        """ Berechnet die Positionen der beweglichen Gelenke mit least_squares() """
        movable_joints = [j for j in self.joints if not j.fixed]

        if not movable_joints:
            return

        def equations(positions):
            positions = positions.reshape(-1, 2)
            eqs = []
            joint_positions = {joint: joint.pos.copy() for joint in self.joints if joint.fixed}  # Kopien für Stabilität

            # Aktualisiere die Positionen der beweglichen Gelenke
            for i, joint in enumerate(movable_joints):
                joint_positions[joint] = positions[i].copy()

            # Gleichungen für alle Verbindungen
            for link in self.links:
                pos1 = joint_positions[link.joint1]
                pos2 = joint_positions[link.joint2]

                # Sicherstellen, dass link.length existiert
                if not hasattr(link, "length"):
                    link.length = np.linalg.norm(link.joint2.pos - link.joint1.pos)  

                eqs.append((pos2[0] - pos1[0])**2 + (pos2[1] - pos1[1])**2 - link.length**2)

            return np.array(eqs)

        # Startwerte für die Optimierung
        initial_guess = np.array([j.pos for j in movable_joints]).flatten()

        # Kleine Störung für bessere Konvergenz
        initial_guess += np.random.normal(0, 0.01, size=initial_guess.shape)

        # Nutze 'trf' statt 'lm', um Shape-Fehler zu vermeiden
        result = least_squares(equations, initial_guess, method='trf')

        if result.success:
            solved_positions = result.x.reshape(-1, 2)
            for i, joint in enumerate(movable_joints):
                joint.pos = solved_positions[i]
        else:
            print("Lösung nicht gefunden:", result.message)
            print("Residuen:", result.fun)  # Debugging-Ausgabe



    def update(self, frame):
        """ Aktualisiert die Mechanismus-Position für die Animation """
        self.theta = (self.theta + self.crank_speed) % (2 * np.pi)
        self.joints[1].pos = self.joints[0].pos + np.array([np.cos(self.theta), np.sin(self.theta)]) * self.links[0].length
        self.solve_positions()

        #Bahnkurve von Gelenk H speichern
        tracked_joint = self.joints[7]  # Gelenk H (Index anpassen, falls anderes Gelenk gewünscht)
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
        return ani


data_strandbeest = {
    "joints": [
        {"x": 10.0, "y": 0.0, "fixed": True},
        {"x": 14.8, "y": -1.3, "fixed": False},
        {"x": -3.0, "y": 0.0, "fixed": True},
        {"x": 3.7, "y": 8.7, "fixed": False},
        {"x": -12.1, "y": 6.2, "fixed": False},
        {"x": -9.6, "y": -4.6, "fixed": False},
        {"x": -0.5, "y": -10.7, "fixed": False},
        {"x": -4.9, "y": -24.0, "fixed": False}
    ],
    "links": [
        [0, 1], [1, 3], [1, 6], [2, 4], [2, 3], [2, 6], [3, 4],
        [4, 5], [4, 6], [4, 7], [6, 7], [5, 6]
    ]
}

mechanism_fd = Mechanism(crank_speed=0.05)
mechanism_fd.from_data(data_strandbeest)

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

mechanism_fd.solve_positions() # Wichtig, um die Startpositionen zu berechnen
mechanism.solve_positions()

mech_ani_fd = mechanism_fd.animate()
mech_ani = mechanism.animate()


st.title("Embed Matplotlib animation in Streamlit")
st.markdown("https://matplotlib.org/gallery/animation/basic_example.html")
components.html(mech_ani.to_jshtml(), height=1000)