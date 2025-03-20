import numpy as np
from scipy.optimize import minimize

class Joint:
    def __init__(self, x, y, fixed=False):
        self.x = x
        self.y = y
        self.fixed = fixed

class Link:
    def __init__(self, joint_a, joint_b):
        self.joint_a = joint_a
        self.joint_b = joint_b
        self.length = np.sqrt((joint_a.x - joint_b.x) ** 2 + (joint_a.y - joint_b.y) ** 2)

class Mechanism:
    def __init__(self):
        self.joints = []
        self.links = []

    def add_joint(self, x, y, fixed=False):
        joint = Joint(x, y, fixed)
        self.joints.append(joint)
        return joint

    def add_link(self, joint_a, joint_b):
        link = Link(joint_a, joint_b)
        self.links.append(link)

    def objective_function(self, variables):
        idx = 0
        for joint in self.joints:
            if not joint.fixed:
                joint.x = variables[idx]
                joint.y = variables[idx + 1]
                idx += 2

        error = 0
        for link in self.links:
            dx = link.joint_a.x - link.joint_b.x
            dy = link.joint_a.y - link.joint_b.y
            length = np.sqrt(dx**2 + dy**2)
            error += (length - link.length) ** 2

        return error

    def solve(self):
        variables = []
        for joint in self.joints:
            if not joint.fixed:
                variables.append(joint.x)
                variables.append(joint.y)

        result = minimize(self.objective_function, variables, method='BFGS')

        idx = 0
        for joint in self.joints:
            if not joint.fixed:
                joint.x = result.x[idx]
                joint.y = result.x[idx + 1]
                idx += 2

    def get_joint_positions(self):
        return [(joint.x, joint.y) for joint in self.joints]
