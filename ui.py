import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import json
from basic_functions import Mechanism

# Streamlit UI
st.title("Mechanismus-Simulation")
st.sidebar.header("Mechanismus-Eingabe")

# Mechanismus initialisieren
example_joints = [(0, 0), (1, 1), (2, 0)]  # Beispielhafte Gelenkpunkte
example_links = [(0, 1), (1, 2)]  # Beispielhafte Verbindungen
mechanism = Mechanism(example_joints, example_links)

# Winkel-Steuerung
theta = st.sidebar.slider("Winkel (in Grad)", 0, 360, 0)
theta_rad = np.radians(theta)

# Gelenk hinzufügen
st.sidebar.subheader("Neues Gelenk hinzufügen")
new_x = st.sidebar.number_input("X-Koordinate", value=0.0)
new_y = st.sidebar.number_input("Y-Koordinate", value=0.0)
if st.sidebar.button("Gelenk hinzufügen"):
    mechanism.joints.append((new_x, new_y))
    st.sidebar.success("Neues Gelenk hinzugefügt!")
    positions = mechanism.update_mechanism(theta_rad)

# Verbindung hinzufügen
st.sidebar.subheader("Neue Verbindung hinzufügen")
all_joint_indices = list(range(len(mechanism.joints)))
if len(mechanism.joints) > 1:
    joint1 = st.sidebar.selectbox("Gelenk 1 auswählen", options=all_joint_indices, index=0)
    joint2 = st.sidebar.selectbox("Gelenk 2 auswählen", options=all_joint_indices, index=1)
    if st.sidebar.button("Verbindung hinzufügen"):
        mechanism.add_link(joint1, joint2)
        st.sidebar.success("Neue Verbindung hinzugefügt!")
        positions = mechanism.update_mechanism(theta_rad)

# Mechanismus aktualisieren
positions = mechanism.update_mechanism(theta_rad)

# Mechanismus visualisieren
fig, ax = plt.subplots()
for (i, j), length in mechanism.links.items():
    ax.plot([positions[i, 0], positions[j, 0]], [positions[i, 1], positions[j, 1]], "ro-")
ax.scatter(positions[:, 0], positions[:, 1], c='blue')
ax.set_xlim(-3, 3)
ax.set_ylim(-3, 3)
ax.set_aspect('equal')
st.pyplot(fig)

# Länge einer Verbindung ändern
st.sidebar.subheader("Länge einer Verbindung ändern")
if len(mechanism.links) > 0:
    joint1_edit = st.sidebar.selectbox("Gelenk 1 (Länge ändern)", options=all_joint_indices, index=0)
    joint2_edit = st.sidebar.selectbox("Gelenk 2 (Länge ändern)", options=all_joint_indices, index=1)
    new_length = st.sidebar.number_input("Neue Länge", min_value=0.1, value=1.0)
    if st.sidebar.button("Länge ändern"):
        mechanism.update_link_length(joint1_edit, joint2_edit, new_length)
        st.sidebar.success("Länge der Verbindung aktualisiert!")

# CSV-Export
def export_csv(positions):
    df = pd.DataFrame(positions, columns=["x", "y"])
    return df.to_csv(index=False)

if st.sidebar.button("Export CSV"):
    csv_data = export_csv(positions)
    st.sidebar.download_button(label="Download CSV", data=csv_data, file_name="mechanism_positions.csv", mime="text/csv")

# Optimierung starten
if st.sidebar.button("Optimierung starten"):
    optimized_theta = mechanism.optimize_mechanism()
    st.sidebar.write(f"Optimierter Winkel: {np.degrees(optimized_theta):.2f}°")

# Mechanismus speichern und laden
if st.sidebar.button("Mechanismus speichern"):
    mech_data = json.dumps({"joints": mechanism.joints, "links": list(mechanism.links.keys())})
    with open("mechanismus.json", "w") as f:
        f.write(mech_data)
    st.sidebar.success("Mechanismus gespeichert!")

uploaded_file = st.sidebar.file_uploader("Mechanismus laden", type="json")
if uploaded_file:
    loaded_data = json.load(uploaded_file)
    mechanism = Mechanism(loaded_data["joints"], loaded_data["links"])
    st.sidebar.success("Mechanismus geladen!")
