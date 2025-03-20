import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

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

    def rotate_joint(self, joint, center, angle):
        """ Rotiert ein Gelenk um ein anderes Gelenk mit einer Rotationsmatrix """
        offset = joint.pos - center
        rotation_matrix = np.array([
            [np.cos(angle), -np.sin(angle)],
            [np.sin(angle),  np.cos(angle)]
        ])
        new_offset = rotation_matrix @ offset
        joint.pos = center + new_offset

    def project_length_constraint(self, link):
        """
        Erzwinge die Länge der Verbindung, indem die Gelenke entlang der Verbindungslinie angepasst werden.
        """
        j1 = link.joint1
        j2 = link.joint2
        
        dx = j2.pos[0] - j1.pos[0]
        dy = j2.pos[1] - j1.pos[1]
        dist = np.sqrt(dx**2 + dy**2)

        if dist == 0:
            return
        
        correction_factor = link.length / dist
        midpoint = (j1.pos + j2.pos) / 2
        
        if not j1.fixed:
            j1.pos = midpoint + correction_factor * (j1.pos - midpoint)
        if not j2.fixed:
            j2.pos = midpoint + correction_factor * (j2.pos - midpoint)

    def solve_positions(self):
        """
        Iterative Lösung der Kinematik unter Berücksichtigung der Zwangsbedingungen.
        """
        for _ in range(10):  # Mehrere Iterationen für Konvergenz
            for link in self.links:
                j1 = link.joint1
                j2 = link.joint2
                
                if j1.fixed and not j2.fixed:
                    # Bewegung von j2 um j1 unter Berücksichtigung der Länge
                    dx = j2.pos[0] - j1.pos[0]
                    dy = j2.pos[1] - j1.pos[1]
                    current_angle = np.arctan2(dy, dx)
                    target_angle = current_angle + self.crank_speed
                    
                    self.rotate_joint(j2, j1.pos, target_angle - current_angle)
                    self.project_length_constraint(link)

                elif j2.fixed and not j1.fixed:
                    # Bewegung von j1 um j2 unter Berücksichtigung der Länge
                    dx = j1.pos[0] - j2.pos[0]
                    dy = j1.pos[1] - j2.pos[1]
                    current_angle = np.arctan2(dy, dx)
                    target_angle = current_angle + self.crank_speed
                    
                    self.rotate_joint(j1, j2.pos, target_angle - current_angle)
                    self.project_length_constraint(link)

                elif not j1.fixed and not j2.fixed:
                    # Beide Gelenke beweglich -> Länge erhalten
                    self.project_length_constraint(link)

    def update(self, frame):
        self.theta += self.crank_speed

        # Unbegrenzte Rotation über 2π hinaus
        if self.theta > 2 * np.pi:
            self.theta -= 2 * np.pi

        self.solve_positions()

        # Spur speichern
        tracked_joint = self.joints[-1]
        self.trace.append(tracked_joint.pos.copy())

        # Verbindungslinien für Anzeige
        link_xs = []
        link_ys = []
        for link in self.links:
            link_xs.extend([link.joint1.pos[0], link.joint2.pos[0], None])
            link_ys.extend([link.joint1.pos[1], link.joint2.pos[1], None])

        self.line.set_data(link_xs, link_ys)

        if len(self.trace) > 1:
            trace_xs, trace_ys = zip(*self.trace)
            self.trace_line.set_data(trace_xs, trace_ys)

        return self.line, self.trace_line

    def animate(self):
        fig, ax = plt.subplots()
        ax.set_xlim(-50, 50)
        ax.set_ylim(-50, 50)

        self.line, = ax.plot([], [], 'k-', lw=2)
        self.trace_line, = ax.plot([], [], 'r-', lw=1)

        ani = FuncAnimation(fig, self.update, frames=360, interval=20, blit=True)

        return ani