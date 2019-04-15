from qt_work import qt

import qt_work
import sys

import time
import random

from multiprocessing import Queue


class TestProducer(qt_work.ProducerProcess):
    def items(self):
        while True:
            value = random.random()
            print('produced', value)
            yield self.name, value
            time.sleep(0.05*value)


class TestConsumer(qt_work.ConsumerProcess):
    def consume(self, item):
        producer, item = item
        print('Received item', item, 'from', producer)
        time.sleep(0.01*item)


if __name__ == '__main__':
    app = qt.QApplication(sys.argv)
    manager_window = qt_work.ManagerWindow()
    manager_window.show()

    queue = Queue()

    for i in range(2):
        manager_window.add_process(TestProducer, output_queue=queue)

    for i in range(18):
        manager_window.add_process(TestConsumer, input_queue=queue)

    manager_window.arrange_windows()

    sys.exit(app.exec())
