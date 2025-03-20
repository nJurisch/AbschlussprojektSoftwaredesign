import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from io import BytesIO
import base64
import csv
from matplotlib.animation import FuncAnimation

from berechnung import Mechanism
from database import save_mechanism, load_mechanism, delete_mechanism, list_mechanisms
from user_db import register, login

# Session-State initialisieren
def initialize_session_state():
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False

    if "username" not in st.session_state:
        st.session_state.username = ""

    if "joints" not in st.session_state:
        st.session_state.joints = []

    if "links" not in st.session_state:
        st.session_state.links = []

    if "crank_speed" not in st.session_state:
        st.session_state.crank_speed = 0.05

    if "running" not in st.session_state:
        st.session_state.running = False


# Mechanismus-Animation mit to_jshtml()
def create_animation():
    mechanism = Mechanism(st.session_state.crank_speed)
    
    joints = [mechanism.add_joint(j["x"], j["y"], j["fixed"]) for j in st.session_state.joints]
    for j1, j2 in st.session_state.links:
        mechanism.add_link(joints[j1], joints[j2])

    ani = mechanism.animate()
    html = ani.to_jshtml()
    return html


# Gelenkgeschwindigkeit berechnen
def calculate_max_speed():
    if st.session_state.joints:
        selected_joint = st.selectbox("Gelenk für maximale Geschwindigkeit", range(len(st.session_state.joints)))
        joint = st.session_state.joints[selected_joint]
        speed = st.session_state.crank_speed * joint["x"]
        st.write(f"Maximale Geschwindigkeit von Gelenk {selected_joint + 1}: {speed:.2f}")


# Export der Gelenkpositionen als CSV
def export_joint_positions():
    if not st.session_state.joints:
        st.warning("Keine Gelenkpositionen vorhanden.")
        return
    
    filename = f"gelenkpositionen_{st.session_state.username}.csv"
    with open(filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Gelenk', 'X-Position', 'Y-Position', 'Fixiert'])

        for i, joint in enumerate(st.session_state.joints):
            x_pos = f"{joint['x']:.3f}"
            y_pos = f"{joint['y']:.3f}"
            fixed = "Ja" if joint['fixed'] else "Nein"
            writer.writerow([f"Gelenk {i + 1}", x_pos, y_pos, fixed])

    # Download-Link für CSV
    with open(filename, "rb") as f:
        data = f.read()
        b64 = base64.b64encode(data).decode()
        href = f'<a href="data:file/csv;base64,{b64}" download="{filename}">CSV-Datei herunterladen</a>'
        st.markdown(href, unsafe_allow_html=True)

    # Ausgabe der CSV-Daten in der Benutzeroberfläche
    st.write("### Gelenkpositionen (CSV-Ausgabe):")
    table = []
    for i, joint in enumerate(st.session_state.joints):
        table.append([
            f"Gelenk {i + 1}",
            f"{joint['x']:.3f}",
            f"{joint['y']:.3f}",
            "Ja" if joint["fixed"] else "Nein"
        ])
    
    st.table(table)


# Mechanismus-Logik (Speichern, Laden, Bearbeiten)
def run_simulation():
    st.title(f"Mechanismus-Simulation für {st.session_state.username}")

    # Abmelde-Button
    if st.button("Abmelden"):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.session_state.joints = []
        st.session_state.links = []
        st.rerun()

    # Mechanismus speichern
    st.write("Mechanismus speichern")
    mechanism_name = st.text_input("Mechanismusname")

    if st.button("Speichern"):
        if mechanism_name.strip():
            data = {
                'joints': st.session_state.joints,
                'links': st.session_state.links,
                'crank_speed': st.session_state.crank_speed
            }
            save_mechanism(st.session_state.username, mechanism_name, data)
            st.success(f"Mechanismus '{mechanism_name}' gespeichert!")

    # Mechanismus laden und löschen
    st.write("Gespeicherte Mechanismen")
    saved_mechanisms = list_mechanisms(st.session_state.username)

    if saved_mechanisms:
        selected_mechanism = st.selectbox("Gespeicherten Mechanismus laden", [""] + saved_mechanisms)

        if selected_mechanism:
            col1, col2 = st.columns(2)

            with col1:
                if st.button("Laden"):
                    data = load_mechanism(st.session_state.username, selected_mechanism)
                    if data:
                        st.session_state.joints = data["joints"]
                        st.session_state.links = data["links"]
                        st.session_state.crank_speed = data.get("crank_speed", 0.05)
                        st.success(f"Mechanismus '{selected_mechanism}' erfolgreich geladen!")
                        st.rerun()

            with col2:
                if st.button("Löschen"):
                    confirm = st.checkbox("Löschen bestätigen")
                    if confirm:
                        delete_mechanism(st.session_state.username, selected_mechanism)
                        st.success(f"Mechanismus '{selected_mechanism}' erfolgreich gelöscht!")
                        st.rerun()

    # Gelenke bearbeiten
    st.write("Gelenke bearbeiten")
    for i, joint in enumerate(st.session_state.joints):
        cols = st.columns(4)
        joint["x"] = cols[0].number_input(f"X-Koordinate Gelenk {i + 1}", value=joint["x"])
        joint["y"] = cols[1].number_input(f"Y-Koordinate Gelenk {i + 1}", value=joint["y"])
        joint["fixed"] = cols[2].checkbox(f"Fixiert {i + 1}", value=joint["fixed"])
        if cols[3].button("Löschen", key=f"delete_joint_{i}"):
            st.session_state.joints.pop(i)
            st.rerun()

    if st.button("Gelenk hinzufügen"):
        st.session_state.joints.append({"x": 0.0, "y": 0.0, "fixed": False})
        st.rerun()

    # Export der Gelenkpositionen als CSV
    if st.button("Gelenkpositionen exportieren (CSV)"):
        export_joint_positions()

    # Steuerung der Geschwindigkeit
    st.write("Steuerung")
    st.session_state.crank_speed = st.number_input(
        "Kurbelgeschwindigkeit", 
        value=st.session_state.crank_speed, 
        step=0.01
    )
    calculate_max_speed()

    # Animation
    st.write("---") 
    st.write("Mechanismus-Animation")

    if st.button("Simulation starten"):
        html = create_animation()
        st.components.v1.html(html, height=800, width=800)


# Login-Formular
def login_form():
    st.title("Anmeldung")

    username = st.text_input("Benutzername")
    password = st.text_input("Passwort", type="password")

    if st.button("Anmelden"):
        if username.strip() and password.strip():
            success = login(username, password)
            if success:
                st.session_state.logged_in = True
                st.session_state.username = username
                st.success(f"Willkommen, {username}!")
                st.rerun()
            else:
                st.error("Falscher Benutzername oder Passwort.")


# Steuerung für Anmeldung und Simulation
def main():
    initialize_session_state()

    if not st.session_state.logged_in:
        login_form()
    else:
        run_simulation()


if __name__ == "__main__":
    main()
