import collections


class MulticlassQueue:

    def __init__(self, n_classes: int = 1):
        self.n_classes = n_classes
        self.q_classes = collections.deque()
        self.q_packets = collections.deque()
        self.n_packets = 0

    def push(self, n: int = 1):
        if n == 0:
            return

        cl = 1  # initialize the packets as being of class 1
        self.append(cl, n)
        self.n_packets += n

    def serve(self, amount: int = 1) -> int:
        exit_packets = 0
        max_class = 1
        inc_class = 1
        cycle_it = 0
        cycle_len = len(self.q_packets)
        while amount > 0 and self.n_packets > 0:

            if cycle_it == cycle_len:
                cycle_it = 0
                cycle_len = len(self.q_packets)
                am_ppk = max(int(amount/self.n_packets), 1)
                inc_class = min(am_ppk, self.n_classes-max_class+1)
                max_class = 1

            pkt_class, pkt_n = self.get_head()
            serving = min(pkt_n, amount)

            pkt_class += inc_class
            if pkt_class <= self.n_classes:
                self.append(pkt_class, serving)  # change class in the same queue
                if pkt_class > max_class:
                    max_class = pkt_class
            elif pkt_class == self.n_classes + 1:
                self.n_packets -= serving
                exit_packets += serving  # departure
            else:
                raise Exception('Error')

            if pkt_n > amount:
                self.update_head(pkt_n - amount)
            else:
                self.popleft()

            amount -= serving * inc_class
            cycle_it += 1

        return exit_packets

    def append(self, pkt_class: int = 1, pkt_n: int = 1):
        self.q_classes.append(pkt_class)
        self.q_packets.append(pkt_n)

    def get_head(self):
        return self.q_classes[0], self.q_packets[0]

    def update_head(self, pkt_n: int):
        self.q_packets[0] = pkt_n

    def popleft(self):
        return self.q_classes.popleft(), self.q_packets.popleft()

    def workload(self):
        if self.n_packets == 0:
            return 0
        return sum([(self.n_classes - self.q_classes[_]) *  self.q_packets[_] for _ in range(len(self.q_packets))])

    def __len__(self):
        return self.n_packets

    def __str__(self):
        return str(self.q_classes)

