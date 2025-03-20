import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import time
from mechanism import Mechanism
from database import Database

# Initialisieren
mechanism = Mechanism()
db = Database()

st.title("Mechanismus Simulation")

# Eingabe für Gelenke
x = st.number_input("X-Koordinate", value=0.0)
y = st.number_input("Y-Koordinate", value=0.0)
fixed = st.checkbox("Fixiert")
if st.button("Gelenk hinzufügen"):
    mechanism.add_joint(x, y, fixed)

# Eingabe für Glieder
if len(mechanism.joints) >= 2:
    joint_a = st.selectbox("Gelenk A", range(len(mechanism.joints)))
    joint_b = st.selectbox("Gelenk B", range(len(mechanism.joints)))
    if st.button("Glied hinzufügen"):
        mechanism.add_link(mechanism.joints[joint_a], mechanism.joints[joint_b])

# Simulation starten
if st.button("Simulation starten"):
    mechanism.solve()

# Echtzeit-Animation
if len(mechanism.links) > 0:
    fig, ax = plt.subplots()
    progress_bar = st.progress(0)

    for angle in np.linspace(0, 2 * np.pi, 100):
        for joint in mechanism.joints:
            if not joint.fixed:
                joint.x += 0.1 * np.cos(angle)
                joint.y += 0.1 * np.sin(angle)

        ax.clear()
        for link in mechanism.links:
            x_values = [link.joint_a.x, link.joint_b.x]
            y_values = [link.joint_a.y, link.joint_b.y]
            ax.plot(x_values, y_values, 'o-')

        ax.set_xlim(-10, 10)
        ax.set_ylim(-10, 10)

        st.pyplot(fig)
        time.sleep(0.05)

        progress_bar.progress(int(angle / (2 * np.pi) * 100))

# Speichern und Laden
if st.button("Speichern"):
    db.save_mechanism(mechanism)
if st.button("Laden"):
    db.load_mechanism(mechanism)
    st.success("Mechanismus geladen!")
