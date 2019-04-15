from .work_process import WorkProcess


class ProducerProcess(WorkProcess):
    def work(self):
        for item in self.items():
            self.pause_flag.wait()
            self.output_queue.put(item, block=False)

    def items(self):
        yield from ()
