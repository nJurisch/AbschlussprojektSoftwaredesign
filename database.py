from tinydb import TinyDB, Query

class Database:
    def __init__(self, db_path="mechanism_db.json"):
        self.db = TinyDB(db_path)

    def save_mechanism(self, mechanism):
        data = {
            "joints": [(joint.x, joint.y, joint.fixed) for joint in mechanism.joints],
            "links": [(mechanism.joints.index(link.joint_a), mechanism.joints.index(link.joint_b)) for link in mechanism.links]
        }
        self.db.insert(data)

    def load_mechanism(self, mechanism):
        data = self.db.all()[0]
        joints = [Joint(x, y, fixed) for x, y, fixed in data["joints"]]

        mechanism.joints = joints
        mechanism.links = []
        for link in data["links"]:
            joint_a = joints[link[0]]
            joint_b = joints[link[1]]
            mechanism.add_link(joint_a, joint_b)
