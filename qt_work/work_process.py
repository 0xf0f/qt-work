import sys
import multiprocessing


class StopWork:
    pass


class WorkProcess(multiprocessing.Process):
    class StdOut:
        def __init__(self, stdout_queue: multiprocessing.Queue):
            self.stdout_queue = stdout_queue

        def write(self, data):
            self.stdout_queue.put(data, block=False)

        def flush(self):
            pass

        def close(self):
            pass

    def __init__(self, input_queue, output_queue, stdout_queue):
        super().__init__()
        self.input_queue: multiprocessing.Queue = input_queue
        self.output_queue: multiprocessing.Queue = output_queue
        self.stdout_queue: multiprocessing.Queue = stdout_queue

        self.pause_flag = multiprocessing.Event()
        self.pause_flag.set()

    def run(self) -> None:
        sys.stdout = WorkProcess.StdOut(self.stdout_queue)
        sys.stderr = sys.stdout

        self.started()
        self.work()
        self.finished()

    def started(self):
        pass

    def work(self):
        pass

    def finished(self):
        pass

    def set_paused(self, paused: bool):
        if paused:
            self.pause_flag.clear()
        else:
            self.pause_flag.set()
