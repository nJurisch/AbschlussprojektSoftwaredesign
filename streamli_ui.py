import streamlit as st
import json
import os
import matplotlib.pyplot as plt
from mechanism import Mechanism
from simulation import MechanismSimulator
from kinematik_optimization import KinematicsAnalyzer
from link_optimization import MechanismOptimizer

# Temporärer Speicher für Gelenke und Verbindungen
if "mechanism_data" not in st.session_state:
    st.session_state.mechanism_data = {"joints": [], "links": []}

def plot_mechanism(joints, links):
    """Erstellt eine visuelle Darstellung des Mechanismus."""
    fig, ax = plt.subplots()
    for link in links:
        j1 = next(j for j in joints if j["name"] == link["joint1"])
        j2 = next(j for j in joints if j["name"] == link["joint2"])
        ax.plot([j1["x"], j2["x"]], [j1["y"], j2["y"]], 'bo-')
    for joint in joints:
        ax.text(joint["x"], joint["y"], joint["name"], fontsize=12, color='red')
    ax.set_xlabel("X-Koordinate")
    ax.set_ylabel("Y-Koordinate")
    ax.set_title("Mechanismus-Darstellung")
    st.pyplot(fig)

st.title("Mechanismus Simulation und Optimierung")

# Mechanismus selbst erstellen
st.subheader("Erstelle einen neuen Mechanismus")
joint_name = st.text_input("Gelenkname:")
x_coord = st.number_input("X-Koordinate:", value=0.0)
y_coord = st.number_input("Y-Koordinate:", value=0.0)
is_fixed = st.checkbox("Fixiertes Gelenk?")
if st.button("Gelenk hinzufügen"):
    st.session_state.mechanism_data["joints"].append({"name": joint_name, "x": x_coord, "y": y_coord, "fixed": is_fixed})
    st.success(f"Gelenk {joint_name} hinzugefügt!")

if len(st.session_state.mechanism_data["joints"]) > 1:
    st.subheader("Erstelle eine Verbindung zwischen Gelenken")
    joint_options = [j["name"] for j in st.session_state.mechanism_data["joints"]]
    joint1_name = st.selectbox("Erstes Gelenk:", joint_options, key="joint1")
    joint2_name = st.selectbox("Zweites Gelenk:", joint_options, key="joint2")
    length = st.number_input("Länge der Verbindung:", min_value=0.1, value=1.0)
    if st.button("Verbindung hinzufügen"):
        st.session_state.mechanism_data["links"].append({"joint1": joint1_name, "joint2": joint2_name, "length": length})
        st.success(f"Verbindung zwischen {joint1_name} und {joint2_name} hinzugefügt!")

# Mechanismus visualisieren
if st.button("Zeige Mechanismus"):
    plot_mechanism(st.session_state.mechanism_data["joints"], st.session_state.mechanism_data["links"])