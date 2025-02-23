import numpy as np
import json
from scipy.optimize import minimize
from mechanism import Mechanism, Joint

class MechanismSimulator:
    """Führt die Kinematik-Simulation eines Mechanismus durch."""
    def __init__(self, mechanism):
        self.mechanism = mechanism

    def objective_function(self, variables, fixed_joints, movable_joints, links):
        """Zielfunktion zur Minimierung des Längenfehlers der Glieder."""
        error = 0
        idx = 0
        joint_positions = {joint.name: np.array([variables[idx], variables[idx + 1]]) for joint in movable_joints}
        for joint in fixed_joints:
            joint_positions[joint.name] = np.array([joint.x, joint.y])
            
        for link in links:
            p1, p2 = joint_positions[link.joint1.name], joint_positions[link.joint2.name]
            distance = np.linalg.norm(p2 - p1)
            error += (distance - link.length) ** 2
        return error

    def simulate(self, theta_steps=36):
        """Simuliert die Mechanik für verschiedene Winkelwerte."""
        results = []
        fixed_joints = [joint for joint in self.mechanism.joints if joint.fixed]
        movable_joints = [joint for joint in self.mechanism.joints if not joint.fixed]
        initial_positions = np.array([coord for joint in movable_joints for coord in (joint.x, joint.y)])
        
        for theta in np.linspace(0, 2 * np.pi, theta_steps):
            solution = minimize(self.objective_function, initial_positions, args=(fixed_joints, movable_joints, self.mechanism.links), method='BFGS')
            if solution.success:
                optimized_positions = solution.x.reshape(-1, 2)
                for i, joint in enumerate(movable_joints):
                    joint.x, joint.y = optimized_positions[i]
                results.append({"theta": theta, "positions": [(j.name, j.x, j.y) for j in self.mechanism.joints]})
            else:
                print(f"Optimierung fehlgeschlagen für theta={theta}")
        
        return results

    def save_results(self, results, filename="simulation_results.json"):
        with open(filename, 'w') as f:
            json.dump(results, f, indent=4)

if __name__ == "__main__":
    from mechanism import Mechanism
    
    mech = Mechanism()
    A = mech.add_joint("A", 0, 0, fixed=True)
    B = mech.add_joint("B", 1, 0)
    C = mech.add_joint("C", 2, 1)
    D = mech.add_joint("D", 1, 2, fixed=True)
    
    mech.add_link(A, B)
    mech.add_link(B, C)
    mech.add_link(C, D)
    mech.add_link(D, A)
    
    simulator = MechanismSimulator(mech)
    results = simulator.simulate()
    simulator.save_results(results)
    
    print("Simulation abgeschlossen. Ergebnisse gespeichert in 'simulation_results.json'")