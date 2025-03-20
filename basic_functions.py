import numpy as np
from scipy.optimize import minimize

class Mechanism:
    def __init__(self, joints, links):
        self.joints = joints  # Liste von Punkten [(x,y)]
        self.links = {tuple(link): np.linalg.norm(np.array(self.joints[link[0]]) - np.array(self.joints[link[1]])) for link in links}  # Dictionary für Verbindungen mit Längen
        self.angle = 0  # Startwinkel
    
    def update_mechanism(self, theta):
        """Aktualisiert den Mechanismus für einen bestimmten Winkel."""
        self.angle = theta
        return self.calculate_positions()
    
    def calculate_positions(self):
        """Berechnet die neuen Positionen der Punkte basierend auf dem gegebenen Winkel."""
        positions = np.array(self.joints)
        rotation_matrix = np.array([[np.cos(self.angle), -np.sin(self.angle)],
                                    [np.sin(self.angle), np.cos(self.angle)]])
        positions[1:, :] = (rotation_matrix @ positions[1:, :].T).T  # Nur bewegliche Punkte rotieren
        return positions
    
    def compute_length_error(self, positions):
        """Berechnet die Fehler der Längen der Glieder."""
        errors = []
        for (i, j), expected_length in self.links.items():
            actual_length = np.linalg.norm(positions[i] - positions[j])
            errors.append((actual_length - expected_length) ** 2)
        return sum(errors)
    
    def optimize_mechanism(self):
        """Optimiert die Kinematik zur Minimierung der Längenfehler."""
        res = minimize(lambda theta: self.compute_length_error(self.update_mechanism(theta)), self.angle)
        return res.x
    
    def add_link(self, joint1, joint2, length=None):
        """Fügt ein neues Glied zwischen zwei bestehenden Gelenken hinzu."""
        if (joint1, joint2) not in self.links and (joint2, joint1) not in self.links:
            if length is None:
                length = np.linalg.norm(np.array(self.joints[joint1]) - np.array(self.joints[joint2]))
            self.links[(joint1, joint2)] = length
        else:
            print("Diese Verbindung existiert bereits.")
    
    def update_link_length(self, joint1, joint2, new_length):
        """Aktualisiert die Länge einer bestehenden Verbindung."""
        if (joint1, joint2) in self.links:
            self.links[(joint1, joint2)] = new_length
        elif (joint2, joint1) in self.links:
            self.links[(joint2, joint1)] = new_length
        else:
            print("Diese Verbindung existiert nicht.")   
