import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import time
import pandas as pd
from scipy.optimize import minimize

# Rotationsfunktion
def rotate_point(origin, point, angle):
    ox, oy = origin
    px, py = point

    qx = ox + np.cos(angle) * (px - ox) - np.sin(angle) * (py - oy)
    qy = oy + np.sin(angle) * (px - ox) + np.cos(angle) * (py - oy)

    return qx, qy

# Zielfunktion für die Optimierung (Stablängen konstant halten)
def objective(positions, num_joints, lengths):
    total_error = 0
    for i in range(num_joints - 1):
        x1, y1 = positions[2 * i], positions[2 * i + 1]
        x2, y2 = positions[2 * (i + 1)], positions[2 * (i + 1) + 1]
        distance = np.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
        total_error += (distance - lengths[i]) ** 2
    return total_error

# Nebenbedingungen für feste Gelenke (erstes und letztes Gelenk fixieren)
def constraint_fixed_joint(positions, fixed_positions, fixed_support):
    constraints = []
    for i, fixed in enumerate(fixed_support):
        if fixed:
            x_fixed, y_fixed = fixed_positions[i]
            x_current, y_current = positions[2 * i], positions[2 * i + 1]
            constraints.append(x_current - x_fixed)
            constraints.append(y_current - y_fixed)
    return constraints

# Nebenbedingungen für die Vermeidung von Überschneidungen der Stäbe (außer Stab 1)
def constraint_no_crossing(positions, num_joints):
    min_distance = 0.1  # Mindestabstand zwischen den Stäben
    constraints = []
    for i in range(1, num_joints - 2):  # Stab 1 wird ausgeschlossen
        x1, y1 = positions[2 * i], positions[2 * i + 1]
        x2, y2 = positions[2 * (i + 1)], positions[2 * (i + 1) + 1]
        x3, y3 = positions[2 * (i + 2)], positions[2 * (i + 2) + 1]

        # Berechnung der Abstände zwischen benachbarten Stäben
        d1 = np.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
        d2 = np.sqrt((x3 - x2) ** 2 + (y3 - y2) ** 2)

        # Mindestabstand als Nebenbedingung hinzufügen
        constraints.append(d1 - min_distance)
        constraints.append(d2 - min_distance)
    return constraints

def main():
    st.title("Kinematik-Simulation einer Gelenkstruktur")

    # Anzahl der Gelenke (mindestens 3)
    num_joints = st.number_input("Anzahl der Gelenke", min_value=3, step=1, value=4)

    if num_joints > 0:
        fixed_support = [False] * num_joints
        x_positions = [0] * num_joints
        y_positions = [0] * num_joints
        lengths = [0] * (num_joints - 1)
        paths = [[] for _ in range(num_joints)]

        st.header("Eingabe der Fixierungen und Startkoordinaten")

        for i in range(num_joints):
            col1, col2, col3 = st.columns(3)
            with col1:
                # Erstes und letztes Gelenk automatisch fixieren
                if i == 0 or i == num_joints - 1:
                    fixed_support[i] = True
                    st.text(f"Gelenk {i + 1} = fest")
                else:
                    fixed_support[i] = st.checkbox(f"Festlager für Gelenk {i + 1}", value=False, key=f"support_{i}")
            with col2:
                x_positions[i] = st.number_input(f"x-Position für Gelenk {i + 1}", value=i, key=f"x_{i}")
            with col3:
                y_positions[i] = st.number_input(f"y-Position für Gelenk {i + 1}", value=0, key=f"y_{i}")

        # Berechnung der Länge der Stäbe (nur einmal für die Startwerte)
        for i in range(num_joints - 1):
            dx = x_positions[i + 1] - x_positions[i]
            dy = y_positions[i + 1] - y_positions[i]
            lengths[i] = np.sqrt(dx**2 + dy**2)

        # 🏁 Start der Simulation
        if st.button("🔄 Starte vollständige Simulation"):
            angle_step = np.radians(2)
            total_steps = int(360 / 2)

            plot_area = st.empty()
            fig, ax = plt.subplots()

            data = []

            for step in range(total_steps):
                angle = step * angle_step

                # Stab 1 um Gelenk 1 drehen
                x_positions[1], y_positions[1] = rotate_point(
                    origin=(x_positions[0], y_positions[0]),
                    point=(x_positions[1], y_positions[1]),
                    angle=angle_step
                )

                # Optimierung der restlichen Gelenke
                initial_positions = np.array(
                    [coord for xy in zip(x_positions, y_positions) for coord in xy]
                )

                fixed_positions = list(zip(x_positions, y_positions))

                result = minimize(
                    objective,
                    initial_positions,
                    args=(num_joints, lengths),
                    constraints=[
                        {'type': 'eq', 'fun': lambda pos: constraint_fixed_joint(pos, fixed_positions, fixed_support)},
                        {'type': 'ineq', 'fun': lambda pos: constraint_no_crossing(pos, num_joints)}
                    ],
                    method='SLSQP'
                )

                optimized_positions = result.x.reshape((num_joints, 2))
                x_positions, y_positions = optimized_positions[:, 0], optimized_positions[:, 1]

                # Speicherung der Bahnkurven für nicht feste Gelenke
                for i in range(num_joints):
                    if not fixed_support[i]:
                        paths[i].append((x_positions[i], y_positions[i]))

                # Zeichnen der Gelenke und Stäbe
                ax.clear()
                ax.set_xlim(-10, 10)
                ax.set_ylim(-10, 10)
                ax.grid(True)

                for i in range(num_joints - 1):
                    color = 'red' if i == 0 else 'blue'
                    ax.plot(x_positions[i], y_positions[i], 'o', color=color, markersize=10)
                    ax.plot([x_positions[i], x_positions[i + 1]], [y_positions[i], y_positions[i + 1]], color=color)

                for i in range(num_joints):
                    if not fixed_support[i] and len(paths[i]) > 1:
                        path_x, path_y = zip(*paths[i])
                        ax.plot(path_x, path_y, linestyle="--", color="gray", alpha=0.7)

                plot_area.pyplot(fig)
                time.sleep(0.01)

if __name__ == "__main__":
    main()










