import numpy as np
import json
from scipy.optimize import minimize

class Joint:
    """Repräsentiert ein Gelenk (Punkt) im Mechanismus."""
    def __init__(self, name, x, y, fixed=False):
        self.name = name
        self.x = x
        self.y = y
        self.fixed = fixed  # Ist das Gelenk statisch oder nicht?

    def position(self):
        return np.array([self.x, self.y])

    def __repr__(self):
        return f"Joint({self.name}, x={self.x}, y={self.y}, fixed={self.fixed})"

class Link:
    """Repräsentiert eine starre Verbindung (Glied) zwischen zwei Gelenken."""
    def __init__(self, joint1, joint2):
        self.joint1 = joint1
        self.joint2 = joint2
        self.length = np.linalg.norm(joint2.position() - joint1.position())

    def __repr__(self):
        return f"Link({self.joint1.name}-{self.joint2.name}, length={self.length:.2f})"

class Mechanism:
    """Repräsentiert den gesamten Mechanismus mit Gelenken und Gliedern."""
    def __init__(self):
        self.joints = []
        self.links = []

    def add_joint(self, name, x, y, fixed=False):
        joint = Joint(name, x, y, fixed)
        self.joints.append(joint)
        return joint

    def add_link(self, joint1, joint2):
        link = Link(joint1, joint2)
        self.links.append(link)
        return link
    
    def to_dict(self):
        return {
            "joints": [{"name": j.name, "x": j.x, "y": j.y, "fixed": j.fixed} for j in self.joints],
            "links": [(l.joint1.name, l.joint2.name) for l in self.links]
        }
    
    def save_to_file(self, filename):
        with open(filename, 'w') as f:
            json.dump(self.to_dict(), f, indent=4)

    def __repr__(self):
        return f"Mechanism(Joints: {len(self.joints)}, Links: {len(self.links)})"

# Beispielmechanismus (Viergelenkkette)
if __name__ == "__main__":
    mech = Mechanism()
    A = mech.add_joint("A", 0, 0, fixed=True)
    B = mech.add_joint("B", 1, 0)
    C = mech.add_joint("C", 2, 1)
    D = mech.add_joint("D", 1, 2, fixed=True)
    
    mech.add_link(A, B)
    mech.add_link(B, C)
    mech.add_link(C, D)
    mech.add_link(D, A)
    
    print(mech)
    mech.save_to_file("mechanism.json")