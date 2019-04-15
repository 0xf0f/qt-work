import multiprocessing
import qt
import threading
import sys
import time


class WorkThread(threading.Thread):
    def __init__(self, process_name, input_queue, output_queue):
        super().__init__()
        self.process_name = process_name
        self.input_queue: multiprocessing.Queue = input_queue
        self.output_queue: multiprocessing.Queue = output_queue

    def run(self):
        while True:
            number, item = self.input_queue.get(block=True)

            print('item', number, 'received.')
            print('Sleeping', item, 'seconds.')
            time.sleep(item)

            print('item', number, 'complete.')
            # self.input_queue.task_done()
            self.output_queue.put((self.process_name, f'Completed {number}'))


class WorkerProcess(multiprocessing.Process):
    def __init__(self, process_count, input_queue, output_queue):
        super().__init__()
        self.process_count = process_count
        self.output_queue: multiprocessing.Queue = output_queue
        self.input_queue: multiprocessing.Queue = input_queue

    def run(self) -> None:
        app = qt.QApplication([])

        class TestWindow(qt.QWidget):
            def __init__(self):
                super().__init__()

                self.hboxlayout = qt.QHBoxLayout(self)
                self.output = qt.QPlainTextEdit()
                # self.output.setCenterOnScroll(True)
                self.hboxlayout.addWidget(self.output)

            def write(self, data):
                scroll = False
                if self.output.verticalScrollBar().value() == self.output.verticalScrollBar().maximum():
                    scroll = True

                self.output.insertPlainText(data)

                if scroll:
                    self.output.verticalScrollBar().setValue(self.output.verticalScrollBar().maximum())

        test_window = TestWindow()
        test_window.setWindowTitle(self.name)

        class StdOut(qt.QObject):
            write_signal = qt.pyqtSignal(str)

            def write(self, data):
                self.write_signal.emit(data)

            def flush(self):
                pass

            def close(self):
                pass

        stdout = StdOut()
        stdout.write_signal.connect(test_window.write)
        sys.stdout = stdout

        test_window.show()
        test_window_width = test_window.frameGeometry().width()
        test_window_height = test_window.frameGeometry().height()

        screen_rect: qt.QRect = test_window.windowHandle().screen().availableGeometry()
        columns = screen_rect.width() // test_window_width
        # rows = screen_rect.height() // test_window_height

        row, column = divmod(self.process_count, columns)

        test_window.move(column*test_window_width, row*test_window_height)

        print('Hi!')
        print('This is process', self.name)
        self.output_queue.put((self.name, 'Lol!'), block=False)

        work_thread = WorkThread(self.name, self.input_queue, self.output_queue)
        work_thread.start()

        app.exec()


if __name__ == '__main__':
    def main():
        # app = qt.QApplication([])

        input_queue = multiprocessing.Queue()
        output_queue = multiprocessing.Queue()

        class OutputThread(threading.Thread):
            def __init__(self):
                super().__init__()
                self.setDaemon(True)

            def run(self) -> None:
                while True:
                    item = output_queue.get(block=True)
                    print(item)

        class InputThread(threading.Thread):
            def __init__(self):
                super().__init__()
                self.setDaemon(True)

            def run(self):
                import random
                for j in range(1_000_000):
                    input_queue.put((j, random.random()))

        InputThread().start()
        OutputThread().start()

        processes = []
        for i in range(10):
            worker_process = WorkerProcess(i, input_queue, output_queue)
            worker_process.start()
            processes.append(worker_process)

        for process in processes:
            process.join()

        # app.exec()

    main()
