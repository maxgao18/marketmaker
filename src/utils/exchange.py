import json
import zmq


class Exchange:
    def __init__(self, exchange_addr="tcp://localhost:10000"):
        context = zmq.Context()
        self.ex_socket = context.socket(zmq.REQ)
        self.ex_socket.connect(exchange_addr)

    def submit(self, order):
        self.ex_socket.send_string(json.dumps(order))
        while True:
            try:
                message = self.ex_socket.recv(zmq.NOBLOCK)
                break
            except zmq.ZMQError:
                continue
