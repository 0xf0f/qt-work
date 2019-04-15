from .work_process import WorkProcess
from .work_process import StopWork


class ConsumerProcess(WorkProcess):
    def work(self):
        while True:
            self.pause_flag.wait()
            item = self.input_queue.get(block=True)
            self.pause_flag.wait()
            if item == StopWork:
                return
            self.consume(item)

    def consume(self, item):
        pass

    def output(self, data):
        self.output_queue.put(data, block=False)
