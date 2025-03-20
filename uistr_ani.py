import streamlit as st
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import numpy as np
from io import BytesIO
import base64
import tempfile
import imageio_ffmpeg
import matplotlib as mpl
import matplotlib.animation as animation

# ✅ ffmpeg automatisch mit imageio-ffmpeg laden
mpl.rcParams['animation.ffmpeg_path'] = imageio_ffmpeg.get_ffmpeg_exe()

from test_idk import Mechanism
from database import save_mechanism, load_mechanism, delete_mechanism, list_mechanisms
from user_db import register, login

# ✅ Session-State-Initialisierung
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


# ✅ Login-Formular
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
                return
            else:
                st.error("Falscher Benutzername oder Passwort.")


# ✅ Registrierungs-Formular
def registration_form():
    st.title("Registrierung")

    new_username = st.text_input("Neuer Benutzername")
    new_password = st.text_input("Neues Passwort", type="password")

    if st.button("Registrieren"):
        if new_username.strip() and new_password.strip():
            success = register(new_username, new_password)
            if success:
                st.success(f"Benutzer '{new_username}' erfolgreich registriert!")
            else:
                st.error("Benutzername bereits vergeben.")


# ✅ Animationserstellung mit ffmpeg
def create_animation():

    mechanism = Mechanism(st.session_state.crank_speed)

    joints = [mechanism.add_joint(j["x"], j["y"], j["fixed"]) for j in st.session_state.joints]
    for j1, j2 in st.session_state.links:
        mechanism.add_link(joints[j1], joints[j2])

    fig, ax = plt.subplots()
    ax.set_xlim(-50, 50)
    ax.set_ylim(-50, 50)

    line, = ax.plot([], [], 'k-', lw=2)
    trace_line, = ax.plot([], [], 'r-', lw=1)

    def init():
        line.set_data([], [])
        trace_line.set_data([], [])
        return line, trace_line

    def update(frame):
        mechanism.update(frame, line, trace_line)
        return line, trace_line

    ani = FuncAnimation(fig, update, frames=360, init_func=init, blit=True)

    # ✅ Temporäre Datei erstellen
    with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as temp_file:
        temp_file_path = temp_file.name

        writer = animation.FFMpegWriter(fps=30)
        ani.save(temp_file_path, writer=writer)

        buffer = BytesIO()
        with open(temp_file_path, "rb") as f:
            buffer.write(f.read())
        buffer.seek(0)

    # ✅ Video in HTML-Format umwandeln
    b64 = base64.b64encode(buffer.read()).decode()
    html = f"""
    <video width="600" height="400" controls autoplay loop>
        <source src="data:video/mp4;base64,{b64}" type="video/mp4">
        Dein Browser unterstützt kein HTML5-Video.
    </video>
    """
    return html

import streamlit.components.v1 as components

# 🌟 Mechanismus-Bearbeitung
def run_simulation():
    st.title(f"Mechanismus-Simulation für {st.session_state.username}")

    # ✅ Abmelden-Button
    if st.sidebar.button("Abmelden"):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.session_state.joints = []
        st.session_state.links = []
        st.session_state.running = False
        st.rerun()

    # ✅ Mechanismus laden & löschen
    st.write("### Gespeicherte Mechanismen")
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

            with col2:
                if st.button("Löschen"):
                    confirm = st.checkbox("Löschen bestätigen")
                    if confirm:
                        delete_mechanism(st.session_state.username, selected_mechanism)
                        st.success(f"Mechanismus '{selected_mechanism}' erfolgreich gelöscht!")
                        st.rerun()
    

    # ✅ Gelenke bearbeiten
    st.write("### Gelenke bearbeiten")
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

    # ✅ Kurbelgeschwindigkeit bearbeiten
    st.write("### Kurbelgeschwindigkeit")
    st.session_state.crank_speed = st.number_input("Kurbelgeschwindigkeit", value=st.session_state.crank_speed, step=0.01)

# 💻 Steuerung für Anmeldung und Simulation
def main():

    initialize_session_state()

    if not st.session_state.logged_in:
        mode = st.radio("Anmelden oder Registrieren", ["Anmelden", "Registrieren"])
        if mode == "Anmelden":
            login_form()
        elif mode == "Registrieren":
            registration_form()
    else:
         mode = st.sidebar.radio("Wähle eine Ansicht", ["Simulation", "Test Animation"])
        
         if mode == "Simulation":
                run_simulation()

         elif mode == "Test Animation":
                if st.button("Starte Animation"):

                  
                    mechanism_animation = Mechanism(st.session_state.crank_speed)
                                                    
                    if not st.session_state.joints or not st.session_state.links:
                        st.error("Keine Mechanismus-Daten im Session State gefunden!")
                        st.stop()

                    # Erstelle Datenstruktur für from_data()
                    data = {
                        "joints": st.session_state.joints,
                        "links": st.session_state.links
                    }

                    # Debugging: Zeige die geladenen Daten
                    st.write("Daten für Mechanismus:", data)

                    # Mechanismus mit den gespeicherten Daten füllen
                    for joint in data["joints"]:
                        mechanism_animation.add_joint(joint["x"], joint["y"], joint["fixed"])

                    for link in data["links"]:
                        # Hole die Joint-Objekte anhand der Indizes der Links und füge sie hinzu
                        joint1 = mechanism_animation.joints[link[0]]
                        joint2 = mechanism_animation.joints[link[1]]
                        mechanism_animation.add_link(joint1, joint2)

                    mechanism_animation.solve_positions()
                    mech_ani = mechanism_animation.animate()

                    # ✅ Animation mit to_jshtml() einbetten
                    components.html(mech_ani.to_jshtml(), height=1000)


if __name__ == "__main__":
    main()
