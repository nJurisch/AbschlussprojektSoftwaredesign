import json
import numpy as np
from scipy.optimize import minimize
from mechanism import Mechanism
from simulation import MechanismSimulator

class MechanismOptimizer:
    """Optimiert die Gliederlängen eines Mechanismus basierend auf der Simulation."""
    def __init__(self, mechanism, simulation_results_file):
        self.mechanism = mechanism
        self.simulation_results_file = simulation_results_file
        self.results = self.load_results()
    
    def load_results(self):
        """Lädt die gespeicherten Simulationsergebnisse aus einer JSON-Datei."""
        with open(self.simulation_results_file, 'r') as f:
            return json.load(f)
    
    def objective_function(self, variables):
        """Zielfunktion zur Minimierung des Längenfehlers der Glieder."""
        error = 0
        for entry in self.results:
            for i, (joint1, joint2) in enumerate(zip(entry["positions"], entry["positions"][1:])):
                _, x1, y1 = joint1
                _, x2, y2 = joint2
                distance = np.linalg.norm([x2 - x1, y2 - y1])
                error += (distance - variables[i]) ** 2
        return error
    
    def optimize_lengths(self):
        """Optimiert die Gliederlängen basierend auf der Simulation."""
        initial_lengths = [link.length for link in self.mechanism.links]
        solution = minimize(self.objective_function, initial_lengths, method='BFGS')
        
        if solution.success:
            optimized_lengths = solution.x
            print("Optimierte Gliederlängen:")
            for link, new_length in zip(self.mechanism.links, optimized_lengths):
                print(f"{link.joint1.name}-{link.joint2.name}: {new_length:.4f}")
                link.length = new_length
        else:
            print("Optimierung fehlgeschlagen!")
        
        return solution.success

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
    
    optimizer = MechanismOptimizer(mech, "simulation_results.json")
    optimizer.optimize_lengths()