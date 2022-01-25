import numpy as np
import clelib as cl
import time

class Anchor():

    def __init__(self, msg, cfg, cle):

        self.cfg = cfg
        self.number = msg["number"]
        self.x = msg["x"]
        self.y = msg["y"]
        self.z = msg["z"]
        self.Role = msg["Role"]
        self.master_number = msg["master_number"]
        self.ID = msg["ID"]
        self.data2sendflag = 0
        self.T_max = cfg.T_max
        self.c = cfg.c
        self.company = cle.company
        self.room = cle.room

        self.master = []
        self.master_ID = []
        self.Range = []
        self.sync_flag = 0
        self.current_master_seq = -1
        self.current_rx = -1.
        self.current_tx = -1.
        self.X = []
        self.Dx = []
        self.rx_last_cs = -1.
        self.tx_last_cs = -1.
        self.startnumber = 5
        self.tx = []
        self.rx = []
        self.k_skip = 0 # number of skipped rx messages by raim


    def relate_to_master(self, anchors):
        for master in anchors:
            if master.number == self.master_number:
                self.master_ID = master.ID
                self.Range = np.sqrt(pow(master.x - self.x, 2) +
                                     pow(master.y - self.y, 2) +
                                     pow(master.z - self.z, 2)) / self.c
                self.master = master
                self.log_message(f"Anchor {self.number} has been related to {self.master.number}")

        if self.master_ID == [] and self.Role == "Master":
            self.sync_flag = 1
            self.log_message(f"Master anchor {self.number} synchronized")

        if self.master_ID == [] and self.Role != "Master":
            self.log_message(f"Anchor {self.number} has no master")


        self.X = np.array([[0.0], [0.0]])
        self.Dx = np.array([[2.46e-20, 4.21e-20], [4.21e-20, 1.94e-19]])


    def add_tx(self, msg):
        if self.master.sync_flag:
            self.current_tx = self.master.correct_timestamp(msg['timestamp'])
            if self.current_master_seq == msg['seq']:
                self.one_step()
            else:
                self.current_master_seq = msg['seq']


    def add_rx(self, msg):
        self.current_rx = msg['timestamp']
        if self.current_master_seq == msg['seq']:
            self.one_step()
        else:
            self.current_master_seq = msg['seq']


    def one_step(self):
        if self.sync_flag:
            dt = self.current_tx - self.tx_last_cs
            if dt < 0:
                dt = dt + self.T_max
            b, X, Dx, nev = cl.CS_filter(self.X, self.Dx, dt, self.current_tx, self.current_rx, self.Range, self.T_max)
            if b:
                self.k_skip = 0
                self.X = X
                self.Dx = Dx
                self.rx_last_cs = self.current_rx
                self.tx_last_cs = self.current_tx
                # print(f"Anchor {self.number}, {self.X[0]}, {self.X[1]}")
            else:
                self.k_skip = self.k_skip + 1
                if self.k_skip == 5:
                    self.sync_flag = 0
                    self.k_skip = 0
                    self.log_message("Sync lost: " + str(self.number))
                    self.data2sendflag = 1
        else:
            if len(self.tx) == self.startnumber:
                del self.tx[0]
                del self.rx[0]
            self.tx.append(self.current_tx)
            self.rx.append(self.current_rx)
            if len(self.tx) == self.startnumber:
                flag, shift, drift = cl.make_initial(self.tx, self.rx, self.Range, self.T_max)

                if flag:
                    X = np.array([[shift + drift * self.tx[0]], [drift]])
                    Dx = self.Dx
                    for i in range(1, self.startnumber):
                        dt = self.tx[i] - self.tx[i - 1]
                        if dt < 0:
                            dt = dt + self.T_max
                        b, X, Dx, nev = cl.CS_filter(X, Dx, dt, self.tx[i], self.rx[i], self.Range, self.T_max)
                    self.X = X
                    self.Dx = Dx
                    self.rx_last_cs = self.rx[len(self.rx) - 1]
                    self.tx_last_cs = self.tx[len(self.tx) - 1]
                    self.tx = []
                    self.rx = []
                    self.sync_flag = 1
                    self.log_message("Synchronized: " + str(self.number))
                    self.data2sendflag = 1
        self.current_master_seq = -1


    def correct_timestamp(self, t):
        dt = t - self.rx_last_cs
        if dt < 0:
            dt += self.T_max
        return float(t - (self.X[0] + self.X[1] * dt))


    def log_message(self, msg):
        print(msg)













