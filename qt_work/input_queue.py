import multiprocessing.queues


class InputQueue(multiprocessing.queues.Queue):
    def __init__(self):
        super().__init__()
        self.cancel_join_thread()
