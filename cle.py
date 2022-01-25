from anchor import Anchor

class Cle():

    def __init__(self, msg, cfg):
        self.tags = []
        self.anchors = []
        self.cfg = cfg
        self.company = msg["company"]
        self.room = msg["room"]

        for data in msg["anchors"]:
            print(data)
            anchor = Anchor(data, cfg, self)
            self.anchors.append(anchor)

        for anchor in self.anchors:
            anchor.relate_to_master(self.anchors)

