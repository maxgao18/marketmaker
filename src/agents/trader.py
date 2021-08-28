from abc import ABC, abstractmethod


class Trader(ABC):
    class CallBackOptions:
        def __init__(self, always_run=False, on_event=True):
            self.always_run = always_run
            self.on_event = on_event

    def __init__(self, user):
        self.user = user
        self.msg_id = 0

    def callback_options(self):
        return Trader.CallBackOptions()

    @abstractmethod
    def symbols(self):
        pass

    @abstractmethod
    def init(self, state):
        pass

    @abstractmethod
    def run(self, state):
        pass

    def submit_to_exchange(self, state, msg=None, func=None, **kwargs):
        self.msg_id += 1
        if msg is not None:
            msg["user"] = self.user
            msg["id"] = self.msg_id
            state.exchange.submit(msg)
        elif func is not None:
            msg = func(user=self.user, id=self.msg_id, **kwargs)
            state.exchange.submit(msg)
