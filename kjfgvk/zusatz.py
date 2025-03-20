import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import csv
import tkinter as tk
from tkinter import filedialog

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
        offset = joint.pos - center
        rotation_matrix = np.array([
            [np.cos(angle), -np.sin(angle)],
            [np.sin(angle),  np.cos(angle)]
        ])
        joint.pos = center + rotation_matrix @ offset

    def project_length_constraint(self, link):
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

    def cyclic_coordinate_descent(self):
        for _ in range(10):
            for link in self.links:
                self.project_length_constraint(link)

    def solve_positions(self):
        for link in self.links:
            j1 = link.joint1
            j2 = link.joint2

            if j1.fixed and not j2.fixed:
                dx = j2.pos[0] - j1.pos[0]
                dy = j2.pos[1] - j1.pos[1]
                angle = np.arctan2(dy, dx) + self.crank_speed
                self.rotate_joint(j2, j1.pos, angle - np.arctan2(dy, dx))
            elif j2.fixed and not j1.fixed:
                dx = j1.pos[0] - j2.pos[0]
                dy = j1.pos[1] - j2.pos[1]
                angle = np.arctan2(dy, dx) + self.crank_speed
                self.rotate_joint(j1, j2.pos, angle - np.arctan2(dy, dx))

        self.cyclic_coordinate_descent()

    def update(self, frame):
        self.theta += self.crank_speed
        self.solve_positions()

        tracked_joint = self.joints[-1]
        self.trace.append(tracked_joint.pos.copy())

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

        button = tk.Button(text="Abmelden", command=self.logout)
        button.pack()

        plt.show()

    def logout(self):
        print("Zurück zum Login-Screen")

    def save_trace_to_csv(self, filename):
        with open(filename, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['X', 'Y'])
            for point in self.trace:
                writer.writerow(point)

    def load_from_csv(self, filename):
        self.joints = []
        self.links = []
        with open(filename, mode='r') as file:
            reader = csv.reader(file)
            next(reader)
            joints = []
            for row in reader:
                x, y, fixed = float(row[0]), float(row[1]), row[2] == 'True'
                joints.append(self.add_joint(x, y, fixed))
            for i in range(len(joints) - 1):
                self.add_link(joints[i], joints[i + 1])

    def export_bill_of_materials(self, filename):
        with open(filename, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['Joint 1 (X, Y)', 'Joint 2 (X, Y)', 'Length'])
            for link in self.links:
                writer.writerow([
                    f'({link.joint1.pos[0]}, {link.joint1.pos[1]})',
                    f'({link.joint2.pos[0]}, {link.joint2.pos[1]})',
                    f'{link.length:.2f}'
                ])

# Beispiel
mechanism = Mechanism(crank_speed=0.1)
j1 = mechanism.add_joint(0, 0, fixed=True)
j2 = mechanism.add_joint(10, 0)
j3 = mechanism.add_joint(20, 0)

mechanism.add_link(j1, j2)
mechanism.add_link(j2, j3)

# Starten der Animation
mechanism.animate()
