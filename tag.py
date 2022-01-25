import clelib as cl
import time

class Tag():
    def __init__(self, msg, cle):
        self.company = cle.company
        self.room = cle.room
        self.cfg = cle.cfg
        self.cle = cle
        self.ID = msg["sender"]
        self.SN = -1
        self.measurements = []
        self.x = 0.0
        self.y = 0.0
        self.h = cle.cfg.hei
        self.DOP = 1.
        self.starttime = time.time()
        self.lasttime = time.time()
        self.lifetime = 0.
        self.state = 0
        self.alpha = 0.5
        self.data2sendflag = 0
        self.anchors_number_to_solve = 0
        self.x_buffer = []
        self.y_buffer = []

    def add_data(self, msg):

        if time.time() - self.lasttime > 10:
            self.x_buffer = []
            self.y_buffer = []
            self.measurements = []
            self.SN = -1
            self.lasttime = time.time()

        if msg["sn"] != self.SN:
            delta = msg["sn"] - self.SN
            if delta < -240:
                delta += 255
            if (delta > 0) or self.SN < 0:
                self.SN = msg["sn"]
            else:
                return

            self.measurements = cl.check_PD(self.measurements, self.cfg)

            flag = cl.coords_calc_2D(self)

            if flag:
                self.data2sendflag = 1
                self.lasttime = time.time()
                self.lifetime = self.lasttime - self.starttime
                self.anchors_number_to_solve = len(self.measurements)
            else:
                flag = 0
            self.measurements = []
        self.measurements.append(msg)








