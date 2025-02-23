import json
import numpy as np
import matplotlib.pyplot as plt

class KinematicsAnalyzer:
    """Analysiert die berechneten Kinematikdaten und visualisiert die Bewegung."""
    def __init__(self, simulation_results_file):
        self.simulation_results_file = simulation_results_file
        self.results = self.load_results()
    
    def load_results(self):
        with open(self.simulation_results_file, 'r') as f:
            return json.load(f)
    
    def plot_trajectories(self):
        """Visualisiert die Bahnkurven der Gelenke."""
        plt.figure(figsize=(8, 6))
        joint_trajectories = {}
        
        for entry in self.results:
            for joint in entry["positions"]:
                name, x, y = joint
                if name not in joint_trajectories:
                    joint_trajectories[name] = {"x": [], "y": []}
                joint_trajectories[name]["x"].append(x)
                joint_trajectories[name]["y"].append(y)
        
        for name, trajectory in joint_trajectories.items():
            plt.plot(trajectory["x"], trajectory["y"], label=name)
        
        plt.xlabel("X-Koordinate")
        plt.ylabel("Y-Koordinate")
        plt.title("Bahnkurven der Gelenke")
        plt.legend()
        plt.grid()
        plt.show()
    
    def optimize_link_lengths(self):
        """Findet die optimalen Längen der Glieder für eine verbesserte Kinematik."""
        # Extrahiert alle tatsächlichen Längen aus den Simulationsergebnissen
        link_lengths = []
        for entry in self.results:
            for joint1, joint2 in zip(entry["positions"], entry["positions"][1:]):
                _, x1, y1 = joint1
                _, x2, y2 = joint2
                link_lengths.append(np.linalg.norm([x2 - x1, y2 - y1]))
        
        avg_length = np.mean(link_lengths)
        print(f"Optimierte durchschnittliche Gliederlänge: {avg_length:.4f}")
        return avg_length
    
if __name__ == "__main__":
    analyzer = KinematicsAnalyzer("simulation_results.json")
    analyzer.plot_trajectories()
    optimized_length = analyzer.optimize_link_lengths()
    print(f"Optimierte Gliederlänge: {optimized_length:.4f}")