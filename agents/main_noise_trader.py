import zmq
import json
import random
import time
import signal

ctr = 0
interrupted = False

sleeptime_sec = 1


def signal_handler(signum, frame):
    global interrupted
    interrupted = True


def buy(px=1, qty=1):
    global ctr
    ctr += 1
    return {
        "user": "nt",
        "id": f"{ctr}",
        "type": "LIMIT",
        "symbol": "BABA",
        "side": "BUY",
        "qty": qty,
        "px": px,
    }


def sell(px=0.98, qty=1):
    global ctr
    ctr += 1
    return {
        "user": "nt",
        "id": f"{ctr}",
        "type": "LIMIT",
        "symbol": "BABA",
        "side": "SELL",
        "qty": qty,
        "px": px,
    }


def cancel_all():
    global ctr
    ctr += 1
    return {
        "user": "nt",
        "id": "999",
        "type": "CANCELALL",
        "symbol": "*",
    }


signal.signal(signal.SIGINT, signal_handler)

# send
scontext = zmq.Context()
ssocket = scontext.socket(zmq.REQ)
ssocket.connect("tcp://localhost:10000")

# events
pcontext = zmq.Context()
psocket = pcontext.socket(zmq.SUB)
psocket.connect("tcp://localhost:10001")
psocket.subscribe("")

ssocket.send_string(json.dumps(cancel_all()))
while not interrupted:
    try:
        message = ssocket.recv(zmq.NOBLOCK)
        # print(message)
        break
    except zmq.ZMQError:
        continue

while not interrupted:
    while not interrupted:
        try:
            message = psocket.recv(zmq.NOBLOCK)
            # print(message, flush=True)
        except zmq.ZMQError:
            break
    px = random.randint(50, 100) / 100
    qty = random.randint(1, 10)
    side = random.randint(0, 1)
    if side == 0:
        ssocket.send_string(json.dumps(buy(px, qty)))
    else:
        ssocket.send_string(json.dumps(sell(px, qty)))

    while not interrupted:
        try:
            message = ssocket.recv(zmq.NOBLOCK)
            # print(message)
            break
        except zmq.ZMQError:
            continue
    time.sleep(sleeptime_sec)
