import qt
import sys
import multiprocessing
import multiprocessing.queues
import random
import threading




import time
class TestProcess(WorkProcess):
    def started(self):
        print('Hi!')

    def work_on(self, data):
        print(data)
        time.sleep(1)


# class TerminableQueue(multiprocessing.queues.Queue):
#     def __init__(self):
#         super().__init__()
#         self.running = True


if __name__ == '__main__':
    def main():
        app = qt.QApplication(sys.argv)
        main_window = MainWindow()
        main_window.show()

        class InputThread(threading.Thread):
            def __init__(self):
                super().__init__()
                self.setDaemon(True)

            def run(self):
                for i in range(1_000_000):
                    main_window.input_queue.put(i, block=False)

        InputThread().start()
        result = app.exec()

        # input_queue = main_window.input_queue
        main_window.input_queue.cancel_join_thread()
        # main_window.input_queue.close()

        return result


    sys.exit(main())
